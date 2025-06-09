#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright © 2024, Iron Graterol
Licensed under the GNU Affero General Public License, version 3 or later.

Clase para el manejo de la impresora fiscal PNP
"""

import datetime
import time
import json
import logging
import os
from decimal import Decimal, ROUND_HALF_UP, getcontext
from typing import Any, Dict, Union

from controllers.pfpnp import FiscalPrinterPnp
from printers.printer_base import BasePrinter
from printers.printer_commands import PNPcmd
from handy.tools import get_base_path, normalize_text, normalize_date, normalize_number, format_time

# Configuración del logging
logger = logging.getLogger(__name__)


class PnpPrinter(BasePrinter):
    """Clase para manejar la impresión en impresoras fiscales PNP"""

    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa la impresora fiscal y establece la conexión
        Args:
            config (dict): Configuración de la impresora
        """
        super().__init__(config)
        self.template_config = self._load_config("template_fiscal_printer.json", "templates")
        self.baudrate = config.get("fiscal_baudrate", 9600)
        self.enabled = config.get("fiscal_enabled", False)
        self.printer = config.get("fiscal_name", "pnp")
        self.port = config.get("fiscal_port")
        self.timeout = config.get("fiscal_timeout", 2)
        self._printer = None
        self._model = self.template_config.get("fiscal", {}).get("model", "PF-220")  # Modelo de la impresora
        self._serial = None  # Serial de la impresora
        self._type_doc = None
        self._last_document = "0000000000"

        self._initialize_printer()
        if not self.connect():
            raise ConnectionError(f"Error al conectar con la impresora: {self.printer}")

    def _load_config(self, file_name: str, local_path: str) -> Dict[str, Any]:
        """
        Carga un archivo de configuración JSON desde el directorio especificado.
        Args:
            file_name (str): Nombre del archivo de configuración
            local_path (str): Directorio donde se encuentra el archivo
        Returns:
            Dict[str, Any]: Configuración cargada del archivo JSON
        """
        try:
            config_path = os.path.join(get_base_path(), local_path, file_name)
            if not os.path.exists(config_path):
                logger.error("Archivo de configuración no encontrado: %s", config_path)
                return {}

            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning("Error cargando configuración %s: %s", file_name, str(e))
            return {}

    def _initialize_printer(self) -> None:
        """Crea la instancia del controlador de la impresora PNP"""
        try:
            self._printer = FiscalPrinterPnp(self.port, self.baudrate, self.timeout)
            logger.info("Impresora PNP inicializada")
        except Exception as e:
            logger.error("Error al inicializar la impresora PNP: %s", str(e))
            raise

    def _format_number(self, value: Union[float, int, str], field_type: str) -> str:
        """
        Formatea un número como string según el tipo de campo para la impresora PNP.
        Los números se formatean con punto decimal y el número de decimales depende del tipo.
        Args:
            value: Valor a formatear (puede ser float, int o str)
            field_type: Tipo de campo ('quantity', 'price', 'payment', 'discount')
        Returns:
            str: Valor formateado como string con punto decimal
        """
        try:
            decimals = 2
            getcontext().rounding = ROUND_HALF_UP
            decimal_value = Decimal(str(value))
            if field_type == "quantity":
                decimals = 3

            format_str = f"{{:.{decimals}f}}"
            formatted = format_str.format(float(decimal_value))
            formatted = formatted.replace(".", "")
            return formatted
        except Exception as e:
            logger.error("Error al formatear número (%s): %s", field_type, str(e))
            raise

    def _format_text(self, text: str, field_type: str) -> str:
        """
        Formatea texto según los límites del modelo de impresora PNP.
        Normaliza el texto y lo trunca según el tipo de campo y modelo.
        Args:
            text: Texto a formatear
            field_type: Tipo de campo ('product', 'comment', 'line', 'header', 'footer', 'partner', 'vat')
        Returns:
            str: Texto formateado según las especificaciones del modelo
        """
        try:
            max_char_config = self._load_config("pnp_max_char.json", "config")
            if not max_char_config:
                logger.warning("No se pudo cargar la configuración de caracteres máximos")
                max_chars = 40 if self._model == "PF-300" else 20 if field_type == "product" else 40
            else:
                model_config = max_char_config.get(self._model, max_char_config["PF-220"])  # PF-220 como fallback
                max_chars = model_config.get(field_type, 40)  # 40 como valor por defecto

            normalized = normalize_text(text)
            return normalized[:max_chars]
        except Exception as e:
            logger.error("Error al formatear texto (%s): %s", field_type, str(e))
            normalized = normalize_text(text)  # Valores seguros por defecto en caso de error
            return normalized[:40]

    def connect(self) -> bool:
        """
        Establece la conexión con la impresora
        Returns:
            bool: True si la conexión fue exitosa
        """
        try:
            if self._printer.open_port():
                if not self.check_status():
                    self._printer.close_port()
                    return False

                serial_info = self._printer.get_version()  # Obtener modelo de la impresora
                if not serial_info:
                    raise RuntimeError("No se pudo obtener el modelo o serial de la impresora")
                self._model = serial_info.get("modelo", "PF-220")
                self._serial = serial_info.get("serial", "EOO9000000")

                logger.info("Conexión con impresora modelo: %s, serial: %s", self._model, self._serial)
                return True
            logger.error("Error al conectar con el puerto: %s", self.port)
            return False
        except KeyError as ke:
            logger.error("KeyError: %s", ke)
            self._printer.close_port()
            return False
        except Exception as e:
            logger.error("Error al iniciar conexión: %s", str(e))
            self._printer.close_port()
            return False

    def disconnect(self) -> None:
        """Desconecta la impresora fiscal"""
        try:
            self._printer.close_port()
            logger.info("Desconexión exitosa")
        except Exception as e:
            logger.error("Error al desconectar: %s", str(e))

    def send_command(self, command: str, wait_time: float = 0.0) -> bool:
        """
        Envía un comando a la impresora
        Args:
            command (str): Comando a enviar
            wait_time (float): Tiempo de espera después del comando
        Returns:
            bool: True si el comando se ejecutó correctamente
        """
        try:
            value = False
            logger.info("Comando  Enviado: %s", command)
            result = self._printer.send_cmd(command)
            logger.debug("Valores Recibidos: %s", result)
            if result:
                if result[0] == "0080" and result[1] == "2600":
                    value = True

                if result[0] == "0080" and result[1] == "3600":
                    value = True

                if result[0] == "0080" and result[1] == "0600" and len(result) == 2:
                    value = True

                if result[0] == "0080" and result[1] == "0600" and len(result) >= 3:
                    if self._type_doc == "note":
                        self._last_document = result[2]
                    elif self._type_doc == "invoice":
                        self._last_document = result[3]
                    elif self._type_doc == "credit":
                        self._last_document = result[4]
                    else:
                        self._last_document = "0000000000"
                    logger.info("Documento Fiscal: %s", self._last_document)
                    value = True

                if wait_time > 0:
                    time.sleep(wait_time)

            return value
        except Exception as e:
            logger.error("Error al enviar comando %s: %s", command, str(e))
            return False

    def check_status(self) -> bool:
        """
        Verifica si la impresora está lista para operar
        Returns:
            bool: True si la impresora está lista, False en caso contrario
        """
        try:
            status = self._printer.get_status()
            if status["status"] != "00":
                logger.error("Estado: %s", status["status_detallado"])
                return False

            if status["status_code"] != "0080" or status["error_code"] != "0600":
                logger.error("Estado: %s || Error: %s", status["status_code"], status["error_code"])
                self._cancel_doc(status["status_code"], status["error_code"])
                return False

            return True
        except Exception as e:
            logger.error("Error al verificar estado de la impresora: %s", str(e))
            return False

    def get_printer_status(self) -> Dict[str, Any]:
        """
        Obtiene el estado detallado de la impresora
        Returns:
            Dict[str, Any]: Diccionario con la información del estado
        """
        try:
            check_status = self._printer.get_status()
            if not check_status:
                logger.error("Error al obtener estado de la impresora")
                return {
                    "status_code": "0000",
                    "error_code": "0000",
                    "status": "Error al obtener estado",
                    "error": "Error al obtener estado",
                }

            if check_status["error_critico"] or check_status["requiere_servicio"]:
                logger.error("Estado: %s", check_status["estado_detallado"])

            return {
                "status_code": check_status["status_code"],
                "error_code": check_status["error_code"],
                "status": check_status["status"],
                "error": check_status["status_detallado"],
            }
        except Exception as e:
            logger.error("Error al obtener estado de impresora: %s", str(e))
            return {
                "status_code": "0000",
                "error_code": "0000",
                "status": f"Error inesperado: {str(e)}",
                "error": f"Error inesperado: {str(e)}",
            }

    def _cancel_doc(self, value1: str, value2: str) -> None:
        """Metodo para cancelar, anular o cerrar documento"""
        result = None
        if value1 == "0080" and value2 == "2600":
            result = self.send_command(PNPcmd.DNF_CLOSE)

        if value1 == "0080" and value2 == "8620":
            result = self.send_command(PNPcmd.CLOSE_TOTAL)

        logger.info("Resultado de Cancelado: %s", result)

    def report_x(self) -> bool:
        """Imprime reporte X (reporte diario sin cierre)"""
        try:
            if self.send_command(PNPcmd.DAILY_REPORT):
                time.sleep(3)
                return True
            return False
        except Exception as e:
            logger.error("Error al generar reporte X: %s", str(e))
            return False

    def report_z(self) -> bool:
        """Imprime reporte Z (cierre diario)"""
        try:
            if self.send_command(PNPcmd.DAILY_CLOSE):
                time.sleep(3)
                return True
            return False
        except Exception as e:
            logger.error("Error al generar reporte Z: %s", str(e))
            return False

    def print_document(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Imprime un documento fiscal
        Args:
            data (Dict[str, Any]): Documento a imprimir
        Returns:
            Dict[str, Any]: Resultado de la impresión
        """
        logger.debug("Procesando documento")
        status = self.get_printer_status()
        message_info = f"Estado: {status['status']} - {status['error']}"
        if status["status_code"] != "0080" or status["error_code"] != "0600":
            self._cancel_doc(status["status_code"], status["error_code"])

            logger.error("Estado Cod.: %s || Error Cod.: %s", status["status_code"], status["error_code"])
            logger.error("%s", message_info)
            return {
                "status": False,
                "message": f"Impresora fiscal {self.printer} en estado inoperativo",
                "data": {
                    "Estado": status["status"],
                    "Error": status["error"],
                },
            }

        try:
            operation_type = data.get("operation_type", "").lower()
            if operation_type not in ("credit", "debit", "invoice", "note"):
                return {
                    "status": False,
                    "message": f"Tipo de documento no válido: {operation_type}",
                    "data": None,
                }

            logger.info(message_info)
            self._type_doc = operation_type
            self._process_customer_data(data)  # Procesar datos del cliente
            self._process_items(data)  # Procesar ítems
            self._process_footer(data)  # Procesar pie de página
            self._process_payments(data)  # Procesar pagos
            return self._process_send_data()  # Procesar envio de datos
        except Exception as e:
            message_error = f"Falla durante la impresión del documento de tipo: {operation_type} [{str(e)}]"
            return {"status": False, "message": message_error, "data": None}

    def _process_customer_data(self, data: Dict[str, Any]) -> None:
        """Procesa y envía los datos del cliente a la impresora."""
        logger.debug("Procesando datos del documento")
        customer = data.get("customer", {})
        customer_vat = self._format_text(customer.get("customer_vat", ""), "vat")
        customer_name = self._format_text(customer.get("customer_name", ""), "partner")
        customer_address = self._format_text(customer.get("customer_address", ""), "comment")
        customer_phone = self._format_text(customer.get("customer_phone", ""), "comment")
        customer_email = self._format_text(customer.get("customer_email", ""), "comment")

        document = data.get("document", {})
        document_number = normalize_number(document.get("document_number", ""))
        document_date = normalize_date(document.get("document_date", ""))
        document_name = self._format_text(document.get("document_name", ""), "comment")
        document_cashier = self._format_text(document.get("document_cashier", ""), "comment")

        commands = []
        if self._type_doc == "credit":
            affected_document = data.get("affected_document", {})
            affected_number = normalize_number(affected_document.get("affected_number", ""), 10)
            affected_date = normalize_date(affected_document.get("affected_date", ""))
            affected_serial = self._format_text(affected_document.get("affected_serial", ""), "comment")
            current_time = format_time(datetime.datetime.now().strftime("%H%M"))

            resp = self.send_command(
                PNPcmd.OPEN_CREDIT.format(
                    customer_name,
                    customer_vat,
                    affected_number,
                    affected_serial,
                    affected_date,
                    current_time,
                )
            )
            if not resp:
                raise RuntimeError("Error al abrir nota de credito")

        if self._type_doc in ("debit", "invoice"):
            resp = self.send_command(PNPcmd.OPEN_INVOICE.format(customer_name, customer_vat))
            if not resp:
                raise RuntimeError("Error al abrir factura")

        if self._type_doc in ("credit", "debit", "invoice"):
            include_line = {
                "include_partner_address": PNPcmd.PARTNER_ADDRESS.format(customer_address),
                "include_partner_phone": PNPcmd.PARTNER_PHONE.format(customer_phone),
                "include_partner_email": PNPcmd.PARTNER_EMAIL.format(customer_email),
                "include_document_number": PNPcmd.DOCUMENT_NUMBER.format(document_number),
                "include_document_date": PNPcmd.DOCUMENT_DATE.format(document_date),
                "include_document_name": PNPcmd.DOCUMENT_NAME.format(document_name),
                "include_document_cashier": PNPcmd.DOCUMENT_CASHIER.format(document_cashier),
            }
            format_config = self.template_config.get("format", {})
            lines_add = [value for key, value in include_line.items() if format_config.get(key, False)]

            if lines_add:
                for command in lines_add[:3]:
                    resp = self.send_command(PNPcmd.COMMENTS.format(command))
                    if not resp:
                        raise RuntimeError("Error en datos adicionales de documento fiscal")
                self.send_command(PNPcmd.COMMENTS.format(PNPcmd.INTER_LINE))

        if self._type_doc == "note":
            name_note = self.template_config.get("fiscal", {}).get("name_note", "Nota")
            resp = self.send_command(PNPcmd.DNF_OPEN)

            if not resp:
                raise RuntimeError("Error en inicio de documento NO fiscal")
            commands = [
                name_note,
                PNPcmd.INTER_LINE,
                PNPcmd.PARTNER_VAT.format(customer_vat),
                PNPcmd.PARTNER_NAME.format(customer_name),
                PNPcmd.PARTNER_ADDRESS.format(customer_address),
                PNPcmd.PARTNER_PHONE.format(customer_phone),
                PNPcmd.PARTNER_EMAIL.format(customer_email),
                PNPcmd.DOCUMENT_NUMBER.format(document_number),
                PNPcmd.DOCUMENT_DATE.format(document_date),
                PNPcmd.DOCUMENT_NAME.format(document_name),
                PNPcmd.DOCUMENT_CASHIER.format(document_cashier),
                PNPcmd.INTER_LINE,
            ]
            for command in commands:
                resp = self.send_command(PNPcmd.DNF_TEXT.format(command))
                if not resp:
                    raise RuntimeError("Error en datos de documento NO fiscal")

    def _process_items(self, data: Dict[str, Any]) -> None:
        """Procesa y envía los ítems del documento a la impresora."""
        logger.debug("Procesando items")

        for item in data.get("items", []):
            item_comment = self._format_text(item.get("item_comment", ""), "comment")
            if self.template_config.get("format", {}).get("include_item_reference", False):
                item_code = item.get("item_ref", "")
                item_product = item.get("item_name", "")
                item_name = self._format_text(f"[{item_code}] {item_product}", "product")
            else:
                item_name = self._format_text(item.get("item_name", ""), "product")

            item_quantity = self._format_number(item.get("item_quantity", 0), "quantity")
            item_price = self._format_number(item.get("item_price", 0), "price")
            item_tax = item.get("item_tax", "0")

            if self._type_doc == "note":
                item_line = f"{item_name} x{item_quantity} x{item_price} Iva:{item_tax}"
                resp = self.send_command(PNPcmd.DNF_TEXT.format(item_line))
                if not resp:
                    raise RuntimeError("Error en items de documento NO fiscal")

                if self.template_config.get("format", {}).get("include_item_comment", False) and item_comment:
                    resp = self.send_command(PNPcmd.DNF_TEXT.format(item_comment))
                    if not resp:
                        raise RuntimeError("Error de comentario en item de documento NO fiscal")
            else:
                tax_value = str(int(float(item_tax) * 100)).zfill(4)
                resp = self.send_command(PNPcmd.ITEM_LINE.format(item_name, item_quantity, item_price, tax_value))
                if not resp:
                    self.send_command(PNPcmd.ITEM_LINE_DEL.format(item_name, item_quantity, item_price, tax_value))
                    raise RuntimeError("Error al procesar ítem fiscal")

                if self.template_config.get("format", {}).get("include_item_comment", False) and item_comment:
                    resp = self.send_command(PNPcmd.COMMENTS.format(item_comment))
                    if not resp:
                        raise RuntimeError(f"Error al procesar comentario fiscal: {item_comment}")

    def _process_footer(self, data: Dict[str, Any]) -> None:
        """Procesa el pie de página."""
        logger.debug("Procesando pie de página")
        delivery_comments = data.get("delivery", {}).get("delivery_comments", [])
        delivery_barcode = data.get("delivery", {}).get("delivery_barcode", "")

        if delivery_comments and self.template_config.get("format", {}).get("include_delivery_comments", False):
            if self._type_doc == "note":
                self.send_command(PNPcmd.DNF_TEXT.format(PNPcmd.INTER_LINE))
            else:
                self.send_command(PNPcmd.COMMENTS.format(PNPcmd.INTER_LINE))

            for comment in delivery_comments:
                line_comment = self._format_text(comment, "comment")
                if self._type_doc == "note":
                    resp = self.send_command(PNPcmd.DNF_TEXT.format(line_comment))
                else:
                    resp = self.send_command(PNPcmd.COMMENTS.format(line_comment))

                if not resp:
                    raise RuntimeError(f"Error al procesar delivery comments: {line_comment}")

        if delivery_barcode and self.template_config.get("format", {}).get("include_delivery_barcode", False):
            if self._type_doc == "note":
                resp = self.send_command(PNPcmd.DNF_TEXT.format(delivery_barcode))
            else:
                resp = self.send_command(PNPcmd.BARCODE.format(delivery_barcode))

            if not resp:
                raise RuntimeError(f"Error al procesar barcode: {delivery_barcode}")

    def _process_payments(self, data: Dict[str, Any]) -> None:
        """Procesa los métodos de pago del documento."""
        logger.debug("Procesando pagos")
        payments = data.get("payments", [])
        total_amount = sum(float(payment.get("payment_amount", 0)) for payment in payments)

        if self._type_doc == "note":
            self.send_command(PNPcmd.DNF_TEXT.format(f"Monto Total: {total_amount}"))
            if not self.send_command(PNPcmd.DNF_CLOSE):
                raise RuntimeError("Error al procesar cierre de documento NO fiscal")
        else:
            if payments:
                mount_base = 0
                mount_igtf = 0
                sorted_payments = sorted(payments, key=lambda x: x["payment_method"], reverse=True)
                for payment in sorted_payments:
                    code = payment["payment_method"]
                    mount_base += payment["payment_amount"] if 1 <= int(code) <= 19 else 0
                    mount_igtf += payment["payment_amount"] if 20 <= int(code) <= 24 else 0

                if mount_igtf > 0:
                    formatted_igtf = self._format_number(mount_igtf, "payment").replace(".", "")
                    if not self.send_command(PNPcmd.CLOSE_PARTIAL_IGTF.format(formatted_igtf)):
                        raise RuntimeError("Error en pago con IGTF")

            time.sleep(1)
            if not self.send_command(PNPcmd.CLOSE_TOTAL):
                raise RuntimeError("Error al cerrar documento fiscal")

    def _process_send_data(self) -> Dict[str, Any]:
        """Obtiene los datos finales después de la impresión."""
        logger.debug("Obteniendo datos de los contadores finales %s", self._type_doc)
        try:
            data = self._printer.get_counters()
            daily_closure = data["ultimo_z"]
            daily_closure = int(daily_closure) + 1

            return {
                "status": True,
                "message": "Impresión finalizada exitosamente",
                "data": {
                    "document_date": data["fecha_formateada"],
                    "document_number": self._last_document,
                    "machine_serial": self._serial,
                    "machine_report": str(daily_closure).zfill(4),
                },
            }

        except Exception as e:
            logger.error("Error al obtener datos fiscales: %s", str(e))
            raise RuntimeError(f"Error al obtener datos fiscales: {str(e)}") from e
