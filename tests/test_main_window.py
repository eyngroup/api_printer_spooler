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


class _FakeResponse:
    """Respuesta HTTP simulada con cuerpo JSON fijo."""

    def __init__(self, payload: dict) -> None:
        self.payload = payload

    def json(self) -> dict:
        """Devuelve el JSON simulado."""
        return self.payload


@pytest.fixture
def posts(monkeypatch):
    """Sustituye requests.post y registra (url, kwargs) de cada llamada."""
    import requests

    calls: list[tuple] = []

    def fake_post(url, **kwargs):
        calls.append((url, kwargs))
        return _FakeResponse({"status": True})

    monkeypatch.setattr(requests, "post", fake_post)
    return calls


CFG = {"server": {"server_host": "192.168.1.5", "server_port": 5051}}


@pytest.mark.parametrize("report_type,endpoint", [("X", "report_x"), ("Z", "report_z")])
def test_request_report(posts, report_type, endpoint):
    """El reporte usa la URL local, sin cuerpo y con el timeout de 90 s."""
    assert main_window.request_report(CFG, report_type) == {"status": True}
    url, kwargs = posts[0]
    assert url == main_window.local_api_url(CFG, f"/api/{endpoint}")
    assert kwargs == {"timeout": 90}


def test_request_commands(posts):
    """Los comandos se envían como JSON con timeout de 15 s."""
    main_window.request_commands(CFG, ["S1", "I0X"])
    url, kwargs = posts[0]
    assert url == main_window.local_api_url(CFG, "/api/fiscal/command")
    assert kwargs == {"json": {"commands": ["S1", "I0X"]}, "timeout": 15}


def test_request_clock_sync(posts):
    """El ajuste de reloj fuerza la sincronización con timeout de 30 s."""
    main_window.request_clock_sync(CFG)
    url, kwargs = posts[0]
    assert url == main_window.local_api_url(CFG, "/api/fiscal/clock")
    assert kwargs == {"json": {"force": True}, "timeout": 30}


def test_build_payment_commands_order_and_skips_empty():
    """Genera PE<código><nombre> en orden de código y omite los vacíos."""
    labels = {"01": "Efectivo", "02": "", "03": "Zelle", "24": "DivisaCashea"}
    assert main_window.build_payment_commands(labels) == ["PE01Efectivo", "PE03Zelle", "PE24DivisaCashea"]


def test_build_payment_commands_all_codes():
    """Con los 24 códigos con nombre se obtienen 24 comandos."""
    from server.config_loader import PAYMENT_CODES

    commands = main_window.build_payment_commands({code: f"N{code}" for code in PAYMENT_CODES})
    assert len(commands) == 24 and commands[0] == "PE01N01" and commands[-1] == "PE24N24"


def test_build_payment_commands_normalizes_accents():
    """Los acentos no llegan a la máquina."""
    assert main_window.build_payment_commands({"05": "Débito"}) == ["PE05Debito"]


def test_build_payment_commands_too_long_lists_codes():
    """Nombres de más de 14 caracteres lanzan ValueError con los códigos."""
    with pytest.raises(ValueError, match="03, 07"):
        main_window.build_payment_commands({"03": "A" * 15, "05": "ok", "07": "B" * 20})


def test_default_payment_labels_fit_machine_limit():
    """Todas las etiquetas por defecto caben en 14 caracteres."""
    from server.config_loader import _load_default_payment_labels

    labels = _load_default_payment_labels()
    assert main_window.payment_labels_too_long(labels) == []
    assert all(len(v) <= main_window.PAYMENT_LABEL_MAX_CHARS for v in labels.values())


@pytest.mark.parametrize(
    ("screen", "wanted", "expected"),
    [
        ((1920, 1080), (980, 720), "980x720+470+135"),  # cabe entera: centrada en el área útil
        ((1366, 768), (980, 720), "980x678+193+0"),  # pantalla baja: el alto se limita a 768 - 90
        ((800, 600), (980, 720), "780x510+10+0"),  # pantalla pequeña: ancho y alto limitados
    ],
)
def test_window_geometry_fits_the_screen(screen, wanted, expected):
    """La ventana se centra y nunca sobrepasa el área útil (pantalla menos barra de tareas)."""
    assert main_window.window_geometry(*screen, *wanted) == expected
