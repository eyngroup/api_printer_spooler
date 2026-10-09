"""
Integration tests for the Flask REST API endpoints without requiring physical hardware.
"""

from unittest.mock import MagicMock

import pytest

from server.config_loader import ConfigManager
from server.handlers import job_store
from server.server_api import create_app


@pytest.fixture
def app_client(tmp_path, monkeypatch):
    """Create Flask test client with an isolated job store and test config."""
    db_file = tmp_path / "test_api_jobs.db"
    monkeypatch.setattr(job_store, "_DB_PATH", db_file)
    job_store.init_db()

    config = ConfigManager.get_config()
    test_config = dict(config)
    test_config["server"]["server_mode"] = "SPOOLER"

    app = create_app(test_config)
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


@pytest.fixture
def sample_invoice_payload():
    return {
        "operation_type": "invoice",
        "affected_document": {
            "affected_number": "00000001",
            "affected_date": "2026-10-04",
            "affected_serial": "Z1B1234567",
        },
        "customer": {
            "customer_name": "CLIENTE PRUEBA C.A.",
            "customer_vat": "J-99999999-9",
            "customer_address": "Calle 1, Local 2",
            "customer_phone": "+58 412-0000000",
            "customer_email": "cliente@test.com",
        },
        "document": {
            "document_number": "TEST-0099",
            "document_reference": "REF-001",
            "document_date": "2026-10-04",
            "document_time": "12:00:00",
            "document_name": "FACTURA DE VENTA",
            "document_cashier": "Cajero 1",
        },
        "items": [
            {
                "item_ref": "SKU-01",
                "item_name": "Item Demo",
                "item_quantity": 1.0,
                "item_price": 50.0,
                "item_tax": 16,
                "item_comment": "Nota de item",
            }
        ],
        "payments": [
            {
                "payment_method": "01",
                "payment_name": "Efectivo",
                "payment_amount": 58.0,
            }
        ],
        "delivery": {
            "delivery_comments": [],
            "delivery_barcode": "123456789012",
        },
        "operation_metadata": {
            "terminal_id": "T01",
            "branch_code": "01",
            "operator_id": "OP01",
            "currency_code": "VES",
            "exchange_rate": 1.0,
            "inverse_rate": 1.0,
        },
    }


def test_ping_endpoint(app_client):
    """GET /api/ping returns 200 with serial."""
    resp = app_client.get("/api/ping")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "success"
    assert "message" in data


def test_block_svg_endpoint(app_client):
    """GET /block returns the memorial SVG."""
    resp = app_client.get("/block")
    assert resp.status_code == 200
    assert "svg" in resp.content_type


def test_fiscal_commands_empty_list_rejected(app_client):
    """POST /api/fiscal/command rejects empty or invalid command lists."""
    resp = app_client.post("/api/fiscal/command", json={"commands": []})
    assert resp.status_code == 400
    data = resp.get_json()
    assert data["status"] is False


def test_document_invalid_payload_rejected(app_client):
    """POST /api/document with malformed payload returns 400."""
    resp = app_client.post("/api/document", json={"invalid": "payload"})
    assert resp.status_code == 400
    data = resp.get_json()
    assert data["status"] is False


def test_document_mock_print_and_idempotency(app_client, sample_invoice_payload, monkeypatch):
    """POST /api/document successfully prints via mocked printer and handles idempotency."""
    from server.handlers import document_handler

    mock_printer = MagicMock()
    mock_printer.print_document.return_value = {
        "status": True,
        "message": "Impresión completada",
        "data": {"nro_fiscal": "00054321"},
    }

    # Mock printer_instance so no physical hardware is needed
    monkeypatch.setattr(document_handler, "printer_instance", lambda cfg: (mock_printer, None))

    # 1. First print request
    resp1 = app_client.post("/api/document", json=sample_invoice_payload)
    assert resp1.status_code == 200
    data1 = resp1.get_json()
    assert data1["status"] is True
    assert data1["message"] == "Impresión completada"
    assert mock_printer.print_document.call_count == 1

    # 2. Second duplicate print request for the exact same document
    resp2 = app_client.post("/api/document", json=sample_invoice_payload)
    assert resp2.status_code == 200
    data2 = resp2.get_json()
    assert data2["status"] is True
    assert data2["data"]["nro_fiscal"] == "00054321"

    # Crucial: printer was NOT called a second time (idempotent deduplication!)
    assert mock_printer.print_document.call_count == 1


def _job_status(document_id: str, operation_type: str = "invoice") -> str | None:
    """Read the stored status of a job directly from the job store."""
    with job_store._connect() as conn:
        row = conn.execute(
            "SELECT status FROM print_jobs WHERE document_id=? AND operation_type=?", (document_id, operation_type)
        ).fetchone()
    return row["status"] if row else None


def _ok_printer() -> MagicMock:
    """Mock printer that prints successfully."""
    printer = MagicMock()
    printer.print_document.return_value = {
        "status": True,
        "message": "Impresión completada",
        "data": {"document_number": "00000123", "machine_serial": "ZB1234567"},
    }
    return printer


def test_exception_getting_printer_releases_job(app_client, sample_invoice_payload, monkeypatch):
    """An exception before printing marks the job failed so the retry can print."""
    from server.handlers import document_handler

    def _boom(cfg):
        raise OSError("puerto serial no disponible")

    monkeypatch.setattr(document_handler, "printer_instance", _boom)
    resp = app_client.post("/api/printers", json=sample_invoice_payload)
    assert resp.status_code == 500
    assert resp.get_json()["status"] is False
    assert _job_status("TEST-0099") == "failed"

    printer = _ok_printer()
    monkeypatch.setattr(document_handler, "printer_instance", lambda cfg: (printer, None))
    resp_retry = app_client.post("/api/printers", json=sample_invoice_payload)
    assert resp_retry.status_code == 200
    assert printer.print_document.call_count == 1
    assert _job_status("TEST-0099") == "completed"


def test_exception_during_print_releases_job(app_client, sample_invoice_payload, monkeypatch):
    """An exception raised by print_document marks the job failed (no permanent 409)."""
    from server.handlers import document_handler

    printer = MagicMock()
    printer.print_document.side_effect = OSError("cable desconectado")
    monkeypatch.setattr(document_handler, "printer_instance", lambda cfg: (printer, None))

    resp = app_client.post("/api/printers", json=sample_invoice_payload)
    assert resp.status_code == 500
    assert _job_status("TEST-0099") == "failed"


def test_printed_but_not_recorded_never_reprints(app_client, sample_invoice_payload, monkeypatch):
    """If the job cannot be recorded after printing, Odoo still gets success and retries get 409."""
    from server.handlers import document_handler

    printer = _ok_printer()
    monkeypatch.setattr(document_handler, "printer_instance", lambda cfg: (printer, None))

    def _db_down(*args, **kwargs):
        raise job_store.sqlite3.OperationalError("database is locked")

    monkeypatch.setattr(document_handler, "complete_job", _db_down)

    resp = app_client.post("/api/printers", json=sample_invoice_payload)
    assert resp.status_code == 200
    assert resp.get_json()["data"]["document_number"] == "00000123"
    assert _job_status("TEST-0099") == "processing"

    resp_retry = app_client.post("/api/printers", json=sample_invoice_payload)
    assert resp_retry.status_code == 409
    assert printer.print_document.call_count == 1


def test_complete_job_retried_once(app_client, sample_invoice_payload, monkeypatch):
    """A transient failure recording the job is retried and the duplicate is served from cache."""
    from server.handlers import document_handler

    printer = _ok_printer()
    monkeypatch.setattr(document_handler, "printer_instance", lambda cfg: (printer, None))
    calls = {"n": 0}
    real_complete = job_store.complete_job

    def _flaky_complete(*args, **kwargs):
        calls["n"] += 1
        if calls["n"] == 1:
            raise job_store.sqlite3.OperationalError("database is locked")
        return real_complete(*args, **kwargs)

    monkeypatch.setattr(document_handler, "complete_job", _flaky_complete)

    resp = app_client.post("/api/printers", json=sample_invoice_payload)
    assert resp.status_code == 200
    assert _job_status("TEST-0099") == "completed"

    resp_dup = app_client.post("/api/printers", json=sample_invoice_payload)
    assert resp_dup.status_code == 200
    assert resp_dup.get_json() == resp.get_json()
    assert printer.print_document.call_count == 1


def _command_printer(results: dict[str, bool]) -> MagicMock:
    """Mock fiscal printer whose send_command answers per command."""
    printer = MagicMock()
    printer.check_status.return_value = True
    printer.send_command.side_effect = lambda cmd: results[cmd]
    return printer


def test_command_success_reports_status_true(app_client, monkeypatch):
    """A command accepted by the printer returns status true (contract: one command per call)."""
    from server.handlers import document_handler

    printer = _command_printer({"RU00000000000000": True})
    monkeypatch.setattr(document_handler, "printer_instance", lambda cfg: (printer, None))
    resp = app_client.post("/api/command", json={"commands": ["RU00000000000000"]})
    body = resp.get_json()
    assert resp.status_code == 200
    assert body["status"] is True
    assert body["data"] == [{"command": "RU00000000000000", "success": True}]


def test_command_rejected_reports_status_false(app_client, monkeypatch):
    """A command rejected by the printer must not be reported as success to Odoo."""
    from server.handlers import document_handler

    printer = _command_printer({"RF00010030001003": False})
    monkeypatch.setattr(document_handler, "printer_instance", lambda cfg: (printer, None))
    resp = app_client.post("/api/command", json={"commands": ["RF00010030001003"]})
    body = resp.get_json()
    assert body["status"] is False
    assert "RF00010030001003" in body["message"]
    assert body["data"]["results"] == [{"command": "RF00010030001003", "success": False}]
    assert body["data"]["Estado"] == "Comando rechazado"


def test_command_partial_failure_reports_status_false(app_client, monkeypatch):
    """With several commands, any rejection makes the whole request fail and lists each result."""
    from server.handlers import document_handler

    printer = _command_printer({"A": True, "B": False})
    monkeypatch.setattr(document_handler, "printer_instance", lambda cfg: (printer, None))
    body = app_client.post("/api/command", json={"commands": ["A", "B"]}).get_json()
    assert body["status"] is False
    assert body["data"]["results"] == [{"command": "A", "success": True}, {"command": "B", "success": False}]


def test_schema_error_reports_estado_and_error(app_client):
    """A schema validation failure carries Estado/Error so Odoo never reads a null data."""
    body = app_client.post("/api/printers", json={"invalid": "payload"}).get_json()
    assert body["status"] is False
    assert body["data"]["Estado"] == "Documento rechazado"
    assert body["data"]["Error"]


def test_business_error_reports_estado_and_error(app_client, sample_invoice_payload):
    """A business rule failure carries Estado 'Documento rechazado' and the specific message."""
    sample_invoice_payload["payments"][0]["payment_amount"] = 1.0  # no cubre el total
    resp = app_client.post("/api/printers", json=sample_invoice_payload)
    body = resp.get_json()
    assert resp.status_code == 400
    assert body["status"] is False
    assert body["data"]["Estado"] == "Documento rechazado"
    assert body["data"]["Error"]


def test_printer_unavailable_cover_open_reports_real_status(app_client, sample_invoice_payload, monkeypatch):
    """Creation fails (cover open): the status read by PrinterManager.read_status reaches Odoo."""
    from server.handlers import document_handler
    from server.handlers.printer_manager import PrinterManager

    class _FailingPrinter:
        def __init__(self, config):
            raise ConnectionError("Error al conectar con la impresora: TFHKA")

    monkeypatch.setattr("printers.printer_hka.TfhkaPrinter", _FailingPrinter)
    monkeypatch.setattr(PrinterManager, "_instances", {})
    monkeypatch.setattr(
        PrinterManager,
        "read_status",
        classmethod(
            lambda cls, printer_type, cfg: {
                "status_code": 96,
                "error_code": 67,
                "status": "En modo fiscal y en espera",
                "error": "Fin en la entrega de papel y error mecánico",
            }
        ),
    )
    monkeypatch.setattr(
        document_handler,
        "find_value",
        lambda cfg, key: {"fiscal_enabled": True, "fiscal_name": "tfhka"}.get(key),
    )

    resp = app_client.post("/api/printers", json=sample_invoice_payload)
    body = resp.get_json()
    assert body["status"] is False
    assert body["data"]["Estado"] == "En modo fiscal y en espera"
    assert body["data"]["Error"] == "Fin en la entrega de papel y error mecánico"
    assert _job_status("TEST-0099") == "failed"


def test_print_failure_fills_status_from_printer(app_client, sample_invoice_payload, monkeypatch):
    """print_document fails with data None: Estado/Error come from the printer status (USB cut)."""
    from server.handlers import document_handler

    printer = MagicMock()
    printer.print_document.return_value = {"status": False, "message": "No se pudo imprimir", "data": None}
    printer.get_printer_status.return_value = {
        "status_code": 0,
        "error_code": 128,
        "status": "Error",
        "error": "CTS en falso",
    }
    printer.format_status_message.return_value = ("Error", "CTS en falso")
    monkeypatch.setattr(document_handler, "printer_instance", lambda cfg: (printer, None))

    body = app_client.post("/api/printers", json=sample_invoice_payload).get_json()
    assert body["status"] is False
    assert body["data"]["Estado"] == "Error"
    assert body["data"]["Error"] == "CTS en falso"
    assert _job_status("TEST-0099") == "failed"


def test_print_exception_without_status_still_has_estado_and_error(app_client, sample_invoice_payload, monkeypatch):
    """If the status cannot be read either, the response still carries Estado/Error."""
    from server.handlers import document_handler

    printer = MagicMock()
    printer.print_document.side_effect = OSError("cable desconectado")
    printer.get_printer_status.side_effect = OSError("sin puerto")
    monkeypatch.setattr(document_handler, "printer_instance", lambda cfg: (printer, None))

    resp = app_client.post("/api/printers", json=sample_invoice_payload)
    body = resp.get_json()
    assert resp.status_code == 500
    assert body["data"]["Estado"] == "Error interno"
    assert "cable desconectado" in body["data"]["Error"]


def test_blueprint_errorhandler_returns_boolean_false(app_client, monkeypatch):
    """Unhandled exceptions in a route return status false (boolean) with Estado/Error."""
    from server import server_api

    def _boom(*args, **kwargs):
        raise RuntimeError("fallo inesperado")

    monkeypatch.setattr(server_api, "handle_fiscal_commands", _boom)
    resp = app_client.post("/api/command", json={"commands": ["A"]})
    body = resp.get_json()
    assert resp.status_code == 500
    assert body["status"] is False
    assert body["data"] == {"Estado": "Error interno", "Error": "fallo inesperado"}


def test_ping_returns_machine_serial(app_client, monkeypatch):
    """GET /api/ping returns the serial read from the machine instead of the template default."""
    from server.handlers.printer_manager import PrinterManager

    monkeypatch.setattr(PrinterManager, "read_serial", classmethod(lambda cls, t, c: "Z7C7034708"))
    body = app_client.get("/api/ping").get_json()
    assert body == {"status": "success", "message": "Z7C7034708"}


def test_ping_falls_back_to_configured_serial(app_client, monkeypatch):
    """When the machine cannot be read, the serial configured in the Fiscal tab (template) is returned."""
    from server.handlers.printer_manager import PrinterManager
    from server import server_api

    monkeypatch.setattr(PrinterManager, "read_serial", classmethod(lambda cls, t, c: None))
    monkeypatch.setattr(server_api, "_configured_serial", lambda: "Z1B9999999")
    body = app_client.get("/api/ping").get_json()
    assert body == {"status": "success", "message": "Z1B9999999"}
