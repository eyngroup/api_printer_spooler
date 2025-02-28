#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Define el esquema JSON para la validación de documentos."""

from typing import Dict, Any

from jsonschema import validate, ValidationError

# Constantes para valores permitidos
VALID_OPERATION_TYPES = {"invoice", "credit", "debit", "note"}
VALID_DISCOUNT_TYPES = {"discount_percentage", "surcharge_percentage", "discount_amount", "surcharge_amount"}

# Esquema principal
DOCUMENT_SCHEMA = {
    "type": "object",
    "properties": {
        "operation_type": {"type": "string", "enum": list(VALID_OPERATION_TYPES)},
        "affected_document": {
            "type": "object",
            "properties": {
                "affected_number": {"type": "string"},
                "affected_date": {"type": "string", "format": "date"},
                "affected_serial": {"type": "string"},
            },
            "required": ["affected_number", "affected_date"],
        },
        "customer": {
            "type": "object",
            "properties": {
                "customer_vat": {"type": "string"},
                "customer_name": {"type": "string"},
                "customer_address": {"type": "string"},
                "customer_phone": {"type": "string"},
                "customer_email": {"type": "string", "format": "email"},
            },
            "required": ["customer_vat", "customer_name"],
        },
        "document": {
            "type": "object",
            "properties": {
                "document_number": {"type": "string"},
                "document_date": {"type": "string", "format": "date"},
                "document_name": {"type": "string"},
                "document_cashier": {"type": "string"},
            },
            "required": ["document_number", "document_date", "document_cashier"],
        },
        "items": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "properties": {
                    "item_ref": {"type": "string"},
                    "item_name": {"type": "string"},
                    "item_quantity": {"type": "number", "minimum": 0},
                    "item_price": {"type": "number", "minimum": 0},
                    "item_tax": {"type": "number", "minimum": 0},
                    "item_discount": {"type": "number", "minimum": 0},
                    "item_discount_type": {"type": "string", "enum": list(VALID_DISCOUNT_TYPES)},
                    "item_comment": {"type": "string"},
                },
                "required": ["item_name", "item_quantity", "item_price", "item_tax"],
            },
        },
        "payments": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "properties": {
                    "payment_method": {"type": "string"},
                    "payment_name": {"type": "string"},
                    "payment_amount": {"type": "number", "minimum": 0},
                },
                "required": ["payment_method", "payment_amount"],
            },
        },
        "delivery": {
            "type": "object",
            "properties": {
                "delivery_comments": {"type": "array", "items": {"type": "string"}},
                "delivery_barcode": {"type": "string"},
            },
        },
        "operation_metadata": {
            "type": "object",
            "properties": {
                "terminal_id": {"type": "string"},
                "branch_code": {"type": "string"},
                "operator_id": {"type": "string"},
            },
            "required": ["terminal_id", "operator_id"],
        },
    },
    "required": ["operation_type", "customer", "document", "items", "payments"],
}


def validate_document(document: Dict[str, Any]) -> None:
    """
    Valida un documento contra el esquema definido.
    Args:
        document: Diccionario con los datos del documento a validar
    Raises:
        ValidationError: Si el documento no cumple con el esquema
    Returns: None
    """
    try:
        validate(document, DOCUMENT_SCHEMA)
    except ValidationError as e:
        path = " -> ".join(str(p) for p in e.path)
        raise ValidationError(f"En {path}: {e.message}. {e.schema.get('errorMessage', 'Error de validación.')}") from e
