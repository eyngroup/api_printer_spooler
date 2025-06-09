# -*- coding: utf-8 -*-
from datetime import date
import logging
import json
import socket
from odoo import models, api, fields

from bs4 import BeautifulSoup

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    """Account Move"""

    _inherit = "account.move"

    aps_date = fields.Date(string="Document Date", readonly=True, copy=False)
    aps_number = fields.Char(string="Document Number", size=10, readonly=True, copy=False)
    aps_report = fields.Char(string="Machine Report", size=6, readonly=True, copy=False)
    aps_serial = fields.Char(string="Machine Serial", size=12, readonly=True, copy=False)
    aps_printed = fields.Boolean(string="Printed", readonly=True, copy=False, default=False)

    def _calculate_vat_checkdigit(self, kind, numbers):
        """Calculate check digit based on standard method 'check_vat_ve'"""
        # Mapeo de tipo de documento a dígito
        kind_mapping = {
            "v": 1,  # Venezuela citizenship
            "e": 2,  # Foreigner
            "c": 3,  # Township/Communal Council
            "j": 3,  # Legal entity
            "p": 4,  # Passport
            "g": 5,  # Government
        }
        # Calcular dígito de verificación
        kind_digit = kind_mapping.get(kind.lower(), 1)
        multipliers = [3, 2, 7, 6, 5, 4, 3, 2]
        checksum = kind_digit * 4
        checksum += sum(int(n) * m for n, m in zip(numbers, multipliers))
        check_digit = 11 - (checksum % 11)
        if check_digit > 9:
            check_digit = 0

        return str(check_digit)

    def _format_vat(self, vat):
        """Format VAT number to required format"""
        default_prefix = "J" if self.partner_id.is_company else "V"
        if not vat:
            return f"{default_prefix}-00000000-0"

        # Validar si viene con formato correcto (X-12345678-9)
        if len(vat) == 12 and vat[1] == "-" and vat[10] == "-":
            prefix = vat[0].upper()
            valid_prefixes = {"V", "E", "C", "J", "P", "G"}
            return vat if prefix in valid_prefixes else f"{default_prefix}{vat[1:]}"

        clean_vat = "".join(c for c in vat if c.isalnum())
        valid_prefixes = {"V", "E", "C", "J", "P", "G"}
        first_char = clean_vat[0].upper() if clean_vat and clean_vat[0].isalpha() else default_prefix
        first_char = first_char if first_char in valid_prefixes else default_prefix
        numbers = "".join(c for c in clean_vat if c.isdigit())
        numbers = numbers.zfill(8)[:8]  # Asegurar 8 dígitos

        # Calcular dígito de verificación si no está o si fueron modificados
        if len(clean_vat) < 9 or not clean_vat[-1].isdigit():
            check_digit = self._calculate_vat_checkdigit(first_char, numbers)
        else:
            check_digit = clean_vat[-1]

        return f"{first_char}-{numbers}-{check_digit}"

    def _get_operation_type(self):
        operation_types = {"out_invoice": "invoice", "out_refund": "credit", "out_debit": "debit"}
        return operation_types.get(self.move_type, "invoice")

    def _prepare_affected_document(self):
        """Prepare affected document data for credit/debit notes"""
        return {
            "affected_number": self.reversed_entry_id.aps_number or "00000000",
            "affected_date": str(self.reversed_entry_id.aps_date or self.invoice_date),
            "affected_serial": self.reversed_entry_id.aps_serial or "Z1B1234567",
        }

    def _prepare_customer_data(self):
        """Prepare customer data section"""
        partner_vat = self._format_vat(self.partner_id.vat)
        partner_name = self.partner_id.name
        if not partner_name or partner_name.strip() == "":
            partner_name = "CLIENTE CONTADO"

        address_lines = (self.partner_id.contact_address or "").split("\n")
        if len(address_lines) > 1:
            partner_address = " ".join(address_lines[1:])
        else:
            partner_address = ""
        partner_phone = self.partner_id.mobile or self.partner_id.phone or ""
        partner_email = self.partner_id.email or ""

        print(f"test dir: {partner_address}")

        return {
            "customer_vat": partner_vat,
            "customer_name": partner_name,
            "customer_address": partner_address,
            "customer_phone": partner_phone,
            "customer_email": partner_email,
        }

    def _prepare_document_data(self):
        """Prepare document data section"""
        doc_number = str(self.id).zfill(10)  # id es el número de documento a 10 dígitos
        doc_date = str(self.invoice_date or date.today())
        doc_name = self.name or ""
        doc_cashier = self.partner_id.user_id.name or self.invoice_user_id.name or "VENTAS"

        return {
            "document_number": doc_number,
            "document_date": doc_date,
            "document_name": doc_name,
            "document_cashier": doc_cashier,
        }

    def _prepare_items_data(self):
        """Prepare items data section"""
        items = []
        discount_lines = []
        last_product_item = None  # Para rastrear el último producto

        for line in self.invoice_line_ids:
            if line.display_type == "line_section":
                continue  # Ignorar secciones

            if line.display_type == "line_note":
                if last_product_item:
                    current_comment = last_product_item["item_comment"]
                    if current_comment:  # Agregar la nota al comentario del último producto
                        last_product_item["item_comment"] = f"{current_comment} {line.name}"
                    else:
                        last_product_item["item_comment"] = line.name
                continue  # Manejar notas

            # identificación de descuento por nombre de producto
            is_discount_line = (
                line.product_id
                and line.price_unit < 0
                and line.product_id.type == "service"
                and any(keyword in line.product_id.name.lower() for keyword in ["discount", "descuento"])
            )

            if is_discount_line:  # Acumular descuentos por producto
                discount_lines.append({"amount": abs(line.price_subtotal), "description": line.name})
                continue

            # Descuentos o incrementos por línea de productos
            discount_value = abs(line.discount) if line.discount else 0
            discount_type = "surcharge_percentage" if line.discount < 0 else "discount_percentage"

            # Comentario como parte de la descripción del producto
            comment_value = ""
            if line.name != line.product_id.display_name:
                comment_value = " ".join(line.name.split("\n"))

            product_ref = line.product_id.default_code or ""
            product_name = line.product_id.name if line.product_id else ""
            product_quantity = line.quantity
            product_price = line.price_unit
            product_tax = line.tax_ids.amount

            item = {
                "item_ref": product_ref,
                "item_name": product_name,
                "item_quantity": product_quantity,
                "item_price": product_price,
                "item_tax": product_tax,
                "item_discount": discount_value,
                "item_discount_type": discount_type,
                "item_comment": comment_value,
            }

            items.append(item)
            last_product_item = item  # Identificar el último producto

        if discount_lines and items:  # Descuentos acumulados aplicados al último item
            total_discount = sum(d["amount"] for d in discount_lines)
            items[-1]["item_discount"] = total_discount
            items[-1]["item_discount_type"] = "discount_amount"

        return items

    def _prepare_payments_data(self):
        """Prepare payments data section"""
        config = self.env["ir.config_parameter"].sudo()
        default_code = config.get_param("aps_default_payment_code", "01")
        default_name = config.get_param("aps_default_payment_name", "EFECTIVO")
        payments = []

        if self.payment_state in ["paid", "partial"]:
            payment_lines = self.env["account.payment"].search([("ref", "like", self.name), ("state", "=", "posted")])

            for payment in payment_lines:  # Buscar pagos por referencia
                journal = payment.journal_id
                payments.append(
                    {
                        "payment_method": journal.aps_payment_code or default_code,
                        "payment_name": journal.aps_payment_name or default_name,
                        "payment_amount": payment.amount,
                    }
                )

            if not payments:  # Si no hay pagos por referencia, buscar por reconciliación
                for line in self.line_ids.filtered(
                    lambda l: l.account_type in ["asset_receivable", "liability_payable"]
                ):
                    for payment in line.matched_credit_ids.mapped("credit_move_id"):
                        if payment.payment_id:
                            journal = payment.payment_id.journal_id
                            payments.append(
                                {
                                    "payment_method": journal.aps_payment_code or default_code,
                                    "payment_name": journal.aps_payment_name or default_name,
                                    "payment_amount": payment.amount_total,
                                }
                            )

        if not payments:  # Si no hay pagos registrados, usar valores por defecto
            payments.append(
                {"payment_method": default_code, "payment_name": default_name, "payment_amount": self.amount_total}
            )

        return payments

    def _prepare_delivery_data(self):
        """Prepare delivery data section"""
        picking_name = ""
        if self.invoice_origin:  # Buscar el pedido de venta
            sale_order = self.env["sale.order"].search([("name", "=", self.invoice_origin)], limit=1)

            if sale_order:
                all_pickings = self.env["stock.picking"].search([("sale_id", "=", sale_order.id)])

                _logger.debug("Buscar todos los pickings %s", all_pickings)

                picking = self.env["stock.picking"].search(
                    [
                        ("sale_id", "=", sale_order.id),
                        ("state", "not in", ["cancel", "draft"]),
                        ("picking_type_code", "=", "outgoing"),
                    ],
                    order="id desc",
                    limit=1,
                )  # Buscar el picking específico

                if picking:
                    picking_name = picking.name

        comments = []
        if self.invoice_payment_term_id.note:  # Comentarios por términos de pago
            clean_note = BeautifulSoup(str(self.invoice_payment_term_id.note), "html.parser").get_text().strip()
            if clean_note:
                comments.append(clean_note)

        if self.narration:  # Comentarios por condiciones
            clean_narration = BeautifulSoup(str(self.narration), "html.parser").get_text().strip()
            if clean_narration:
                comments.append(clean_narration)

        return {"delivery_comments": comments, "delivery_barcode": picking_name}

    def _prepare_operation_metadata(self):
        """Prepare operation metadata section"""
        terminal = socket.gethostname()
        company_currency = self.company_id.currency_id
        document_currency = self.currency_id
        exchange_rate = 1.0
        inverse_rate = 1.0

        if company_currency != document_currency:  # Buscar la tasa de cambio
            currency_rate = self.env["res.currency.rate"].search(
                [
                    ("currency_id", "=", document_currency.id),
                    ("company_id", "=", self.company_id.id),
                    ("name", "<=", self.invoice_date or fields.Date.today()),
                ],
                order="name desc",
                limit=1,
            )

            if currency_rate:
                exchange_rate = currency_rate.company_rate
                inverse_rate = currency_rate.inverse_company_rate

        branch = self.journal_id.code or "SUC001"  # desarrollo para sucursales
        operator = self.invoice_user_id.login or "OP001"
        currency = self.currency_id.name or "VEB"

        return {
            "terminal_id": terminal[:15],
            "branch_code": branch,
            "operator_id": operator,
            "currency_code": currency,
            "exchange_rate": exchange_rate,
            "inverse_rate": inverse_rate,
        }

    def _prepare_printer_data(self):
        """Prepare complete data structure for printer"""
        data = {
            "operation_type": self._get_operation_type(),
            "affected_document": self._prepare_affected_document(),
            "customer": self._prepare_customer_data(),
            "document": self._prepare_document_data(),
            "items": self._prepare_items_data(),
            "payments": self._prepare_payments_data(),
            "delivery": self._prepare_delivery_data(),
            "operation_metadata": self._prepare_operation_metadata(),
        }

        return data

    def button_send_to_printer(self):
        if self.aps_printed:
            raise UserWarning("This document has already been printed")

        config = self.env["ir.config_parameter"].sudo()
        api_url = f"{config.get_param('aps_ip')}:{config.get_param('aps_port')}/api/printers"

        printer_data = self._prepare_printer_data()
        _logger.info("API PRINTER DOCUMENT:\n" + json.dumps(printer_data, indent=2, ensure_ascii=False))
        encoded_data = json.loads(json.dumps(printer_data, ensure_ascii=False))

        return {
            "type": "ir.actions.client",
            "tag": "PrinterInvoiceAPI",
            "params": {"url": api_url, "data": encoded_data, "invoice_id": self.id},
        }

    def update_printer_response(self, response_data):
        """Update invoice with printer response data"""
        try:
            self.ensure_one()
            self.env["account.move"].sudo().browse(self.id).write(
                {
                    "aps_date": response_data.get("document_date"),
                    "aps_number": response_data.get("document_number"),
                    "aps_report": response_data.get("machine_report"),
                    "aps_serial": response_data.get("machine_serial"),
                    "aps_printed": True,
                }
            )
            return True
        except Exception as e:
            _logger.error("Error updating invoice: %s", str(e))
            return False

    @api.model
    def get_fiscal_report(self, report_type):
        return {"type": "ir.actions.client", "tag": "fiscal_report", "params": {"report_type": report_type}}
