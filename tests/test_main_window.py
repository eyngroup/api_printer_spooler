"""Tests del ciclo de vida de la ventana principal (sin abrir ventanas reales)."""

import ttkbootstrap as tb

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
