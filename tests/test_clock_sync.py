"""
Tests for the printer clock sync: PrinterManager.sync_clock, the automatic sync after a Z and the manual endpoint.
No hardware: a fake controller records the commands sent.
"""
# ruff: noqa: DTZ001 - la hora local de la máquina fiscal es ingenua (sin zona horaria)

from datetime import datetime
from typing import Any
from unittest.mock import MagicMock

import pytest

from server.config_loader import ConfigManager
from server.handlers import document_handler, job_store
from server.handlers.printer_manager import PrinterManager
from server.server_api import create_app

NOW = datetime(2026, 10, 9, 14, 30, 5)
CONFIG = {"fiscal_port": "COM1", "fiscal_baudrate": 9600, "fiscal_timeout": 2}


class _FakeController:
    """Fake HKA controller: serves S1 readings and records every command sent."""

    reject: set[str] = set()  # noqa: RUF012 - restablecido en la fixture
    s1_readings: list[dict[str, str]] = []  # noqa: RUF012
    sent: list[str] = []  # noqa: RUF012
    closed = False

    def __init__(self, *args, **kwargs):
        self.serial_printer = MagicMock(is_open=True)

    def open_port(self):
        return True

    def close_port(self):
        _FakeController.closed = True

    def get_s1(self):
        readings = _FakeController.s1_readings
        return readings.pop(0) if len(readings) > 1 else readings[0]

    def send_cmd(self, command):
        _FakeController.sent.append(command)
        return command[:2] not in _FakeController.reject


def _s1(dt: datetime) -> dict[str, str]:
    """S1 with the machine date/time of dt."""
    return {"fecha_impresora": dt.strftime("%d%m%y"), "hora_impresora": dt.strftime("%H%M%S")}


@pytest.fixture(autouse=True)
def fake_controller(monkeypatch):
    """Isolate the registry, freeze the server clock and replace the HKA controller."""
    import controllers.pfhka

    monkeypatch.setattr(PrinterManager, "_instances", {})
    monkeypatch.setattr(PrinterManager, "_now", staticmethod(lambda: NOW))
    monkeypatch.setattr(controllers.pfhka, "FiscalPrinterHka", _FakeController)
    _FakeController.reject = set()
    _FakeController.sent = []
    _FakeController.closed = False
    _FakeController.s1_readings = [_s1(NOW)]


def test_in_sync_sends_nothing():
    _FakeController.s1_readings = [_s1(datetime(2026, 10, 9, 14, 31, 5))]  # +60 s
    result = PrinterManager.sync_clock("tfhka", CONFIG)
    assert result == {"status": "in_sync", "drift_seconds": 60}
    assert _FakeController.sent == []
    assert _FakeController.closed


def test_adjusted_sends_pf_and_pg_and_rereads():
    _FakeController.s1_readings = [_s1(datetime(2026, 10, 9, 15, 25, 5)), _s1(NOW)]  # +3300 s, luego en hora
    result = PrinterManager.sync_clock("tfhka", CONFIG)
    assert _FakeController.sent == ["PF143005", "PG091026"]
    assert result == {"status": "adjusted", "drift_before": 3300, "drift_after": 0}


def test_force_adjusts_even_when_in_sync():
    PrinterManager.sync_clock("tfhka", CONFIG, force=True)
    assert _FakeController.sent == ["PF143005", "PG091026"]


def test_rejected_when_machine_refuses():
    _FakeController.s1_readings = [_s1(datetime(2026, 10, 9, 15, 25, 5))]
    _FakeController.reject = {"PF"}
    result = PrinterManager.sync_clock("tfhka", CONFIG)
    assert result["status"] == "rejected"
    assert result["drift_seconds"] == 3300
    assert result["message"] == PrinterManager.CLOCK_REJECTED_MESSAGE
    assert _FakeController.sent == ["PF143005"]  # no se envía PG si PF fue rechazado


def test_unsupported_for_pnp():
    assert PrinterManager.sync_clock("pnp", CONFIG) == {"status": "unsupported"}


def test_error_when_port_cannot_open(monkeypatch):
    monkeypatch.setattr(_FakeController, "open_port", lambda self: False)
    assert PrinterManager.sync_clock("tfhka", CONFIG)["status"] == "error"


def test_error_never_raises(monkeypatch):
    def _boom(self):
        raise RuntimeError("fallo serial")

    monkeypatch.setattr(_FakeController, "get_s1", _boom)
    result = PrinterManager.sync_clock("tfhka", CONFIG)
    assert result == {"status": "error", "message": "fallo serial"}
    assert _FakeController.closed


def test_live_instance_controller_is_used_and_left_open():
    live = MagicMock()
    live._printer = _FakeController()
    PrinterManager._instances["tfhka"] = live
    _FakeController.s1_readings = [_s1(datetime(2026, 10, 9, 15, 25, 5)), _s1(NOW)]
    assert PrinterManager.sync_clock("tfhka", CONFIG)["status"] == "adjusted"
    assert not _FakeController.closed


# --- Integración con la API -------------------------------------------------------------------------------------


@pytest.fixture
def app_client(tmp_path, monkeypatch):
    """Flask test client with an isolated job store."""
    monkeypatch.setattr(job_store, "_DB_PATH", tmp_path / "clock_jobs.db")
    job_store.init_db()
    config = dict(ConfigManager.get_config())
    config["server"]["server_mode"] = "SPOOLER"
    app = create_app(config)
    app.config["TESTING"] = True
    app.config["printers"] = {"fiscal": {"fiscal_enabled": True, "fiscal_name": "tfhka"}}
    with app.test_client() as client:
        yield client


@pytest.fixture
def sync_calls(monkeypatch) -> list[dict[str, Any]]:
    """Replace sync_clock with a recorder returning an adjusted result."""
    calls: list[dict[str, Any]] = []

    def _fake(cls, printer_type, printer_config, threshold_seconds=120, force=False):
        calls.append({"type": printer_type, "force": force})
        return {"status": "adjusted", "drift_before": 3300, "drift_after": 0}

    monkeypatch.setattr(PrinterManager, "sync_clock", classmethod(_fake))
    monkeypatch.setattr(document_handler.time, "sleep", lambda s: None)
    return calls


def _printer(report_z: bool = True, command_ok: bool = True) -> MagicMock:
    printer = MagicMock()
    printer.check_status.return_value = True
    printer.report_z.return_value = report_z
    printer.send_command.return_value = command_ok
    return printer


def test_report_z_success_syncs_clock(app_client, monkeypatch, sync_calls):
    monkeypatch.setattr(document_handler, "printer_instance", lambda cfg: (_printer(), None))
    body = app_client.post("/api/report_z").get_json()
    assert body["status"] is True
    assert body["data"]["clock_sync"]["status"] == "adjusted"
    assert sync_calls == [{"type": "tfhka", "force": False}]


def test_report_z_failure_does_not_sync(app_client, monkeypatch, sync_calls):
    monkeypatch.setattr(document_handler, "printer_instance", lambda cfg: (_printer(report_z=False), None))
    body = app_client.post("/api/report_z").get_json()
    assert body["status"] is False
    assert sync_calls == []


def test_report_x_does_not_sync(app_client, monkeypatch, sync_calls):
    monkeypatch.setattr(document_handler, "printer_instance", lambda cfg: (_printer(), None))
    body = app_client.post("/api/report_x").get_json()
    assert body["status"] is True
    assert "data" not in body
    assert sync_calls == []


def test_sync_error_does_not_fail_the_z(app_client, monkeypatch, sync_calls):
    def _boom(cls, *a, **k):
        raise RuntimeError("fallo")

    monkeypatch.setattr(PrinterManager, "sync_clock", classmethod(_boom))
    monkeypatch.setattr(document_handler, "printer_instance", lambda cfg: (_printer(), None))
    body = app_client.post("/api/report_z").get_json()
    assert body["status"] is True
    assert body["data"]["clock_sync"]["status"] == "error"


def test_raw_z_command_syncs_clock(app_client, monkeypatch, sync_calls):
    monkeypatch.setattr(document_handler, "printer_instance", lambda cfg: (_printer(), None))
    body = app_client.post("/api/command", json={"commands": ["I0Z"]}).get_json()
    assert body["status"] is True
    assert body["data"] == [{"command": "I0Z", "success": True}]  # el contrato de data no cambia
    assert body["clock_sync"]["status"] == "adjusted"
    assert len(sync_calls) == 1


def test_non_z_command_does_not_sync(app_client, monkeypatch, sync_calls):
    monkeypatch.setattr(document_handler, "printer_instance", lambda cfg: (_printer(), None))
    body = app_client.post("/api/command", json={"commands": ["I0X", "S1"]}).get_json()
    assert body["status"] is True
    assert "clock_sync" not in body
    assert sync_calls == []


def test_rejected_z_command_does_not_sync(app_client, monkeypatch, sync_calls):
    monkeypatch.setattr(document_handler, "printer_instance", lambda cfg: (_printer(command_ok=False), None))
    body = app_client.post("/api/command", json={"commands": ["I0Z"]}).get_json()
    assert body["status"] is False
    assert sync_calls == []


def test_clock_endpoint_returns_result_and_forwards_force(app_client, sync_calls):
    resp = app_client.post("/api/fiscal/clock", json={"force": True})
    body = resp.get_json()
    assert resp.status_code == 200
    assert body["status"] is True
    assert body["data"] == {"status": "adjusted", "drift_before": 3300, "drift_after": 0}
    assert sync_calls == [{"type": "tfhka", "force": True}]


def test_clock_endpoint_rejected_reports_estado_and_error(app_client, monkeypatch):
    rejected = {"status": "rejected", "drift_seconds": 3300, "message": PrinterManager.CLOCK_REJECTED_MESSAGE}
    monkeypatch.setattr(PrinterManager, "sync_clock", classmethod(lambda cls, *a, **k: rejected))
    resp = app_client.post("/api/fiscal/clock")
    body = resp.get_json()
    assert body["status"] is False
    assert body["message"] == PrinterManager.CLOCK_REJECTED_MESSAGE
    assert body["data"]["Estado"] and body["data"]["Error"]
    assert body["data"]["drift_seconds"] == 3300
