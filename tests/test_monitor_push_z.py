"""
Pruebas de las lecturas del monitor antes y después de cada Z (before_z / after_z) y de FiscalMonitor.read_fresh.
Sin hardware ni red: la impresora es un doble y la lectura de la máquina se reemplaza.
"""

from typing import Any
from unittest.mock import MagicMock

import pytest

from server.config_loader import ConfigManager
from server.handlers import document_handler, fiscal_monitor, job_store, monitor_push
from server.handlers.fiscal_monitor import FiscalMonitor
from server.handlers.printer_manager import PrinterManager
from server.server_api import create_app

PRINTERS = {"fiscal": {"fiscal_enabled": True, "fiscal_name": "tfhka"}}
PUSH_ON = {"enabled": True, "url": "https://odoo.example/api", "token": "t0k3n", "branch_code": "S1"}
GOOD = {"available": True, "machine": {"serial": "Z1A0000001"}}


@pytest.fixture
def calls(monkeypatch) -> list[str]:
    """Registro ordenado de los eventos: read_fresh, enqueue, report_z, command, clock_sync, invalidate, thread."""
    events: list[str] = []
    monkeypatch.setattr(
        PrinterManager,
        "sync_clock",
        classmethod(lambda cls, *a, **k: events.append("clock_sync") or {"status": "in_sync", "drift_seconds": 0}),
    )
    monkeypatch.setattr(document_handler.time, "sleep", lambda s: None)
    monkeypatch.setattr(FiscalMonitor, "invalidate", classmethod(lambda cls: events.append("invalidate")))

    def _enqueue(trigger, config, snapshot=None, now=None):
        events.append(f"enqueue:{trigger}:{(snapshot or {}).get('available')}")
        return "rid"

    monkeypatch.setattr(monitor_push, "enqueue_reading", _enqueue)
    return events


@pytest.fixture
def reads(monkeypatch, calls) -> dict[str, Any]:
    """Reemplaza read_fresh: devuelve `result` (o lanza si es una excepción) y lo registra."""
    state: dict[str, Any] = {"result": GOOD}

    def _fake(cls, printers_config):
        calls.append("read_fresh")
        if isinstance(state["result"], Exception):
            raise state["result"]
        return dict(state["result"])

    monkeypatch.setattr(FiscalMonitor, "read_fresh", classmethod(_fake))
    return state


@pytest.fixture
def threads(monkeypatch) -> list:
    """Hace el hilo posterior al Z determinista: lo ejecuta en línea al iniciarse."""
    started: list = []

    class _Inline:
        def __init__(self, target, args=(), **kwargs):
            self._target, self._args = target, args
            started.append(self)

        def start(self):
            self._target(*self._args)

    monkeypatch.setattr(monitor_push.threading, "Thread", _Inline)
    return started


def _client(tmp_path, monkeypatch, push: dict | None, mode: str = "SPOOLER"):
    monkeypatch.setattr(job_store, "_DB_PATH", tmp_path / "z_jobs.db")
    job_store.init_db()
    config = dict(ConfigManager.get_config())
    config["server"] = {**config.get("server", {}), "server_mode": mode}
    app = create_app(config)
    app.config["TESTING"] = True
    app.config["printers"] = PRINTERS
    if push is None:
        app.config.pop("monitor_push", None)
    else:
        app.config["monitor_push"] = push
    return app.test_client()


@pytest.fixture
def client_on(tmp_path, monkeypatch):
    return _client(tmp_path, monkeypatch, PUSH_ON)


@pytest.fixture
def client_off(tmp_path, monkeypatch):
    return _client(tmp_path, monkeypatch, None)


def _printer(calls: list[str], report_z: bool = True, command_ok: bool = True) -> MagicMock:
    printer = MagicMock()
    printer.check_status.return_value = True
    printer.report_z.side_effect = lambda: calls.append("report_z") or report_z
    printer.report_x.side_effect = lambda: calls.append("report_x") or True
    printer.send_command.side_effect = lambda cmd: calls.append(f"command:{cmd}") or command_ok
    return printer


def _use(monkeypatch, printer):
    monkeypatch.setattr(document_handler, "printer_instance", lambda cfg: (printer, None))


def test_report_z_reads_before_and_after(client_on, monkeypatch, calls, reads, threads):
    _use(monkeypatch, _printer(calls))
    response = client_on.post("/api/report_z")
    assert response.status_code == 200
    assert response.get_json() == {
        "status": True,
        "message": "Reporte Z impreso correctamente",
        "data": {"clock_sync": {"status": "in_sync", "drift_seconds": 0}},
    }
    assert calls == [
        "read_fresh",
        "enqueue:before_z:True",
        "report_z",
        "clock_sync",
        "invalidate",
        "read_fresh",
        "enqueue:after_z:True",
    ]
    assert threads[0]._args[0] == "after_z"


def test_command_z_reads_before_and_after_once(client_on, monkeypatch, calls, reads, threads):
    _use(monkeypatch, _printer(calls))
    response = client_on.post("/api/command", json={"commands": ["I0Z", "I1Z"]})
    assert response.status_code == 200
    assert calls == [
        "read_fresh",
        "enqueue:before_z:True",
        "command:I0Z",
        "command:I1Z",
        "clock_sync",
        "invalidate",
        "read_fresh",
        "enqueue:after_z:True",
    ]


def test_command_without_z_makes_no_reads(client_on, monkeypatch, calls, reads, threads):
    _use(monkeypatch, _printer(calls))
    assert client_on.post("/api/command", json={"commands": ["PF143005"]}).status_code == 200
    assert calls == ["command:PF143005"]


def test_x_report_makes_no_reads(client_on, monkeypatch, calls, reads, threads):
    _use(monkeypatch, _printer(calls))
    assert client_on.post("/api/report_x").status_code == 200
    assert calls == ["report_x"]


def test_push_disabled_no_reads_but_cache_invalidated(client_off, monkeypatch, calls, reads, threads):
    _use(monkeypatch, _printer(calls))
    assert client_off.post("/api/report_z").get_json()["status"] is True
    assert calls == ["report_z", "clock_sync", "invalidate"]
    calls.clear()
    assert client_off.post("/api/command", json={"commands": ["I0Z"]}).status_code == 200
    assert calls == ["command:I0Z", "clock_sync", "invalidate"]
    assert not threads


def test_push_incomplete_config_counts_as_disabled(tmp_path, monkeypatch, calls, reads, threads):
    client = _client(tmp_path, monkeypatch, {"enabled": True, "url": "", "token": "x"})
    _use(monkeypatch, _printer(calls))
    assert client.post("/api/report_z").status_code == 200
    assert "read_fresh" not in calls


def test_proxy_mode_makes_no_reads(tmp_path, monkeypatch, calls, reads, threads):
    client = _client(tmp_path, monkeypatch, PUSH_ON, mode="PROXY")
    _use(monkeypatch, _printer(calls))
    assert client.post("/api/report_z").status_code == 200
    assert "read_fresh" not in calls


def test_read_failure_never_blocks_z(client_on, monkeypatch, calls, reads, threads):
    reads["result"] = RuntimeError("puerto ocupado")
    _use(monkeypatch, _printer(calls))
    response = client_on.post("/api/report_z")
    assert response.status_code == 200
    assert response.get_json()["status"] is True
    assert "report_z" in calls
    assert not any(c.startswith("enqueue") for c in calls)


def test_unavailable_snapshot_is_skipped_but_z_runs(client_on, monkeypatch, calls, reads, threads):
    reads["result"] = {"available": False, "reason": "Impresión en curso"}
    _use(monkeypatch, _printer(calls))
    assert client_on.post("/api/report_z").get_json()["status"] is True
    assert "report_z" in calls
    assert not any(c.startswith("enqueue") for c in calls)


def test_enqueue_failure_never_blocks_z(client_on, monkeypatch, calls, reads, threads):
    def _boom(*a, **k):
        raise RuntimeError("disco lleno")

    monkeypatch.setattr(monitor_push, "enqueue_reading", _boom)
    _use(monkeypatch, _printer(calls))
    assert client_on.post("/api/report_z").status_code == 200
    assert "report_z" in calls


def test_z_failure_has_no_after_z(client_on, monkeypatch, calls, reads, threads):
    _use(monkeypatch, _printer(calls, report_z=False))
    assert client_on.post("/api/report_z").get_json()["status"] is False
    assert calls == ["read_fresh", "enqueue:before_z:True", "report_z"]
    assert not threads


def test_rejected_z_command_has_no_after_z(client_on, monkeypatch, calls, reads, threads):
    _use(monkeypatch, _printer(calls, command_ok=False))
    assert client_on.post("/api/command", json={"commands": ["I0Z"]}).get_json()["status"] is False
    assert calls == ["read_fresh", "enqueue:before_z:True", "command:I0Z"]


def test_after_z_does_not_block_the_response(client_on, monkeypatch, calls, reads):
    """Sin el hilo en línea: la respuesta sale aunque el hilo posterior aún no haya hecho su lectura."""
    started: list = []
    monkeypatch.setattr(monitor_push.threading, "Thread", lambda **kw: started.append(kw) or MagicMock())
    _use(monkeypatch, _printer(calls))
    assert client_on.post("/api/report_z").status_code == 200
    assert calls.count("read_fresh") == 1  # solo la previa; la posterior corre en el hilo
    assert started[0]["daemon"] is True


# --- FiscalMonitor.read_fresh / invalidate ---------------------------------------------------------------------


@pytest.fixture
def machine(monkeypatch):
    """Máquina simulada: cuenta lecturas y permite simular impresión en curso."""
    FiscalMonitor.reset()
    state = {"reads": 0, "busy": False, "raw": {"s1": {}}}
    monkeypatch.setattr(job_store, "has_processing_jobs", lambda: state["busy"])
    monkeypatch.setattr(fiscal_monitor.job_store, "has_processing_jobs", lambda: state["busy"])

    def _read(cls, name, cfg, busy):
        state["reads"] += 1
        return state["raw"]

    monkeypatch.setattr(PrinterManager, "read_monitor_data", classmethod(_read))
    monkeypatch.setattr(
        fiscal_monitor,
        "build_snapshot",
        lambda raw, payment_labels=None: {"available": True, "payments": [{"code": "01"}], "n": state["reads"]},
    )
    yield state
    FiscalMonitor.reset()


def test_read_fresh_ignores_cache_and_minimum(machine):
    assert FiscalMonitor.get_snapshot(PRINTERS)["n"] == 1
    assert FiscalMonitor.get_snapshot(PRINTERS, force=True)["n"] == 1  # el mínimo de 10 s lo frena
    assert FiscalMonitor.read_fresh(PRINTERS)["n"] == 2
    assert FiscalMonitor.read_fresh(PRINTERS)["n"] == 3
    assert FiscalMonitor.get_snapshot(PRINTERS)["n"] == 3  # la caché se actualizó


def test_read_fresh_applies_payment_labels(machine, monkeypatch):
    monkeypatch.setattr(fiscal_monitor, "get_payment_labels", lambda cfg: {"01": "Efectivo"})
    assert FiscalMonitor.read_fresh(PRINTERS)["payments"][0]["label"] == "Efectivo"


def test_read_fresh_refuses_while_printing_and_never_serves_stale(machine):
    FiscalMonitor.get_snapshot(PRINTERS)
    machine["busy"] = True
    result = FiscalMonitor.read_fresh(PRINTERS)
    assert result == {"available": False, "reason": "Impresión en curso"}
    assert machine["reads"] == 1


def test_read_fresh_failure_is_unavailable_not_stale(machine):
    FiscalMonitor.get_snapshot(PRINTERS)
    machine["raw"] = None
    result = FiscalMonitor.read_fresh(PRINTERS)
    assert result["available"] is False


def test_read_fresh_only_tfhka():
    result = FiscalMonitor.read_fresh({"fiscal": {"fiscal_enabled": True, "fiscal_name": "pnp"}})
    assert result["available"] is False


def test_read_fresh_never_raises(machine, monkeypatch):
    def _boom(cls, *a):
        raise RuntimeError("serial")

    monkeypatch.setattr(PrinterManager, "read_monitor_data", classmethod(_boom))
    assert FiscalMonitor.read_fresh(PRINTERS)["available"] is False


def test_invalidate_clears_cache_without_reading(machine):
    FiscalMonitor.get_snapshot(PRINTERS)
    FiscalMonitor.invalidate()
    assert machine["reads"] == 1
    assert FiscalMonitor.get_snapshot(PRINTERS)["n"] == 2
