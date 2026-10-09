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
