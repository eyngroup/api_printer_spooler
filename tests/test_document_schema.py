"""
Unit tests for JSON schema and business rule validation.
"""

import pytest
from jsonschema import ValidationError
from models.model_invoice import Invoice, InvoiceItem, Payment
from server.document_schema import validate_document


@pytest.fixture
def valid_document_payload():
    return {
        "operation_type": "invoice",
        "affected_document": {
            "affected_number": "00000001",
            "affected_date": "2026-10-04",
            "affected_serial": "Z1B1234567",
        },
        "customer": {
            "customer_name": "EMPRESA DEMO C.A.",
            "customer_vat": "J-12345678-9",
            "customer_address": "Av. Principal 123",
            "customer_phone": "+58 414-1234567",
            "customer_email": "demo@empresa.com",
        },
        "document": {
            "document_number": "INV-00100",
            "document_reference": "PED-12345",
            "document_date": "2026-10-04",
            "document_time": "10:30:00",
            "document_name": "FACTURA DE VENTA",
            "document_cashier": "Cajero 1",
        },
        "items": [
            {
                "item_ref": "PROD-01",
                "item_name": "Producto de Prueba",
                "item_quantity": 2.0,
                "item_price": 10.0,
                "item_tax": 16,
                "item_comment": "Comentario de item",
            }
        ],
        "payments": [
            {
                "payment_method": "01",
                "payment_name": "Efectivo",
                "payment_amount": 23.2,
            }
        ],
        "delivery": {
            "delivery_comments": ["Entregar en porteria"],
            "delivery_barcode": "123456789012",
        },
        "operation_metadata": {
            "terminal_id": "TERM-01",
            "branch_code": "001",
            "operator_id": "OP-1",
            "currency_code": "VES",
            "exchange_rate": 1.0,
            "inverse_rate": 1.0,
        },
    }


def test_validate_document_schema_success(valid_document_payload):
    """A well-formed document should pass schema validation."""
    validate_document(valid_document_payload)


def test_validate_document_schema_missing_fields(valid_document_payload):
    """Removing a required section should trigger ValidationError."""
    del valid_document_payload["customer"]
    with pytest.raises(ValidationError):
        validate_document(valid_document_payload)


def test_invoice_business_validation_success(valid_document_payload):
    """Valid invoice passes business validation."""
    inv = Invoice(valid_document_payload)
    err = inv.validate()
    assert err is None


def test_invoice_credit_without_affected_document(valid_document_payload):
    """Credit note without affected document must fail business validation."""
    valid_document_payload["operation_type"] = "credit"
    valid_document_payload["affected_document"] = {}
    inv = Invoice(valid_document_payload)
    err = inv.validate()
    assert err is not None
    assert "documento afectado" in err.lower()


def test_invoice_item_invalid_tax():
    """Item with unsupported tax percentage fails item validation."""
    item = InvoiceItem({
        "item_ref": "ART-01",
        "item_name": "Articulo",
        "item_quantity": 1,
        "item_price": 5.0,
        "item_tax": 99,  # 99% is not in ALLOWED_TAX_VALUES (0, 8, 16, 31, 12)
    })
    err = item.validate()
    assert err is not None
    assert "impuesto" in err.lower()


def test_invoice_item_excessive_discount():
    """Item with discount percentage >= 100 fails validation."""
    item = InvoiceItem({
        "item_ref": "ART-01",
        "item_name": "Articulo",
        "item_quantity": 1,
        "item_price": 5.0,
        "item_tax": 16,
        "item_discount": 105.0,
        "item_discount_type": "discount_percentage",
    })
    err = item.validate()
    assert err is not None
    assert "99.99%" in err


def test_payment_invalid_method():
    """Payment method must be between 01 and 24."""
    payment = Payment({
        "payment_method": "99",
        "payment_name": "Metodo Invalido",
        "payment_amount": 10.0,
    })
    err = payment.validate()
    assert err is not None
    assert "entre 01 y 24" in err


def test_invoice_rounding_fallback_applied(valid_document_payload):
    """Slight difference within 0.1% tolerance must be auto-adjusted without error."""
    # Setup large document like customer invoice (702,823.49 Bs) with 1.25 Bs rounding difference
    valid_document_payload["items"] = [
        {
            "item_name": "Suministro Medico Especial",
            "item_quantity": 1,
            "item_price": 605882.32,
            "item_tax": 16,
        }
    ]
    # Total with tax = 605882.32 * 1.16 = 702823.49
    # Payment sent from Odoo with slight discrepancy: 702822.24 (diff: 1.25)
    valid_document_payload["payments"] = [
        {
            "payment_method": "01",
            "payment_amount": 702822.24,
        }
    ]

    inv = Invoice(valid_document_payload)
    err = inv.validate()
    # Must succeed (None) thanks to 0.1% fallback
    assert err is None
    # Must adjust payment to match document total
    assert inv.payments[-1].amount == inv.total_with_tax
    assert valid_document_payload["payments"][-1]["payment_amount"] == inv.total_with_tax


def test_invoice_excessive_difference_rejected(valid_document_payload):
    """Difference exceeding 0.1% tolerance must fail validation."""
    valid_document_payload["items"] = [
        {
            "item_name": "Suministro Medico Especial",
            "item_quantity": 1,
            "item_price": 605882.32,
            "item_tax": 16,
        }
    ]
    # Underpayment of 5000 Bs exceeds 0.1% tolerance (~702.82 Bs)
    valid_document_payload["payments"] = [
        {
            "payment_method": "01",
            "payment_amount": 697823.49,
        }
    ]

    inv = Invoice(valid_document_payload)
    err = inv.validate()
    assert err is not None
    assert "superando la tolerancia permitida" in err
