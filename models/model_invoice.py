#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Clases que manejar el modelo de facturas. Contiene reglas de negocio."""

from datetime import datetime
from typing import Dict, Optional


class InvoiceItem:
    """Clase que representa un ítem de un documento."""

    def __init__(self, data: Dict):
        self.ref = data.get("item_ref", "")
        self.name = data.get("item_name", "")
        self.quantity = data.get("item_quantity", 0)
        self.price = data.get("item_price", 0)
        self.tax = data.get("item_tax", 0)
        self.discount = data.get("item_discount", 0)
        self.discount_type = data.get("item_discount_type", "")
        self.comment = data.get("item_comment", "")

    def validate(self) -> Optional[str]:
        """Validar reglas de negocio del item"""
        if self.discount > 0:  # Validar que el precio con descuento no sea negativo
            if self.discount_type in ["discount_percentage", "surcharge_percentage"]:
                if self.discount > 99.99:
                    return f"{self.discount_type} no puede ser mayor a 99.99%"
                if self.discount_type == "discount_percentage":
                    precio_final = self.price * (1 - self.discount / 100)
                else:  # surcharge_percentage
                    precio_final = self.price * (1 + self.discount / 100)
            else:  # discount_amount o surcharge_amount
                if self.discount_type == "discount_amount":
                    precio_final = self.price - self.discount
                    if precio_final < 1:
                        return "Descuento no puede ser mayor o igual al precio"
                else:  # surcharge_amount
                    precio_final = self.price + self.discount
        return None

    @property
    def subtotal(self) -> float:
        """Calcula el subtotal del item con descuento o recargo"""
        if self.discount > 0:
            if self.discount_type == "discount_percentage":
                return self.price * self.quantity * (1 - self.discount / 100)
            if self.discount_type == "surcharge_percentage":
                return self.price * self.quantity * (1 + self.discount / 100)
            if self.discount_type == "discount_amount":
                return (self.price - self.discount) * self.quantity
            if self.discount_type == "surcharge_amount":
                return (self.price + self.discount) * self.quantity
        return self.price * self.quantity


class Payment:  # pylint: disable=R0903
    """Modelo para representar un pago en un documento"""

    def __init__(self, data: Dict):
        self.method = data.get("payment_method", "")
        self.name = data.get("payment_name", "")
        self.amount = data.get("payment_amount", 0)

    def validate(self) -> Optional[str]:
        """Validar reglas de negocio del pago"""
        try:
            payment_code = int(self.method)
            if payment_code < 1 or payment_code > 24:
                return "Código de pago debe estar entre 01 y 24"
            self.method = f"{payment_code:02d}"  # Asegurar formato de dos dígitos
        except ValueError:
            return "Código de pago debe ser un número entre 01 y 24"
        return None


class Invoice:
    """Modelo para representar una factura"""

    def __init__(self, data: Dict):
        self.operation_type = data.get("operation_type", "")  # Datos de operación

        self.affected_document = data.get("affected_document", {})  # Documento afectado

        customer_data = data.get("customer", {})  # Datos del cliente
        self.customer_vat = customer_data.get("customer_vat", "")
        self.customer_name = customer_data.get("customer_name", "")
        self.customer_address = customer_data.get("customer_address", "")
        self.customer_phone = customer_data.get("customer_phone", "")
        self.customer_email = customer_data.get("customer_email", "")

        document_data = data.get("document", {})  # Datos del documento
        self.document_number = document_data.get("document_number", "")
        self.document_date = document_data.get("document_date", "")
        self.document_name = document_data.get("document_name", "")
        self.document_cashier = document_data.get("document_cashier", "")

        self.items = [InvoiceItem(item) for item in data.get("items", [])]  # Listas
        self.payments = [Payment(payment) for payment in data.get("payments", [])]  # Listas

        delivery_data = data.get("delivery", {})  # Datos de entrega
        self.delivery_comments = delivery_data.get("delivery_comments", [])
        self.delivery_barcode = delivery_data.get("delivery_barcode", "")

        self.metadata = data.get("operation_metadata", {})  # Datos de operación

    def validate(self) -> Optional[str]:
        """Valida reglas de negocio del documento"""
        if self.operation_type in ["credit", "debit"]:  # Validar documento afectado
            if not self.affected_document:
                return "Notas de crédito/débito requieren documento afectado"

            try:  # Validar que la fecha del documento afectado sea anterior
                affected_date = datetime.strptime(self.affected_document["affected_date"], "%Y-%m-%d")
                current_date = datetime.strptime(self.document_date, "%Y-%m-%d")
                if affected_date > current_date:
                    return "Fecha del documento afectado no puede ser posterior a la fecha actual"
            except ValueError:
                return "Error en formato de fechas"

        for idx, item in enumerate(self.items, 1):
            if error := item.validate():  # Validar items
                return f"Error en item {idx}: {error}"

        total_pagos = sum(payment.amount for payment in self.payments)  # Validar total de pagos
        if abs(total_pagos - self.total_with_tax) > 0.01:  # Permitir diferencia por redondeo
            return f"Total de pagos ({total_pagos}) no coincide con el total del documento ({self.total_with_tax})"

        return None

    @property
    def total_amount(self) -> float:
        """Calcula el subtotal del documento incluyendo descuentos"""
        return sum(item.subtotal for item in self.items)

    @property
    def total_tax(self) -> float:
        """Calcula el impuesto total del documento"""
        return sum(item.subtotal * (item.tax / 100) for item in self.items)

    @property
    def total_with_tax(self) -> float:
        """Calcula el monto total con impuestos"""
        return self.total_amount + self.total_tax

    @property
    def total_discount(self) -> float:
        """Calcula el descuento total aplicado"""
        total_sin_ajustes = sum(item.price * item.quantity for item in self.items)
        total_con_ajustes = sum(
            item.subtotal for item in self.items if item.discount_type in ["discount_percentage", "discount_amount"]
        )
        return total_sin_ajustes - total_con_ajustes

    @property
    def total_surcharge(self) -> float:
        """Calcula el recargo total aplicado"""
        total_sin_ajustes = sum(item.price * item.quantity for item in self.items)
        total_con_ajustes = sum(
            item.subtotal for item in self.items if item.discount_type in ["surcharge_percentage", "surcharge_amount"]
        )
        return total_con_ajustes - total_sin_ajustes
