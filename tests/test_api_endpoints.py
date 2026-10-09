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
