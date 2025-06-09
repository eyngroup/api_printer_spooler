#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright © 2024, Iron Graterol
Licensed under the GNU Affero General Public License, version 3 or later.

Clase para el manejo de la impresora fiscal HKA
"""

import json
import logging
import os
import time
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP, getcontext
from typing import Dict, Any

from controllers.pfhka import FiscalPrinterHka
from printers.printer_base import BasePrinter
from printers.printer_commands import HKAcmd
from handy.tools import get_base_path, normalize_text, normalize_date, normalize_number

# Configuración del logging
logger = logging.getLogger(__name__)

# Constantes para valores de impuestos
TAX_VALUES = {
    "invoice": {0: " ", 12: "!", 16: "!", 8: '"', 22: "#", 31: "#"},
    "credit": {0: "d0", 12: "d1", 16: "d1", 8: "d2", 22: "d3", 31: "d3"},
    "debit": {0: "`0", 12: "`1", 16: "`1", 8: "`2", 22: "`3", 31: "`3"},
    "note": {0: "80", 12: "80", 16: "80", 8: "80", 22: "80", 31: "80"},
}


class TfhkaPrinter(BasePrinter):
    """Clase para manejar la impresión en impresoras fiscales the factory hka"""

    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa la impresora fiscal y establece la conexión
        Args:
            config (dict): Configuración de la impresora
        """
        super().__init__(config)
        self.flag_config = self._load_config("hka_flag_21.json", "config")
        self.max_char_config = self._load_config("hka_max_char.json", "config")
        self.template_config = self._load_config("template_fiscal_printer.json", "templates")
        self.baudrate = config.get("fiscal_baudrate", 9600)
        self.enabled = config.get("fiscal_enabled", False)
        self.printer = config.get("fiscal_name", "pnp")
        self.port = config.get("fiscal_port")
        self.timeout = config.get("fiscal_timeout", 2)
        self._printer = None
        self._model = None  # Modelo de la impresora
        self._serial = None  # Serial de la impresora
        self._flag_21 = None  # Valor del flag 21 para formateo
        self._flag_30 = None  # código de barra con el número asociado bajo él código
        self._flag_43 = None  # Se activa el codigo
        self._flag_50 = None  # Estado de IGTF

        self._initialize_printer()
        if not self.connect():
            raise ConnectionError(f"Error al conectar con la impresora: {self.printer}")

    def _load_config(self, file_name: str, local_path: str) -> dict[str, Any]:
        """
        Carga un archivo de configuración JSON desde el directorio especificado.
        Args:
            filename (str): Nombre del archivo de configuración
            directory (str): Directorio donde se encuentra el archivo
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
        """Crea la instancia del controlador de la impresora TFHKA"""
        try:
            self._printer = FiscalPrinterHka(self.port, self.baudrate, self.timeout)
            logger.info("Impresora TFHKA inicializada")
        except Exception as e:
            logger.error("Error al inicializar la impresora TFHKA: %s", str(e))
            raise

    def _format_number(self, value: float, field_type: str) -> str:
        """
        Formatea un número según el tipo y el flag 21
        Args:
            value: Valor a formatear
            field_type: Tipo ('price', 'quantity', 'discount', 'cancel', 'payment'.)
        Returns:
            str: Valor formateado como entero escalado con ceros a la izquierda
        """
        try:
            getcontext().rounding = ROUND_HALF_UP  # Configurar contexto para redondeo bancario (half-up)
            flag_config = self.flag_config[field_type].get(self._flag_21, (10, 2))  # Fallback
            total_width, decimals = flag_config  # ancho total y decimales desde TABLE_FLAG_21
            scaled_value = Decimal(str(value)) * (10**decimals)  # Convertir a Decimal y escalar
            scaled_value = scaled_value.quantize(Decimal("1"), rounding=ROUND_HALF_UP)

            return f"{int(scaled_value):0{total_width}d}"
        except Exception as e:
            logger.error("Error al formatear número (%s): %s", field_type, str(e))
            raise

    def _format_text(self, text: str, field_type: str) -> str:
        """
        Formatea texto según los límites del modelo
        Args:
            text: Texto a formatear
            field_type: Tipo de campo ('vat', 'partner', 'comment', 'product', 'header', 'footer')
        Returns:
            str: Texto formateado según las especificaciones
        """
        normalized = ""
        try:
            char_config = self.max_char_config.get(self._model, self.max_char_config["SRP_350"])
            max_length = char_config.get(field_type, 37)  # Default 37 si el campo falta
            normalized = normalize_text(text)
            return normalized[:max_length]
        except Exception as e:
            logger.warning("Modelo %s no reconocido. Usando configuración genérica: %s", self._model, str(e))
            return normalized[:37]  # Default 37 si falla

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

                model_info = self._printer.get_sv()  # Obtener modelo de la impresora
                if not model_info:
                    raise RuntimeError("No se pudo obtener el modelo de la impresora")
                self._model = model_info["modelo"]

                serial_info = self._printer.get_s5()  # Obtener serial de la impresora
                if not serial_info:
                    raise RuntimeError("No se pudo obtener el serial de la impresora")
                self._serial = serial_info.get("serial", "Z1B1234567")

                # Actualizar el archivo JSON con el modelo y serial obtenidos
                try:
                    template_path = os.path.join(get_base_path(), "templates", "template_fiscal_printer.json")
                    with open(template_path, "r", encoding="utf-8") as f:
                        template_data = json.load(f)
                    if "fiscal" not in template_data:
                        template_data["fiscal"] = {}
                    template_data["fiscal"]["model"] = self._model
                    template_data["fiscal"]["serial"] = self._serial
                    with open(template_path, "w", encoding="utf-8") as f:
                        json.dump(template_data, f, indent=2, ensure_ascii=False)
                    logger.info("Conexión con impresora modelo: %s, serial: %s", self._model, self._serial)
                except Exception as e:
                    logger.error("No se pudo actualizar template_fiscal_printer.json: %s", str(e))

                flags_info = self._printer.get_s3()  # Obtener flags de la impresora
                if not flags_info:
                    raise RuntimeError("No se pudo obtener los flags de la impresora")
                self._flag_21 = flags_info["flag_21"]
                self._flag_30 = flags_info["flag_30"]
                self._flag_43 = flags_info["flag_43"]
                self._flag_50 = flags_info["flag_50"]
                logger.info("Flag21: %s | Flag50: %s", self._flag_21, self._flag_50)
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
            result = self._printer.send_cmd(command)
            if result:
                logger.info(command)
                if wait_time > 0:
                    time.sleep(wait_time)
            else:
                logger.error("Error al enviar comando: %s", command)
                status = self.get_printer_status()
                logger.error(
                    "Estado: %s %s ",
                    status["status"],
                    status["error"],
                )
                self._printer.send_cmd(HKAcmd.CANCEL)
                logger.info("Comando de cancelación enviado")

            return result
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
            if status["status_code"] != 96 or status["error_code"] != 64:
                logger.error("Estado: %s || Error: %s", status["status"], status["error"])
                self._printer.send_cmd(HKAcmd.CANCEL)
                logger.info("Comando de cancelación enviado")
                return False

            return True
        except Exception as e:
            logger.error("Error al verificar estado de la impresora: %s", str(e))
            return False

    def get_printer_status(self) -> Dict[str, Any]:
        """
        Obtiene el estado detallado de la impresora desde el propio metodo
        Returns:
            Dict[str, Any]: Diccionario con la información del estado
        """
        return self._printer.get_status()

    def report_x(self) -> bool:
        """Imprime reporte X (reporte diario sin cierre)"""
        try:
            result = self.send_command(HKAcmd.DAILY_REPORT)
            time.sleep(3)
            return result
        except Exception as e:
            logger.error("Error al generar reporte X: %s", str(e))
            return False

    def report_z(self) -> bool:
        """Imprime reporte Z (cierre diario)"""
        try:
            result = self.send_command(HKAcmd.DAILY_CLOSE)
            time.sleep(3)
            return result
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
        message_info = f"Estado: {status['status']} | {status['error']}"
        if status["error_code"] in [114, 137]:
            logger.error("Error %s detectado, codigo: %s", status["error"], status["error_code"])
            try:
                from server.handlers.printer_manager import PrinterManager

                PrinterManager.remove_printer("tfhka")
            except Exception as e:
                logger.error("Error al eliminar instancia: %s", str(e))
            return {
                "status": False,
                "message": f"Impresora fiscal {self.printer} en {message_info}, requiere reinicialización",
                "data": {
                    "Estado": status["status_code"],
                    "Error": status["error_code"],
                },
            }

        if status["status_code"] != 96 or status["error_code"] != 64:
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
            self._process_customer_data(data, operation_type)  # Procesar datos del cliente
            self._process_items(data, operation_type)  # Procesar ítems
            self._process_footer(data, operation_type)  # Procesar pie de página
            self._process_payments(data, operation_type)  # Procesar pagos
            return self._process_send_data(operation_type)  # Procesar envio de datos
        except Exception as e:
            message_error = f"Falla durante la impresión del documento de tipo: {operation_type} [{str(e)}]"
            return {"status": False, "message": message_error, "data": None}

    def _process_customer_data(self, data: Dict[str, Any], operation_type: str) -> None:
        """Procesa y envía los datos del cliente a la impresora."""
        logger.debug("Procesando documento")

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
        if operation_type == "credit":
            affected_document = data.get("affected_document", {})
            affected_number = normalize_number(affected_document.get("affected_number", ""))
            affected_date = normalize_date(affected_document.get("affected_date", ""))
            affected_serial = self._format_text(affected_document.get("affected_serial", ""), "comment")

            commands.append(HKAcmd.AFFECTED_NUMBER.format(affected_number))
            commands.append(HKAcmd.AFFECTED_DATE.format(affected_date))
            commands.append(HKAcmd.AFFECTED_SERIAL.format(affected_serial))

        if operation_type in ("credit", "debit", "invoice"):
            commands.append(HKAcmd.PARTNER_VAT.format(customer_vat))
            commands.append(HKAcmd.PARTNER_NAME.format(customer_name))

            if self.template_config.get("format", {}).get("include_partner_address", False):
                commands.append(HKAcmd.PARTNER_ADDRESS.format(customer_address))
            if self.template_config.get("format", {}).get("include_partner_phone", False):
                commands.append(HKAcmd.PARTNER_PHONE.format(customer_phone))
            if self.template_config.get("format", {}).get("include_partner_email", False):
                commands.append(HKAcmd.PARTNER_EMAIL.format(customer_email))
            if self.template_config.get("format", {}).get("include_document_number", False):
                commands.append(HKAcmd.DOCUMENT_NUMBER.format(document_number))
            if self.template_config.get("format", {}).get("include_document_date", False):
                commands.append(HKAcmd.DOCUMENT_DATE.format(document_date))
            if self.template_config.get("format", {}).get("include_document_name", False):
                commands.append(HKAcmd.DOCUMENT_NAME.format(document_name))
            if self.template_config.get("format", {}).get("include_document_cashier", False):
                commands.append(HKAcmd.DOCUMENT_CASHIER.format(document_cashier))

        if operation_type == "note":
            name_note = self.template_config.get("fiscal", {}).get("name_note", "Nota")
            commands.extend(
                [
                    HKAcmd.DNF_OPEN.format(name_note),
                    HKAcmd.DNF_BOLD.format(f"RIF/CI: {customer_vat}"),
                    HKAcmd.DNF_BOLD.format(f"Nombre: {customer_name}"),
                    HKAcmd.DNF_BOLD.format(f"Direccion: {customer_address}"),
                    HKAcmd.DNF_BOLD.format(f"Telefono: {customer_phone}"),
                    HKAcmd.DNF_BOLD.format(f"Email: {customer_email}"),
                    HKAcmd.DNF_BOLD.format(f"Numero: {document_number}"),
                    HKAcmd.DNF_BOLD.format(f"Fecha: {document_date}"),
                    HKAcmd.DNF_BOLD.format(f"Referencia: {document_name}"),
                    HKAcmd.DNF_BOLD.format(f"Vendedor: {document_cashier}"),
                ]
            )

        for cmd in commands:
            if not self.send_command(cmd):
                raise RuntimeError(f"Error al procesar los datos del documento: {cmd}")

    def _process_items(self, data: Dict[str, Any], operation_type: str) -> None:
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

            if operation_type == "note":
                item_tax = item.get("item_tax", 0)
                item_price = item.get("item_price", 0)
                item_quantity = item.get("item_quantity", 0)
                item_line = f"-{item_name} x{item_quantity} x{item_price} Iva:{item_tax}"

                if not self.send_command(HKAcmd.DNF_CENTERED.format(item_line)):
                    raise RuntimeError(f"Error al procesar ítem DNF: {item_line}")

                if self.template_config.get("format", {}).get("include_item_comment", False) and item_comment:
                    if not self.send_command(HKAcmd.DNF_BOLD_CENTERED.format(item_comment)):
                        raise RuntimeError(f"Error al procesar comentario DNF: {item_comment}")
            else:
                item_tax = TAX_VALUES[operation_type].get(item.get("item_tax", 0), "")
                item_price = self._format_number(item.get("item_price", 0), "price")
                item_quantity = self._format_number(item.get("item_quantity", 0), "quantity")
                item_line = HKAcmd.ITEM_LINE.format(item_tax, item_price, item_quantity, item_name)

                if not self.send_command(item_line):
                    raise RuntimeError(f"Error al procesar ítem: {item_line}")

                if item.get("item_discount", 0) > 0:
                    discount = self._format_number(
                        item.get("item_discount", 0),
                        "percentage" if "percentage" in item.get("item_discount_type", "") else "discount",
                    )
                    discount_cmds = {
                        "discount_percentage": HKAcmd.ITEM_DISCOUNT_PERCENTAGE,
                        "surcharge_percentage": HKAcmd.ITEM_SURCHARGE_PERCENTAGE,
                        "discount_amount": HKAcmd.ITEM_DISCOUNT_AMOUNT,
                        "surcharge_amount": HKAcmd.ITEM_SURCHARGE_AMOUNT,
                    }
                    cmd_discount = discount_cmds.get(item.get("item_discount_type", ""))
                    if cmd_discount:
                        cmd = cmd_discount.format(discount)
                        if not self.send_command(cmd):
                            raise RuntimeError(f"Error al procesar descuento: {cmd}")

                if self.template_config.get("format", {}).get("include_item_comment", False) and item_comment:
                    if not self.send_command(HKAcmd.ITEM_COMMENT.format(item_comment)):
                        raise RuntimeError(f"Error al procesar comentario: {item_comment}")

    def _process_footer(self, data: Dict[str, Any], operation_type: str) -> None:
        """Procesa el pie de página."""
        logger.debug("Procesando pie de página")  # revisarlo y compararlo con el de printer_pnp.py

        delivery = data.get("delivery", {})
        delivery_comments = delivery.get("delivery_comments", [])
        delivery_barcode = delivery.get("delivery_barcode", "")

        logger.debug("flag_30: %s", self._flag_30)
        logger.debug("flag_43: %s", self._flag_43)

        if operation_type not in ["note"]:
            if delivery_comments and self.template_config.get("format", {}).get("include_delivery_comments", False):
                item_id = 1
                for comment in delivery_comments:
                    line_comment = self._format_text(comment, "comment")
                    if not self.send_command(HKAcmd.COMMENTS.format(item_id, line_comment)):
                        raise RuntimeError("Error en commando delivery comments")
                    item_id += 1

            if delivery_barcode and self.template_config.get("format", {}).get("include_delivery_barcode", False):
                if not self.send_command(HKAcmd.BARCODE_LINE.format(delivery_barcode)):
                    raise RuntimeError("Error en commando delivery barcode")

    def _process_payments(self, data: Dict[str, Any], operation_type: str) -> None:
        """Procesa los métodos de pago del documento."""
        logger.debug("Procesando pagos")

        payments = data.get("payments", [])
        if operation_type == "note":
            total_amount = sum(payment["payment_amount"] for payment in payments)
            if not self.send_command(HKAcmd.DNF_CLOSE.format(f"Monto Total: {total_amount}")):
                raise RuntimeError("Error en cierre DNF")
        else:
            if self.template_config.get("format", {}).get("include_payment_subtotal", False):
                if not self.send_command(HKAcmd.SUBTOTAL):
                    raise RuntimeError("Error en commando subtotal")

            if not payments:
                if not self.send_command(HKAcmd.PAY_UNIQUE):
                    raise RuntimeError("Error en pago único")
            elif len(payments) == 1:
                code = payments[0]["payment_method"]
                if not self.send_command(HKAcmd.PAY_FULL.format(code)):
                    raise RuntimeError("Error en pago total")
            else:
                sorted_payments = sorted(payments, key=lambda x: x["payment_method"], reverse=True)
                for payment in sorted_payments[:-1]:
                    code = payment["payment_method"]
                    amount = self._format_number(payment["payment_amount"], "payment")
                    if not self.send_command(HKAcmd.PAY_PARTIAL.format(code, amount)):
                        raise RuntimeError("Error en pago parcial")

                code = sorted_payments[-1]["payment_method"]  # Último pago
                if not self.send_command(HKAcmd.PAY_FULL.format(code)):
                    raise RuntimeError("Error en pago final")

            if self._flag_50 == "01":
                if not self.send_command(HKAcmd.IGTF_CLOSE):
                    raise RuntimeError("Error al ejecutar codigo de cierre con IGTF")

    def _process_send_data(self, operation_type: str) -> Dict[str, Any]:
        """Obtiene los datos fiscales finales después de la impresión."""
        logger.debug("Obteniendo datos fiscales finales")

        data = self._printer.get_s1()
        if not data:
            raise RuntimeError("Error al obtener datos fiscales S1")
        try:
            # self._serial
            machine_number = data["registro_maquina"]
            daily_closure = data["contador_cierres_z"]
            daily_closure = int(daily_closure) + 1

            current_date = data["fecha_impresora"]
            date_format = datetime.strptime(current_date, "%d%m%y")
            current_datetime = date_format.strftime("%Y-%m-%d")

            document_counters = {
                "invoice": data["ultima_factura"],
                "credit": data["ultima_nota_credito"],
                "debit": data["ultima_nota_debito"],
                "note": data["ultimo_doc_no_fiscal"],
            }

            last_document = document_counters.get(operation_type, 0)
            return {
                "status": True,
                "message": "Impresión finalizada exitosamente",
                "data": {
                    "document_date": current_datetime,
                    "document_number": str(last_document).zfill(8),
                    "machine_serial": machine_number,
                    "machine_report": str(daily_closure).zfill(4),
                },
            }
        except KeyError as e:
            raise KeyError(f"Campo faltante en datos fiscales: {str(e)}") from e
