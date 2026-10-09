"""
Tests for PrinterManager: status enrichment on creation failures and one-shot status reads (no hardware).
"""

from typing import Any, ClassVar

import pytest

from server.handlers.printer_manager import PrinterManager


@pytest.fixture(autouse=True)
def clean_instances(monkeypatch):
    """Isolate the singleton registry between tests."""
    monkeypatch.setattr(PrinterManager, "_instances", {})


class _FakeController:
    """Fake HKA controller that records open/close calls."""

    opened = True
    status: ClassVar[dict[str, Any]] = {
        "status_code": 96,
        "error_code": 67,
        "status": "En espera",
        "error": "Error mecánico",
    }
    instances: ClassVar[list] = []

    def __init__(self, port, baudrate, timeout):
        self.args = (port, baudrate, timeout)
        self.closed = False
        _FakeController.instances.append(self)

    def open_port(self):
        return _FakeController.opened

    def get_status(self):
        return self.status

    def close_port(self):
        self.closed = True


def test_read_status_returns_status_and_closes_port(monkeypatch):
    """The one-shot controller reads the status with config defaults and always closes the port."""
    _FakeController.opened = True
    _FakeController.instances = []
    monkeypatch.setattr("controllers.pfhka.FiscalPrinterHka", _FakeController)

    status = PrinterManager.read_status("tfhka", {"fiscal_port": "COM9"})

    assert status == {"status_code": 96, "error_code": 67, "status": "En espera", "error": "Error mecánico"}
    assert _FakeController.instances[0].args == ("COM9", 9600, 2)
    assert _FakeController.instances[0].closed is True


def test_read_status_returns_none_when_port_cannot_open(monkeypatch):
    """An open failure yields None and never raises."""
    _FakeController.opened = False
    _FakeController.instances = []
    monkeypatch.setattr("controllers.pfhka.FiscalPrinterHka", _FakeController)

    assert PrinterManager.read_status("tfhka", {"fiscal_port": "COM9"}) is None
    assert _FakeController.instances[0].closed is True


def test_read_status_skips_when_instance_exists(monkeypatch):
    """With a live instance the serial port is never touched."""
    PrinterManager._instances["tfhka"] = object()
    monkeypatch.setattr("controllers.pfhka.FiscalPrinterHka", _FakeController)
    _FakeController.instances = []

    assert PrinterManager.read_status("tfhka", {"fiscal_port": "COM9"}) is None
    assert _FakeController.instances == []


def test_read_status_pnp_maps_detailed_status(monkeypatch):
    """PNP: status -> status, status_detallado -> error."""

    class _FakePnp(_FakeController):
        status: ClassVar[dict[str, Any]] = {
            "status_code": "0080",
            "error_code": "0600",
            "status": "0001",
            "status_detallado": "Sin papel",
        }

    _FakePnp.open_port = lambda self: True
    monkeypatch.setattr("controllers.pfpnp.FiscalPrinterPnp", _FakePnp)

    status = PrinterManager.read_status("pnp", {"fiscal_port": "COM3"})
    assert status["status"] == "0001"
    assert status["error"] == "Sin papel"


def test_get_printer_failure_is_enriched_with_estado(monkeypatch):
    """A constructor failure without status gets ' - Estado: X, Error: Y' appended."""

    class _Failing:
        def __init__(self, config):
            raise ConnectionError("Error al conectar con la impresora: TFHKA")

    monkeypatch.setattr("printers.printer_hka.TfhkaPrinter", _Failing)
    monkeypatch.setattr(
        PrinterManager,
        "read_status",
        classmethod(lambda cls, t, c: {"status": "En espera", "error": "Error mecánico"}),
    )

    with pytest.raises(ValueError) as exc:
        PrinterManager.get_printer("tfhka", {})
    assert "Estado: En espera, Error: Error mecánico" in str(exc.value)
    assert "Error al conectar con la impresora" in str(exc.value)


def test_get_printer_failure_without_status_keeps_original_message(monkeypatch):
    """If the status cannot be read, the original message is preserved."""

    class _Failing:
        def __init__(self, config):
            raise ConnectionError("Error al conectar con la impresora: TFHKA")

    monkeypatch.setattr("printers.printer_hka.TfhkaPrinter", _Failing)
    monkeypatch.setattr(PrinterManager, "read_status", classmethod(lambda cls, t, c: None))

    with pytest.raises(ValueError) as exc:
        PrinterManager.get_printer("tfhka", {})
    assert str(exc.value) == "Error al conectar con la impresora: TFHKA"


# --- C8: lectura del serial para /api/ping -------------------------------------------------------

HKA_CONFIG = {"fiscal_port": "/dev/ttyACM1", "fiscal_baudrate": 9600, "fiscal_timeout": 2}


class _SerialController:
    """Fake controller exposing the read-only serial queries (HKA S5 / PNP get_version)."""

    calls: ClassVar[list] = []

    def __init__(self, port, baudrate, timeout):
        self.sent: list[str] = []

    def open_port(self):
        return True

    def close_port(self):
        _SerialController.calls.append("close")

    def get_s5(self):
        _SerialController.calls.append("S5")
        return {"rif": "J-000000000", "serial": "Z7C7034708"}

    def get_version(self):
        _SerialController.calls.append("version")
        return {"modelo": "PF-220", "serial": "EOO1234567"}

    def send_cmd(self, command):  # pragma: no cover - must never be called
        raise AssertionError(f"read_serial must not send commands: {command}")


@pytest.fixture
def serial_controllers(monkeypatch):
    """Replace both fiscal controllers with the read-only fake."""
    import controllers.pfhka
    import controllers.pfpnp

    _SerialController.calls = []
    monkeypatch.setattr(controllers.pfhka, "FiscalPrinterHka", _SerialController)
    monkeypatch.setattr(controllers.pfpnp, "FiscalPrinterPnp", _SerialController)


def test_read_serial_prefers_live_instance(serial_controllers, monkeypatch):
    """With a connected instance the cached serial is returned without touching the port."""

    class _Live:
        _serial = "Z7C7034708"

    monkeypatch.setattr(PrinterManager, "_instances", {"tfhka": _Live()})
    assert PrinterManager.read_serial("TFHKA", HKA_CONFIG) == "Z7C7034708"
    assert _SerialController.calls == []


@pytest.mark.parametrize(
    ("printer_type", "expected", "query"), [("tfhka", "Z7C7034708", "S5"), ("pnp", "EOO1234567", "version")]
)
def test_read_serial_one_shot_read_only(serial_controllers, printer_type, expected, query):
    """Without an instance the serial is read once (read-only query), the port is closed and no instance is created."""
    assert PrinterManager.read_serial(printer_type, HKA_CONFIG) == expected
    assert _SerialController.calls == [query, "close"]
    assert PrinterManager._instances == {}


def test_read_serial_returns_none_when_unreachable(monkeypatch):
    """If the port cannot be opened the caller falls back to the configured serial."""
    import controllers.pfhka

    class _Down(_SerialController):
        def open_port(self):
            return False

    monkeypatch.setattr(controllers.pfhka, "FiscalPrinterHka", _Down)
    assert PrinterManager.read_serial("tfhka", HKA_CONFIG) is None


class _FakeS1Controller(_FakeController):
    """Controlador HKA falso con S1 para leer el último número fiscal."""

    s1: ClassVar[dict[str, str] | None] = {"ultima_factura": " 00000998 ", "ultima_nota_credito": "00000144"}
    sent: ClassVar[list] = []

    def __init__(self, port, baudrate, timeout):
        self.args = (port, baudrate, timeout)
        self.closed = False
        _FakeS1Controller.instances.append(self)

    def open_port(self):
        return _FakeS1Controller.opened

    def get_s1(self):
        _FakeS1Controller.sent.append("S1")
        return self.s1


def _patch_s1_controller(monkeypatch):
    _FakeS1Controller.opened = True
    _FakeS1Controller.instances = []
    _FakeS1Controller.sent = []
    monkeypatch.setattr("controllers.pfhka.FiscalPrinterHka", _FakeS1Controller)


def test_read_last_document_number_uses_live_instance(monkeypatch):
    """With a healthy instance its own reader is used and no temporary controller is created."""
    _patch_s1_controller(monkeypatch)

    class _Live:
        def read_last_document_number(self, operation_type):
            return "00000999"

    PrinterManager._instances["tfhka"] = _Live()
    assert PrinterManager.read_last_document_number("tfhka", {}, "invoice") == "00000999"
    assert _FakeS1Controller.instances == []
    assert "tfhka" in PrinterManager._instances


def test_read_last_document_number_broken_instance_uses_temporary_controller(monkeypatch):
    """A broken instance is removed and a one-shot controller reads S1 and always closes the port."""
    _patch_s1_controller(monkeypatch)
    disconnected = []

    class _Broken:
        def read_last_document_number(self, operation_type):
            return None

        def disconnect(self):
            disconnected.append(True)

    PrinterManager._instances["tfhka"] = _Broken()

    assert PrinterManager.read_last_document_number("tfhka", {"fiscal_port": "COM9"}, "invoice") == "00000998"
    assert "tfhka" not in PrinterManager._instances
    assert disconnected == [True]
    assert _FakeS1Controller.instances[0].args == ("COM9", 9600, 2)
    assert _FakeS1Controller.instances[0].closed is True
    assert _FakeS1Controller.sent == ["S1"]


def test_read_last_document_number_without_instance_and_per_operation(monkeypatch):
    """Without an instance the temporary controller maps the operation type."""
    _patch_s1_controller(monkeypatch)
    assert PrinterManager.read_last_document_number("tfhka", {}, "credit") == "00000144"
    assert PrinterManager.read_last_document_number("tfhka", {}, "debit") is None  # campo ausente en S1
    assert PrinterManager.read_last_document_number("tfhka", {}, "otro") is None


def test_read_last_document_number_returns_none_when_unreadable(monkeypatch):
    """Port that cannot open, S1 failure or exceptions yield None and the port is closed."""
    _patch_s1_controller(monkeypatch)
    _FakeS1Controller.opened = False
    assert PrinterManager.read_last_document_number("tfhka", {}, "invoice") is None
    assert _FakeS1Controller.instances[0].closed is True

    _FakeS1Controller.opened = True
    monkeypatch.setattr(_FakeS1Controller, "s1", None)
    assert PrinterManager.read_last_document_number("tfhka", {}, "invoice") is None


def test_read_last_document_number_pnp_returns_none(monkeypatch):
    """PNP: the number is not reliably readable, so no controller is touched."""
    _patch_s1_controller(monkeypatch)
    assert PrinterManager.read_last_document_number("pnp", {}, "invoice") is None
    assert _FakeS1Controller.instances == []


# S1 real de la HKA80 tras la factura 999 (RIF y registro anonimizados), en la forma que devuelve get_s1
S1_PARSED = {
    "ultima_factura": "00000999",
    "contador_cierres_z": "0147",
    "registro_maquina": "Z7C0000000",
    "fecha_impresora": "091026",
}


def test_read_fiscal_summary_from_temporary_controller(monkeypatch):
    """Sin instancia: fecha AAAA-MM-DD, próximo Z (contador + 1) y serial desde una lectura S1 única."""
    import controllers.pfhka

    class _S1Controller(_SerialController):
        def get_s1(self):
            return S1_PARSED

    monkeypatch.setattr(controllers.pfhka, "FiscalPrinterHka", _S1Controller)
    summary = PrinterManager.read_fiscal_summary("tfhka", HKA_CONFIG)
    assert summary == {"document_date": "2026-10-09", "machine_report": "0148", "machine_serial": "Z7C0000000"}
    assert PrinterManager._instances == {}


def test_read_fiscal_summary_none_for_pnp_or_failure(monkeypatch):
    """PNP no se lee; un fallo de S1 devuelve None sin lanzar excepciones."""
    import controllers.pfhka

    class _NoS1(_SerialController):
        def get_s1(self):
            return None

    monkeypatch.setattr(controllers.pfhka, "FiscalPrinterHka", _NoS1)
    assert PrinterManager.read_fiscal_summary("pnp", HKA_CONFIG) is None
    assert PrinterManager.read_fiscal_summary("tfhka", HKA_CONFIG) is None
