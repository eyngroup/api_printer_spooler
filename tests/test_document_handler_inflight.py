"""
Pruebas del contador de operaciones fiscales en curso (reportes X/Z, comandos directos, ajuste de reloj) que usa
el botón "Actualizar" para no cerrar la aplicación a mitad de una de ellas. Sin hardware ni red.
"""

import pytest

from server.config_loader import ConfigManager
from server.handlers import document_handler, job_store
from server.server_api import create_app


@pytest.fixture
def app_client(tmp_path, monkeypatch):
    """Cliente Flask con el job store aislado y la impresora fiscal habilitada."""
    monkeypatch.setattr(job_store, "_DB_PATH", tmp_path / "inflight_jobs.db")
    job_store.init_db()
    config = dict(ConfigManager.get_config())
    config["server"] = {**config.get("server", {}), "server_mode": "SPOOLER"}
    app = create_app(config)
    app.config["TESTING"] = True
    app.config["printers"] = {"fiscal": {"fiscal_enabled": True, "fiscal_name": "tfhka"}}
    with app.test_client() as client:
        yield client


def test_context_counts_and_releases_even_on_error(monkeypatch):
    monkeypatch.setattr(document_handler, "has_processing_jobs", lambda: False)
    assert document_handler.fiscal_operation_in_progress() is False
    with document_handler._fiscal_operation():
        assert document_handler.fiscal_operation_in_progress() is True
    assert document_handler.fiscal_operation_in_progress() is False
    with pytest.raises(RuntimeError), document_handler._fiscal_operation():
        raise RuntimeError("falla")
    assert document_handler.fiscal_operation_in_progress() is False


def test_job_store_jobs_also_count(monkeypatch):
    monkeypatch.setattr(document_handler, "has_processing_jobs", lambda: True)
    assert document_handler.fiscal_operation_in_progress() is True


@pytest.mark.parametrize(
    ("path", "method", "body"),
    [
        ("/api/report_x", "post", None),
        ("/api/report_z", "post", None),
        ("/api/command", "post", {"commands": ["PF143005"]}),
        ("/api/fiscal/clock", "post", {"force": True}),
    ],
)
def test_handlers_hold_the_counter_while_running(app_client, monkeypatch, path, method, body):
    """Dentro del handler el contador vale 1 (visible desde el printer) y 0 al terminar, también tras excepción."""
    from unittest.mock import MagicMock

    from server.handlers.printer_manager import PrinterManager

    monkeypatch.setattr(document_handler, "has_processing_jobs", lambda: False)
    seen = []

    def spy(*args, **kwargs):
        seen.append(document_handler._fiscal_ops_in_flight)
        return True

    printer = MagicMock()
    printer.check_status.return_value = True
    printer.report_x.side_effect = spy
    printer.report_z.side_effect = spy
    printer.send_command.side_effect = spy
    monkeypatch.setattr(document_handler, "printer_instance", lambda cfg: (printer, None))
    monkeypatch.setattr(document_handler.monitor_push, "enqueue_before_z", lambda c: None)
    monkeypatch.setattr(document_handler.monitor_push, "start_after_z", lambda c: None)
    monkeypatch.setattr(document_handler, "_sync_clock_after_z", lambda *a, **k: None)

    def clock(cls, *args, **kwargs):
        seen.append(document_handler._fiscal_ops_in_flight)
        raise RuntimeError("falla")

    monkeypatch.setattr(PrinterManager, "sync_clock", classmethod(clock))
    getattr(app_client, method)(path, json=body)
    assert seen == [1]
    assert document_handler._fiscal_ops_in_flight == 0
    assert document_handler.fiscal_operation_in_progress() is False


def test_window_update_guard_uses_fiscal_operation_in_progress(monkeypatch):
    """El botón "Actualizar" se niega mientras haya una operación fiscal (no solo trabajos del job store)."""
    from views import main_window
    from views.main_window import MainWindow

    window = MainWindow.__new__(MainWindow)
    window._update_info = type("Info", (), {"available": True, "latest": "9.9.9"})()
    warnings = []
    monkeypatch.setattr(main_window, "is_supported", lambda: True)
    monkeypatch.setattr(main_window, "fiscal_operation_in_progress", lambda: True)
    monkeypatch.setattr(main_window.Messagebox, "show_warning", lambda msg, title: warnings.append(msg))
    monkeypatch.setattr(main_window.Messagebox, "yesno", lambda *a, **k: pytest.fail("no debe preguntar"))
    window._on_update_apply()
    assert warnings and "operación fiscal en curso" in warnings[0]


def test_window_report_timeout_matches_odoo_document_timeout():
    from views import main_window

    assert main_window.REPORT_TIMEOUT_SECONDS == 90
