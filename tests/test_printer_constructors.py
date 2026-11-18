"""
Los constructores de los drivers fiscales deben crear el controlador y conectar. Se usan controladores falsos que no
abren el puerto, así que el constructor debe terminar en ConnectionError (prueba que llegó hasta connect()).
"""

import pytest

import printers.printer_hka as hka
import printers.printer_pnp as pnp


class FakeController:
    """Controlador serial falso: registra los parámetros y nunca abre el puerto."""

    created: list[tuple] = []

    def __init__(self, port, baudrate, timeout):
        FakeController.created.append((port, baudrate, timeout))

    def open_port(self):
        return False

    def close_port(self):
        return None


CONFIG = {"fiscal_enabled": True, "fiscal_name": "x", "fiscal_port": "COM9", "fiscal_baudrate": 9600, "fiscal_timeout": 2}


@pytest.mark.parametrize(
    ("module", "controller_name", "printer_class"),
    [(hka, "FiscalPrinterHka", "TfhkaPrinter"), (pnp, "FiscalPrinterPnp", "PnpPrinter")],
)
def test_constructor_creates_controller_and_tries_to_connect(monkeypatch, module, controller_name, printer_class):
    """Regresión: el cuerpo de _initialize_printer era código muerto y el constructor no conectaba."""
    FakeController.created.clear()
    monkeypatch.setattr(module, controller_name, FakeController)
    with pytest.raises(ConnectionError):
        getattr(module, printer_class)(CONFIG)
    assert FakeController.created == [("COM9", 9600, 2)]


def test_hka_model_key_is_a_method_outside_init():
    """_model_key debe existir como método (hoy quedó dentro de __init__ por error y rompió la conexión)."""
    instance = hka.TfhkaPrinter.__new__(hka.TfhkaPrinter)
    instance._model = "HKA-80"
    assert instance._model_key() == "HKA_80"
