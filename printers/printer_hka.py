#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Clase para el manejo de la impresora fiscal HKA"""

import json
import logging
import os
import time
from decimal import Decimal, ROUND_HALF_UP, getcontext
from typing import Dict, Any


import clr
from System.Reflection import Assembly

from printers.printer_base import BasePrinter
from printers.printer_commands import HKAcmd
from utils.tools import get_base_path, normalize_text, normalize_date, normalize_number

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

    # Constantes de error
    ERROR_CONNECTION = "Error al conectar con la impresora: {}"
    ERROR_STATUS = "Error: {} || Estado: {}"

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
        self.timeout = config.get("fiscal_timeout", 3)
        self.dll_path = os.path.join(get_base_path(), "library", "TfhkaNet.dll")
        self._printer = None
        self._model = None  # Modelo de la impresora
        self._serial = None  # Serial de la impresora
        self._flag_21 = None  # Valor del flag 21 para formateo
        self._flag_30 = None  # código de barra con el número asociado bajo él código
        self._flag_43 = None  # Se activa el codigo
        self._flag_50 = None  # Estado de IGTF

        self._initialize_printer()
        if not self.connect():
            raise ConnectionError(self.ERROR_CONNECTION.format(self.port))

    def _load_config(self, file_name: str, local_path: str) -> dict[str, Any]:
        try:
            config_path = os.path.join(get_base_path(), local_path, file_name)
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning("Error cargando configuración %s: %s", file_name, str(e))
            return {}

    def _initialize_printer(self) -> None:
        """Inicializa la conexión con el DLL y crea la instancia de la impresora"""
        try:
            if not os.path.exists(self.dll_path):  # Cargar DLL desde la ruta del sistema
                raise FileNotFoundError(f"El archivo DLL no existe en la ruta: {self.dll_path}")
            Assembly.LoadFrom(self.dll_path)
            clr.AddReference("TfhkaNet")  # pylint: disable=E1101
            from TfhkaNet.IF.VE import Tfhka

            self._printer = Tfhka()
            logger.info("Impresora inicializada: DLL Cargada correctamente")
        except FileNotFoundError as e:
            logger.error("Error de carga: %s", str(e))
            raise
        except Exception as e:
            logger.error("Error al inicializar la impresora: %s", str(e))
            raise

    def connect(self) -> bool:
        """
        Establece la conexión con la impresora
        Returns:
            bool: True si la conexión fue exitosa
        """
        try:
            if self._printer.OpenFpCtrl(self.port) and self.check_status():
                status = self.get_printer_status()
                if status["error_code"] != 0 or status["status_code"] != 4:
                    logger.error(
                        "%s",
                        self.ERROR_STATUS.format(status["error_description"], status["status_description"]),
                    )
                    self._printer.CloseFpCtrl()
                    return False

                logger.info("Conexión establecida con la impresora")

                printer_info = self.get_printer_data("SV")  # Obtener modelo de la impresora
                if not printer_info["status"]:
                    raise RuntimeError("No se pudo obtener información de la impresora")
                self._model = str(printer_info["data"]["model"])

                data_info = self.get_printer_data("S1")  # Obtener serial de la impresora
                if not data_info["status"]:
                    raise RuntimeError("No se pudo obtener datos de la impresora")
                self._serial = str(data_info["data"]["general"]["machine_number"])

                logger.info("Modelo: %s | Serial: %s", self._model, self._serial)

                flags_info = self.get_printer_data("S3")  # Obtener flags
                if not flags_info["status"]:
                    raise RuntimeError("No se pudo obtener configuración de flags")

                flags = flags_info["data"]["flags"]  # Almacenar flags importantes
                self._flag_21 = flags.get("flag_21", "00")
                self._flag_30 = flags.get("flag_30", "00")
                self._flag_43 = flags.get("flag_43", "00")
                self._flag_50 = flags.get("flag_50", "00")
                logger.info(
                    "Flags configurados - Flag21: %s, Flag50: %s",
                    self._flag_21,
                    self._flag_50,
                )
                return True
            logger.error("%s", self.ERROR_CONNECTION.format(self.port))
            return False
        except Exception as e:
            logger.error("%s", self.ERROR_CONNECTION.format(str(e)))
            if hasattr(self._printer, "CloseFpCtrl"):
                self._printer.CloseFpCtrl()
            return False

    def format_number(self, value: float, field_type: str) -> str:
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

    def format_text(self, text: str, field_type: str) -> str:
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

    def disconnect(self) -> None:
        """Desconecta la impresora fiscal"""
        try:
            self._printer.CloseFpCtrl()
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
            result = self._printer.SendCmd(command)
            if result:
                logger.info(command)
                if wait_time > 0:
                    time.sleep(wait_time)
            else:
                logger.error("Error al enviar comando: %s", command)
                status = self.get_printer_status()
                logger.error(
                    "Estado: %s %s ",
                    status["status_description"],
                    status["error_description"],
                )
                self._printer.SendCmd(HKAcmd.CANCEL)

            return result
        except Exception as e:
            logger.error("Error al enviar comando %s: %s", command, str(e))
            return False

    def check_status(self) -> bool:
        """
        Verifica si la impresora está operativa
        Returns:
            bool: True si la impresora esta operativa
        """
        try:
            if not self.enabled or not self._printer.CheckFPrinter():
                return False
            return True
        except Exception as e:
            logger.error("Error al verificar estado: %s", str(e))
            return False

    def get_printer_status(self) -> Dict[str, Any]:
        """
        Obtiene el estado detallado de la impresora
        Returns:
            Dict[str, Any]: Diccionario con la información del estado
        """
        try:
            status = self._printer.GetPrinterStatus()
            return {
                "error_validity": status.ErrorValidity,
                "error_code": status.PrinterErrorCode,
                "error_description": status.PrinterErrorDescription,
                "status_code": status.PrinterStatusCode,
                "status_description": status.PrinterStatusDescription,
            }
        except Exception as e:
            logger.error("Error al obtener estado: %s", str(e))
            raise

    def get_printer_data(self, models: str = "SV") -> Dict[str, Any]:
        """
        Obtiene datos de la impresora según el modelo solicitado
        Args:
            models: Tipo de datos a obtener
                  'SV': Información básica (modelo, país)
                  'S1': Información fiscal y contadores
                  'S2': Estado de documentos en curso
                  'S3': Tasas de impuestos y flags de configuración
        Returns:
            Dict[str, Any]: Diccionario con la información solicitada
        """
        try:
            result = {"status": True, "type": models, "data": {}}

            if models == "SV":  # SV: Modelo de la impresora
                data = self._printer.GetSVPrinterData()
                result["data"] = {
                    "country": data.get_Country(),
                    "model": data.get_Model(),
                }

            elif models == "S1":  # S1: información de parámetros generales de la impresora
                data = self._printer.GetS1PrinterData()
                current_date = data.CurrentPrinterDateTime  # Convertir del DLL a string en formato YYYY-MM-DD
                date_str = f"{current_date.Year:04d}-{current_date.Month:02d}-{current_date.Day:02d}"

                result["data"] = {
                    "general": {
                        "rif": data.get_RIF(),
                        "machine_number": data.get_RegisteredMachineNumber(),
                        "cashier_number": data.get_CashierNumber(),
                        "current_datetime": date_str,
                    },
                    "counters": {
                        "audit_reports": data.get_AuditReportsCounter(),
                        "daily_closure": data.get_DailyClosureCounter(),
                        "last_invoice": data.get_LastInvoiceNumber(),
                        "last_credit_note": data.get_LastCreditNoteNumber(),
                        "last_debit_note": data.get_LastDebitNoteNumber(),
                        "last_non_fiscal_doc": data.get_LastNonFiscalDocNumber(),
                    },
                    "daily_totals": {
                        "sales": data.get_TotalDailySales(),
                        "invoices": data.get_QuantityOfInvoicesToday(),
                        "credit_notes": data.get_QuantityOfCreditNotesToday(),
                        "debit_notes": data.get_QuantityOfDebitNotesToday(),
                        "non_fiscal_docs": data.get_QuantityNonFiscalDocuments(),
                    },
                }
                logger.debug("Datos fiscales obtenidos: %s", result["data"])

            elif models == "S2":  # S2: información general de los montos del documento en curso
                data = self._printer.GetS2PrinterData()
                result["data"] = {
                    "document": {
                        "type": data.get_TypeDocument(),
                        "condition": data.get_Condition(),
                    },
                    "totals": {
                        "amount_payable": data.get_AmountPayable(),
                        "subtotal_bases": data.get_SubTotalBases(),
                        "subtotal_tax": data.get_SubTotalTax(),
                    },
                    "counts": {
                        "articles": data.get_QuantityArticles(),
                        "payments_made": data.get_NumberPaymentsMade(),
                    },
                    "metadata": {"data_dummy": data.get_DataDummy()},
                }
                logger.debug("Datos del documento en curso: %s", result["data"])

            elif models == "S3":  # S3: información de configuración de tasas y flags
                data = self._printer.GetS3PrinterData()
                all_system_flags = data.get_AllSystemFlags()

                flags_to_view = [21, 30, 43, 50, 63]  # flags específicos
                selected_flags = {
                    f"flag_{index:02}": str(flag).zfill(2)
                    for index, flag in enumerate(all_system_flags, start=0)
                    if index in flags_to_view
                }

                result["data"] = {
                    "taxes": {
                        "tax1": {"value": data.get_Tax1(), "type": data.get_TypeTax1()},
                        "tax2": {"value": data.get_Tax2(), "type": data.get_TypeTax2()},
                        "tax3": {"value": data.get_Tax3(), "type": data.get_TypeTax3()},
                        "igtf": {
                            "value": data.get_TaxIGTF(),
                            "type": data.get_TypeTaxIGTF(),
                        },
                    },
                    "flags": selected_flags,
                }
                logger.debug("Configuración de impuestos y flags: %s", result["data"])
            else:
                raise ValueError(f"Modelo de datos no válido: {models}")
            return result

        except Exception as e:
            logger.error("Error al obtener los datos de la impresora: %s", str(e))
            return {
                "status": False,
                "message": f"Error al obtener los datos de la impresora: {str(e)}",
            }

    def report_x(self) -> bool:
        """Imprime reporte X (reporte diario sin cierre)"""
        try:
            return self.send_command(HKAcmd.DAILY_REPORT)
        except Exception as e:
            logger.error("Error al generar reporte X: %s", str(e))
            return False

    def report_z(self) -> bool:
        """Imprime reporte Z (cierre diario)"""
        try:
            return self.send_command(HKAcmd.DAILY_CLOSE)
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
        if not self.check_status():
            logger.error("Impresora %s deshabilitada o desconectada", self.printer)
            return {
                "status": False,
                "message": f"Impresora fiscal {self.printer} deshabilitada o desconectada",
                "data": None,
            }

        try:
            operation_type = data.get("operation_type", "").lower()
            status = self.get_printer_status()
            message = f"Estado: {status['error_description']} | {status['status_description']}"

            if operation_type not in ("credit", "debit", "invoice", "note"):
                return {
                    "status": False,
                    "message": f"Tipo de documento no válido: {operation_type}",
                    "data": None,
                }

            if status["error_code"] != 0 or status["status_code"] != 4:
                message_return = "Impresora fiscal en estado inoperativo"

                if status["status_code"] == 5:
                    self._printer.SendCmd(HKAcmd.CANCEL)
                    message_return = "Documento fiscal anulado"

                logger.error(message)
                data = {
                    "Estado": status["status_description"],
                    "Error": status["error_description"],
                }
                return {"status": False, "message": message_return, "data": data}
            logger.info(message)

            self._process_customer_data(data, operation_type)  # Procesar datos del cliente
            self._process_items(data, operation_type)  # Procesar ítems
            self._process_footer(data, operation_type)  # Procesar pie de página
            self._process_payments(data, operation_type)  # Procesar pagos
            return self._process_send_data(operation_type)  # Procesar envio de datos
        except Exception as e:
            message = f"Error durante la impresión del documento fiscal: {str(e)}"
            logger.error(message)
            return {"status": False, "message": message, "data": None}

    def _process_customer_data(self, data: Dict[str, Any], operation_type: str) -> None:
        """Procesa y envía los datos del cliente a la impresora."""
        logger.debug("Procesando documento")

        customer = data.get("customer", {})
        customer_vat = self.format_text(customer.get("customer_vat", ""), "vat")
        customer_name = self.format_text(customer.get("customer_name", ""), "partner")
        customer_address = self.format_text(customer.get("customer_address", ""), "comment")
        customer_phone = self.format_text(customer.get("customer_phone", ""), "comment")
        customer_email = self.format_text(customer.get("customer_email", ""), "comment")

        document = data.get("document", {})
        document_number = normalize_number(document.get("document_number", ""))
        document_date = normalize_date(document.get("document_date", ""))
        document_name = self.format_text(document.get("document_name", ""), "comment")
        document_cashier = self.format_text(document.get("document_cashier", ""), "comment")

        commands = []
        if operation_type == "credit":
            affected_document = data.get("affected_document", {})
            affected_number = normalize_number(affected_document.get("affected_number", ""))
            affected_date = normalize_date(affected_document.get("affected_date", ""))
            affected_serial = self.format_text(affected_document.get("affected_serial", ""), "comment")

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
            item_comment = self.format_text(item.get("item_comment", ""), "comment")
            if self.template_config.get("format", {}).get("include_item_reference", False):
                item_code = item.get("item_ref", "")
                item_product = item.get("item_name", "")
                item_name = self.format_text(f"[{item_code}] {item_product}", "product")
            else:
                item_name = self.format_text(item.get("item_name", ""), "product")

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
                item_price = self.format_number(item.get("item_price", 0), "price")
                item_quantity = self.format_number(item.get("item_quantity", 0), "quantity")
                item_line = HKAcmd.ITEM_LINE.format(item_tax, item_price, item_quantity, item_name)

                if not self.send_command(item_line):
                    raise RuntimeError(f"Error al procesar ítem: {item_line}")

                if item.get("item_discount", 0) > 0:
                    discount = self.format_number(
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
                    amount = self.format_number(payment["payment_amount"], "payment")
                    if not self.send_command(HKAcmd.PAY_PARTIAL.format(code, amount)):
                        raise RuntimeError("Error en pago parcial")

                code = sorted_payments[-1]["payment_method"]  # Último pago
                if not self.send_command(HKAcmd.PAY_FULL.format(code)):
                    raise RuntimeError("Error en pago final")

            if self._flag_50 == "01":
                if not self.send_command(HKAcmd.IGTF_CLOSE):
                    raise RuntimeError("Error al ejecutar codigo de cierre con IGTF")

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
                    line_comment = self.format_text(comment, "comment")
                    if not self.send_command(HKAcmd.COMMENTS.format(item_id, line_comment)):
                        raise RuntimeError("Error en commando delivery comments")
                    item_id += 1

            if delivery_barcode and self.template_config.get("format", {}).get("include_delivery_barcode", False):
                if not self.send_command(HKAcmd.BARCODE_LINE.format(delivery_barcode)):
                    raise RuntimeError("Error en commando delivery barcode")

    def _process_send_data(self, operation_type: str) -> Dict[str, Any]:
        """Obtiene los datos fiscales finales después de la impresión."""
        logger.debug("Obteniendo datos fiscales finales")

        data = self.get_printer_data("S1")
        if not data["status"]:
            raise RuntimeError(f"Error al obtener datos fiscales: {data.get('message', 'Sin detalles')}")
        try:
            machine_number = data["data"]["general"]["machine_number"]
            daily_closure_counter = data["data"]["counters"]["daily_closure"]
            current_datetime = data["data"]["general"]["current_datetime"]

            document_counters = {
                "invoice": data["data"]["counters"]["last_invoice"],
                "credit": data["data"]["counters"]["last_credit_note"],
                "debit": data["data"]["counters"]["last_debit_note"],
                "note": data["data"]["counters"]["last_non_fiscal_doc"],
            }

            last_document = document_counters.get(operation_type, 0)
            return {
                "status": True,
                "message": "Impresión finalizada exitosamente",
                "data": {
                    "document_date": current_datetime,
                    "document_number": str(last_document).zfill(8),
                    "machine_serial": machine_number,
                    "machine_report": str(daily_closure_counter).zfill(4),
                },
            }
        except KeyError as e:
            raise KeyError(f"Campo faltante en datos fiscales: {str(e)}") from e
