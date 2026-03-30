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
from typing import TYPE_CHECKING, Dict, Any

from controllers.pfhka import FiscalPrinterHka
from printers.printer_base import BasePrinter, FiscalPrinterMixin
from printers.printer_commands import HKAcmd

if TYPE_CHECKING:
    from controllers.pfhka import FiscalPrinterHka
from handy.tools import get_base_path, normalize_text, normalize_date, normalize_number, format_multiline

# Configuración del logging
logger = logging.getLogger(__name__)

_SERIAL_FALLBACK = "Z1B1234567"

# Serial de fallback para entorno de pruebas - NO usar en producción

# Constantes para valores de impuestos
TAX_VALUES = {
    "invoice": {0: " ", 12: "!", 16: "!", 8: '"', 22: "#", 31: "#"},
    "credit": {0: "d0", 12: "d1", 16: "d1", 8: "d2", 22: "d3", 31: "d3"},
    "debit": {0: "`0", 12: "`1", 16: "`1", 8: "`2", 22: "`3", 31: "`3"},
    "note": {0: "80", 12: "80", 16: "80", 8: "80", 22: "80", 31: "80"},
}


class TfhkaPrinter(FiscalPrinterMixin, BasePrinter):
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
        self.barcode_rules = self._load_config("hka_barcode_rules.json", "config")
        self.template_config = self._load_config("template_fiscal_printer.json", "templates")
        self.baudrate = config.get("fiscal_baudrate", 9600)
        self.enabled = config.get("fiscal_enabled", False)
        self.printer = config.get("fiscal_name", "pnp")
        self.port = config.get("fiscal_port")
        self.timeout = config.get("fiscal_timeout", 2)
        self.barcode_type = config.get("fiscal_barcode_type", "CODE128")
        self._printer: FiscalPrinterHka = FiscalPrinterHka(self.port, self.baudrate, self.timeout)  # type: ignore[assignment]
        self._model = None  # Modelo de la impresora
        self._serial = None  # Serial de la impresora
        self._flag_21 = None  # Valor del flag 21 para formateo
        self._flag_30 = None  # código de barra con el número asociado bajo él código
        self._flag_43 = None  # Se activa el codigo
        self._flag_50 = None  # Estado de IGTF

        self._initialize_printer()
        if not self.connect():
            raise ConnectionError(f"Error al conectar con la impresora: {self.printer}")

    def _initialize_printer(self) -> None:
        """Crea la instancia del controlador de la impresora TFHKA"""

    def format_status_message(self, status: Dict[str, Any]) -> tuple[str, str]:
        """
        Formatea el mensaje de status para logging/respuesta.
        TFHKA usa keys: 'status' y 'error'.
        Args:
            status: Dict con datos de status de la impresora.
        Returns:
            Tupla (status_message, error_message).
        """
        return (status.get("status", "unknown"), status.get("error", "none"))
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

    def _format_text(self, text: str, field_type: str, truncate: bool = True) -> str:
        """
        Formatea texto según los límites del modelo
        Args:
            text: Texto a formatear
            field_type: Tipo de campo ('vat', 'partner', 'comment', 'product', 'header', 'footer')
            truncate: Si True, trunca el texto al máximo permitido. Para multilínea, pasar False.
        Returns:
            str: Texto formateado según las especificaciones
        """
        normalized = ""
        try:
            default_config = self.max_char_config.get("SRP_350") or {}
            char_config = self.max_char_config.get(self._model) or default_config
            max_length = char_config.get(field_type, 37)  # type: ignore[union-attr]
            normalized = normalize_text(text)
            if truncate:
                return normalized[:max_length]
            return normalized
        except Exception as e:
            logger.warning("Modelo %s no reconocido. Usando configuración genérica: %s", self._model, str(e))
            return normalized[:37] if truncate else normalized

    def _format_barcode(self, text: str) -> str | None:
        """
        Formatea el código de barras según el modelo y el Flag 43
        Args:
            text: Contenido del código de barras
        Returns:
            str | None: Texto formateado o None si no es válido/soportado
        """
        try:
            default_rules = self.barcode_rules.get("SRP_350") or {}
            model_rules = self.barcode_rules.get(self._model) or default_rules
            if not model_rules:
                return None

            flag = str(self._flag_43).zfill(2)
            rule = model_rules.get(flag)  # type: ignore[union-attr]

            if not rule:
                logger.warning("Flag 43 '%s' no soportado o inválido para modelo %s", flag, self._model)
                return None

            limit = rule["limit"]
            is_fixed = rule["fixed"]
            is_numeric = rule["type"] == "numeric"

            processed_text = text
            if is_numeric:
                processed_text = "".join(filter(str.isdigit, text))
                if not processed_text:
                    processed_text = "0"
            # else:
            #     # Para texto, no normalizamos caracteres especiales según solicitud
            #     pass

            if is_fixed:
                processed_text = processed_text.rjust(limit, "0")[-limit:]
            else:
                processed_text = processed_text[:limit]

            return processed_text

        except Exception as e:
            logger.error("Error al formatear código de barras: %s", str(e))
            return None

    def _get_target_flag_43(self) -> str | None:
        """
        Determina el valor del flag 43 basado en el modelo y tipo de barcode deseado.
        Returns: flag value string '00', '01'... or None if not found
        """
        try:
            default_rules = self.barcode_rules.get("SRP_350") or {}
            model_rules = self.barcode_rules.get(self._model) or default_rules
            if not model_rules:
                return None

            # Buscar que flag corresponde al modo deseado (ej: "CODE128")
            for flag, properties in model_rules.items():  # type: ignore[union-attr]
                if properties and properties.get("mode") == self.barcode_type:
                    return flag

            logger.warning("El tipo de barcode '%s' no es soportado por el modelo %s", self.barcode_type, self._model)
            return None
        except Exception:
            return None

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
                self._serial = serial_info.get("serial", _SERIAL_FALLBACK)

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
                logger.debug("Flag43: %s | Flag30: %s", self._flag_43, self._flag_30)

                target_flag = self._get_target_flag_43()
                if target_flag:
                    if self._flag_43 != target_flag:
                        logger.info(
                            "Reprogramando Flag 43: Actual=%s -> Nuevo=%s (%s)",
                            self._flag_43,
                            target_flag,
                            self.barcode_type,
                        )

                        cmd_prog = f"PJ43{target_flag}"
                        if self._printer.send_cmd(cmd_prog):
                            time.sleep(1.0)  # Esperar a que la impresora procese

                            new_flags = self._printer.get_s3()
                            if new_flags:
                                self._flag_43 = new_flags["flag_43"]
                                logger.info("Flag 43 actualizado a: %s", self._flag_43)
                            else:
                                logger.warning("No se pudo verificar el cambio de Flag 43")
                        else:
                            logger.error("Fallo al enviar comando de programación: %s", cmd_prog)

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
            result = bool(result)  # El controlador puede devolver str | bool
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

        operation_type = data.get("operation_type", "").lower()
        try:
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
        # La dirección no se trunca aquí porque se procesa con format_multiline más adelante
        customer_address = self._format_text(customer.get("customer_address", ""), "comment", truncate=False)
        customer_phone = self._format_text(customer.get("customer_phone", ""), "comment")
        customer_email = self._format_text(customer.get("customer_email", ""), "comment")

        document = data.get("document", {})
        document_number = normalize_number(document.get("document_number", ""))
        document_reference = self._format_text(document.get("doc_reference", ""), "comment")
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

            # Asignación dinámica de índices para campos de cliente (i00-i09)
            # El orden de prioridad es: dirección > teléfono > email > documento
            format_config = self.template_config.get("format", {})

            # Obtener máximo de líneas para dirección (default 4)
            max_address_lines = format_config.get("partner_address_lines", 4)

            # Obtener config de caracteres por línea
            default_config = self.max_char_config.get("SRP_350") or {}
            model_config = self.max_char_config.get(self._model) or default_config
            max_chars = model_config.get("comment", 40)

            # Construir lista de campos activos con su contenido y prefijo
            # Cada item: (contenido, prefijo, es_multilinea)
            active_fields = []

            # 1. Dirección (puede ocupar múltiples líneas)
            if format_config.get("include_partner_address", False):
                logger.debug("DEBUG: max_address_lines=%s, max_chars=%s", max_address_lines, max_chars)
                address_chunks = format_multiline(customer_address, max_chars)[:max_address_lines]
                logger.debug("DEBUG: address_chunks length=%s, chunks=%s", len(address_chunks), address_chunks)
                for chunk in address_chunks:
                    active_fields.append((chunk, "", False))

            # 2. Teléfono
            if format_config.get("include_partner_phone", False):
                active_fields.append((f"TEL:{customer_phone}", "", False))

            # 3. Email
            if format_config.get("include_partner_email", False):
                active_fields.append((f"EMAIL:{customer_email}", "", False))

            # 4. Número de documento
            if format_config.get("include_document_number", False):
                active_fields.append((f"NUM:{document_number}", "", False))

            # 5. Referencia de documento
            if format_config.get("include_document_reference", False):
                active_fields.append((f"REF:{document_reference}", "", False))

            # 6. Fecha de documento
            if format_config.get("include_document_date", False):
                active_fields.append((f"FECHA:{document_date}", "", False))

            # 7. Nombre de documento
            if format_config.get("include_document_name", False):
                active_fields.append((f"DOC:{document_name}", "", False))

            # 8. Cajero/Vendedor
            if format_config.get("include_document_cashier", False):
                active_fields.append((f"CAJ:{document_cashier}", "", False))

            # Asignar índices dinámicamente (i00, i01, i02, ...)
            current_index = 0
            for content, _, _ in active_fields:
                if current_index > 9:  # Límite de i00-i09
                    logger.warning(f"Límite de campos de cliente alcanzado (i00-i09). Ignorando: {content[:20]}...")
                    break
                index_str = f"{current_index:02d}"  # Formato: 00, 01, 02, etc.
                commands.append(HKAcmd.PARTNER_ADDRESS.format(index_str, content))
                current_index += 1

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
                    HKAcmd.DNF_BOLD.format(f"Referencia: {document_reference}"),
                    HKAcmd.DNF_BOLD.format(f"Fecha: {document_date}"),
                    HKAcmd.DNF_BOLD.format(f"Documento: {document_name}"),
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
        logger.debug("Procesando pie de página")

        # Línea divisoria antes del footer (línea 0 con guiones)
        separator_line = "-" * 30  # 30 guiones para línea divisoria
        if not self.send_command(HKAcmd.ADDITIONAL_LINES.format("0", separator_line)):
            logger.warning("Error al imprimir línea divisoria del footer")

        # Imprimir exchange rate (línea 9)
        if self.template_config.get("format", {}).get("include_exchange_rate", False):
            operation_metadata = data.get("operation_metadata", {})
            exchange_rate = operation_metadata.get("exchange_rate", 1)
            inverse_rate = operation_metadata.get("inverse_rate", 1)
            if exchange_rate and exchange_rate != 1:
                rate_line = f"TC: {exchange_rate} (Inv: {inverse_rate})"
                if not self.send_command(HKAcmd.ADDITIONAL_LINES.format("9", rate_line)):
                    logger.warning("Error al imprimir exchange rate")

        delivery = data.get("delivery", {})
        delivery_comments = delivery.get("delivery_comments", [])
        delivery_barcode = delivery.get("delivery_barcode", "")

        logger.debug("flag_30: %s", self._flag_30)
        logger.debug("flag_43: %s", self._flag_43)

        if operation_type not in ["note"]:
            # Imprimir email del operador (líneas adicionales antes del barcode)
            if self.template_config.get("format", {}).get("include_operator_mail", False):
                operation_metadata = data.get("operation_metadata", {})
                operator_id = operation_metadata.get("operator_id", "")
                if operator_id:
                    operator_line = self._format_text(operator_id, "comment")
                    # Usar línea adicional i08 para el operador
                    if not self.send_command(HKAcmd.ADDITIONAL_LINES.format("8", operator_line)):
                        raise RuntimeError("Error en comando operator mail")

            if delivery_comments and self.template_config.get("format", {}).get("include_delivery_comments", False):
                item_id = 1
                for comment in delivery_comments:
                    line_comment = self._format_text(comment, "comment")
                    # Usar líneas adicionales i01, i02, etc.
                    if not self.send_command(HKAcmd.ADDITIONAL_LINES.format(str(item_id).zfill(1), line_comment)):
                        raise RuntimeError("Error en commando delivery comments")
                    item_id += 1

            if delivery_barcode and self.template_config.get("format", {}).get("include_delivery_barcode", False):
                formatted_barcode = self._format_barcode(delivery_barcode)

                if formatted_barcode:
                    logger.debug(
                        "Imprimiendo código de barras: %s (Original: %s | Flag 43: %s)",
                        formatted_barcode,
                        delivery_barcode,
                        self._flag_43,
                    )
                    if not self.send_command(HKAcmd.BARCODE_LINE.format(formatted_barcode)):
                        raise RuntimeError("Error en commando delivery barcode")
                else:
                    logger.warning(
                        "Código de barras omitido: Configuración no soportada o error de formato (Flag 43: %s)",
                        self._flag_43,
                    )

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
