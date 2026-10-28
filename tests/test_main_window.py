"""Tests del ciclo de vida de la ventana principal (sin abrir ventanas reales)."""

import pytest
import ttkbootstrap as tb

from views import main_window
from views.main_window import MainWindow


class FakeRoot:
    """Ventana simulada: registra el manejador WM_DELETE_WINDOW y cuenta las destrucciones."""

    def __init__(self) -> None:
        self.handlers: dict = {}
        self.destroyed = 0

    def protocol(self, name, handler) -> None:
        """Guarda el manejador del protocolo de la ventana."""
        self.handlers[name] = handler

    def destroy(self) -> None:
        """Cuenta las veces que se destruye la ventana."""
        self.destroyed += 1


def test_close_button_hides_to_tray_without_destroying():
    """La X de la ventana oculta a la bandeja: el manejador real de ttkbootstrap no debe destruir la ventana."""
    window = MainWindow.__new__(MainWindow)
    hidden = []
    window.hide = lambda: hidden.append(True)

    root = FakeRoot()
    tb.Window.on_close(root, window._on_close)  # mismo registro que hace tb.Window(on_close=...)
    root.handlers["WM_DELETE_WINDOW"]()

    assert hidden == [True]
    assert root.destroyed == 0


@pytest.mark.parametrize(
    ("server", "expected"),
    [
        ({"server_host": "192.168.1.151", "server_port": 5051}, "http://192.168.1.151:5051/api/report_x"),
        ({"server_host": "localhost", "server_port": 5051}, "http://localhost:5051/api/report_x"),
        ({"server_host": "0.0.0.0", "server_port": 5051}, "http://127.0.0.1:5051/api/report_x"),
        ({"server_host": "", "server_port": 5052}, "http://127.0.0.1:5052/api/report_x"),
        ({"server_host": "::", "server_port": 5051}, "http://[::1]:5051/api/report_x"),
        ({"server_host": "fe80::1", "server_port": 5051}, "http://[fe80::1]:5051/api/report_x"),
        ({}, "http://127.0.0.1:5051/api/report_x"),
    ],
)
def test_local_api_url_uses_the_host_the_server_listens_on(server: dict, expected: str):
    """La ventana llama a la misma dirección donde escucha Flask (server_host), no siempre a 127.0.0.1."""
    assert main_window.local_api_url({"server": server}, "/api/report_x") == expected
