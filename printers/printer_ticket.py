#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright © 2024, Iron Graterol
Licensed under the GNU Affero General Public License, version 3 or later.

Clase para una impresora de tickets.
"""

import json
import logging
import os
from datetime import datetime
from typing import Dict, Any, List
from PIL import Image

import sys
import subprocess

if sys.platform == "win32":
    import win32print
from handy.tools import get_base_path, normalize_text, format_multiline

from .printer_base import BasePrinter
from .printer_commands import ESCPOScmd
from .printer_counter import FiscalCounter

logger = logging.getLogger(__name__)


class TicketPrinter(BasePrinter):
    """Clase para manejar la impresión de tickets"""

    STATUS_KEYS_ONLINE = frozenset({"enabled", "idle", "printing"})

    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa la impresora de tickets
        Args:
            config (dict): Configuración de la impresora
        """
        super().__init__(config)
        self.printer_name = config.get("ticket_port")
        self.template_name = config.get("ticket_template", "template_ticket_simple.json")
        self.direct_print = config.get("ticket_direct", True)
        default_output = os.path.join(get_base_path(), "docs", "ticket_output.txt")
        self.output_file = config.get("ticket_file", default_output)
        self.printer_handle = None
        self.connected = False

        use_escpos = config.get("ticket_use_escpos", True)  # Inicializar comandos ESC/POS
        self.escpos_commands = ESCPOScmd(use_escpos)

        self._load_template()  # Inicializar contador usando el template
        template_path = os.path.join(get_base_path(), "templates", self.template_name)
        self.counter = FiscalCounter(template_path)

    def connect(self) -> bool:
        """Conecta con la impresora"""
        try:
            if sys.platform == "win32":
                self.printer_handle = win32print.OpenPrinter(self.printer_name)

                printer_info = win32print.GetPrinter(self.printer_handle, 2)
                if printer_info["Status"] != 0:  # 0 significa "Ready"
                    logger.error("Impresora no lista. Estado: %s", printer_info["Status"])
                    self.disconnect()
                    return False
            else:
                # Linux: Verificar si la impresora existe en CUPS
                # Usamos lpstat -p printer_name para verificar
                cmd = ["lpstat", "-p", self.printer_name]
                subprocess.check_output(cmd, stderr=subprocess.STDOUT)

            self.connected = True
            logger.info("Conectado a impresora: %s", self.printer_name)
            return True
        except Exception as e:
            logger.error("Error conectando a impresora %s : %s", self.printer_name, str(e))
            self.connected = False
            if sys.platform == "win32" and self.printer_handle:
                self.disconnect()
            return False

    def disconnect(self) -> None:
        """Desconecta la impresora"""
        try:
            if sys.platform == "win32":
                if self.printer_handle:
                    win32print.ClosePrinter(self.printer_handle)
                self.printer_handle = None

            self.connected = False
            logger.info("Impresora desconectada")
        except Exception as e:
            logger.error("Error desconectando impresora: %s", str(e))

    def print_document(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Imprime un documento
        Args:
            document: Datos del documento a imprimir
        Returns:
            dict: Resultado de la impresión
        """
        if not self.config["ticket_enabled"]:
            return {
                "status": False,
                "message": "Impresora de tickets deshabilitada en configuración",
                "data": None,
            }

        try:
            if not self.connect():
                return {
                    "status": False,
                    "message": f"No se pudo conectar a la impresora {self.printer_name}",
                    "data": None,
                }

            fiscal_data = self.counter.update_counter(data.get("operation_type", "invoice"))

            if self.config.get("logo_enabled", False) and self.escpos_commands.use_escpos:
                self._print_logo_direct()

            document_content = self._generate_document_content(data)

            if self.direct_print:
                try:
                    if sys.platform == "win32":
                        doc_info = ("Ticket", None, "RAW")  # (nombre_doc, nombre_output, tipo_datos)
                        win32print.StartDocPrinter(self.printer_handle, 1, doc_info)
                        win32print.StartPagePrinter(self.printer_handle)  # Inicia
                        win32print.WritePrinter(self.printer_handle, document_content.encode("utf-8"))  # Envía
                        win32print.EndPagePrinter(self.printer_handle)  # Finaliza
                        win32print.EndDocPrinter(self.printer_handle)  # Finaliza
                    else:
                        # Linux: Usar lpr para enviar raw
                        cmd = ["lpr", "-P", self.printer_name, "-o", "raw"]
                        process = subprocess.Popen(
                            cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                        )
                        stdout, stderr = process.communicate(input=document_content.encode("utf-8"))

                        if process.returncode != 0:
                            raise Exception(f"lpr error: {stderr.decode()}")

                finally:
                    self.disconnect()

                return {
                    "status": True,
                    "message": "Documento enviado a imprimir correctamente",
                    "data": fiscal_data,
                }

            try:
                os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
                with open(self.output_file, "w", encoding="utf-8") as f:
                    f.write(document_content)  # Escribir

                logger.info("Documento guardado en: %s", self.output_file)
                return {
                    "status": True,
                    "message": f"Documento guardado en archivo: {self.output_file}",
                    "data": fiscal_data,
                }
            except Exception as e:
                error_msg = f"Error guardando archivo: {str(e)}"
                logger.error(error_msg)
                return {"status": False, "message": error_msg, "data": None}

        except Exception as e:
            logger.error("Error imprimiendo documento: %s", str(e), exc_info=True)
            return {
                "status": False,
                "message": f"Error imprimiendo documento: {str(e)}",
                "data": None,
            }

    def check_status(self) -> Dict[str, Any]:
        """
        Verifica el estado de la impresora
        Returns:
            Dict[str, Any]: Estado de la impresora
        """
        try:
            if not self.is_connected:
                self.connect()

            if sys.platform == "win32":
                printer_info = win32print.GetPrinter(self.printer_handle, 2)
                status = printer_info["Status"]
                return {
                    "online": status == 0,  # 0 = Ready
                    "paper": not (status & win32print.PRINTER_STATUS_PAPER_OUT),
                    "error": None if status == 0 else f"Printer status: {status}",
                }
            else:
                # Linux: Usar lpstat
                cmd = ["lpstat", "-p", self.printer_name]
                output = subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode()
                # lpstat salida ejemplo: "printer EPSON_TM_T20II is idle. enabled since..."
                if any(key in output for key in self.STATUS_KEYS_ONLINE):
                    return {
                        "online": True,
                        "paper": True,  # Dificil de saber con lpr estandard sin drivers especificos
                        "error": None,
                    }
                else:
                    return {"online": False, "paper": False, "error": output.strip()}

        except Exception as e:
            logger.error("Error verificando estado de impresora: %s", str(e))
            return {"online": False, "paper": False, "error": str(e)}

    def _process_logo(self) -> bytes:
        """Procesa el logo y retorna los bytes listos para imprimir"""
        try:
            logo = Image.open("resources/logo.bmp")
            if not logo:
                logger.error("Imagen de logo no encontrada")
                return b""  # Si la imagen no existe, retornar bytes vacíos
            width = self.config.get("logo_width", 480)
            height = self.config.get("logo_height", 160)

            img_ratio = logo.width / logo.height
            target_ratio = width / height  # Redimensionar manteniendo el aspecto

            if img_ratio > target_ratio:
                new_width = width
                new_height = int(width / img_ratio)
            else:
                new_height = height
                new_width = int(height * img_ratio)

            x_offset = (width - new_width) // 2
            y_offset = (height - new_height) // 2

            logo = logo.resize((new_width, new_height), Image.Resampling.BICUBIC)
            if logo.mode != "1":
                logo = logo.convert("1")  # Redimensionar y convertir a 1-bit

            matrix = [[0 for _ in range(width)] for _ in range(height)]

            for y in range(height):
                for x in range(width):
                    if x_offset <= x < x_offset + new_width and y_offset <= y < y_offset + new_height:
                        img_x = x - x_offset
                        img_y = y - y_offset
                        pixel = logo.getpixel((img_x, img_y))
                        matrix[y][x] = 0 if pixel else 1

            bytes_per_line = (width + 7) // 8
            command = bytearray(
                [
                    0x1B,
                    0x61,
                    0x01,  # Centrar
                    0x1D,
                    0x76,
                    0x30,
                    0x00,  # GS v 0 0 (comando de impresión raster)
                    bytes_per_line & 0xFF,  # xL (ancho en bytes, LSB)
                    (bytes_per_line >> 8) & 0xFF,  # xH (ancho en bytes, MSB)
                    height & 0xFF,  # yL (alto en píxeles, LSB)
                    (height >> 8) & 0xFF,  # yH (alto en píxeles, MSB)
                ]
            )

            data = bytearray()
            for y in range(height):
                for byte_pos in range(bytes_per_line):
                    byte = 0
                    for bit in range(8):
                        x = byte_pos * 8 + bit
                        if x < width and matrix[y][x]:
                            byte |= 0x80 >> bit
                    data.append(byte)

            return bytes(command) + bytes(data) + b"\n"

        except Exception:
            return b""  # Si hay error al procesar el logo, retornar bytes vacíos

    def _print_logo_direct(self) -> None:
        """Imprime el logo directamente"""
        try:
            logo_bytes = self._process_logo()
            if not logo_bytes:
                return

            if sys.platform == "win32":
                doc_info = ("Logo", None, "RAW")
                win32print.StartDocPrinter(self.printer_handle, 1, doc_info)
                win32print.StartPagePrinter(self.printer_handle)
                win32print.WritePrinter(self.printer_handle, logo_bytes)
                win32print.EndPagePrinter(self.printer_handle)
                win32print.EndDocPrinter(self.printer_handle)
            else:
                # Linux
                cmd = ["lpr", "-P", self.printer_name, "-o", "raw"]
                process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = process.communicate(input=logo_bytes)
                if process.returncode != 0:
                    logger.error("Error imprimiendo logo (Linux): %s", stderr.decode())
        except Exception as e:
            logger.error("Error imprimiendo logo: %s", str(e))

    def _format_header(self) -> List[str]:
        """
        Formatea el encabezado del ticket
        Args:
            data: Datos del documento
        Returns:
            List[str]: Líneas del encabezado
        """
        header = []

        header.extend(
            [
                self.escpos_commands.CMD_ALIGN_CENTER,
                self.escpos_commands.CMD_BOLD_ON,
                f"{self.template['header']['title']}\n",
                self.escpos_commands.CMD_BOLD_OFF,
                f"{self.template['header']['subtitle']}\n",
            ]
        )  # Título y subtítulo centrados

        # Datos de empresa, dirección y teléfono con márgenes
        width = self.template["format"]["width"]
        free_space = self.template["format"]["width_free_space"]
        max_text_width = max(
            width - free_space, free_space
        )  # Dejar espacio libre a los lados (aprox 10 caracteres por lado)

        for field in ["company", "address", "phone"]:
            text = self.template["header"].get(field, "").replace("\n", " ").strip()
            if text:
                # Usar textwrap/format_multiline para separar el texto sin necesidad de \n manuales
                lines = format_multiline(text, max_text_width)
                for line in lines:
                    header.append(f"{line}\n")

        return header

    def _format_sub_header(self, data: Dict[str, Any]) -> List[str]:
        """
        Formatea el sub-encabezado del ticket (tipo documento, número, fecha)
        Args:
            data: Datos del documento
        Returns:
            List[str]: Líneas del sub-encabezado
        """
        sub_header = []
        width = self.template["format"]["width"]
        document_mapping = {
            "invoice": "FACTURA",
            "credit": "NOTA DE CREDITO",
            "debit": "NOTA DE DEBITO",
            "note": "NOTA DE ENTREGA",
        }  # Valores de document_type

        header_type = self.template["header"]["type"]  # Formatear tipo de documento
        document_type = (
            document_mapping.get(data["operation_type"], "NOTA DE DESPACHO") if header_type == "*" else header_type
        )

        sub_header.extend(
            [
                self.escpos_commands.CMD_ALIGN_CENTER,
                self.escpos_commands.CMD_BOLD_ON,
                f"{document_type}\n",
                self.escpos_commands.CMD_BOLD_OFF,
            ]
        )  # Tipo de documento centrado

        # Tipos de documento a contadores
        counter_mapping = {
            "invoice": "document_invoice",
            "credit": "document_credit",
            "debit": "document_debit",
            "note": "document_note",
        }

        counter_key = counter_mapping.get(data.get("operation_type", "invoice"), "document_invoice")
        document_number = int(self.template["counter"][counter_key])
        document_number += 1
        doc_number = str(document_number).zfill(8)

        sub_header.extend(
            [
                self.escpos_commands.CMD_ALIGN_LEFT,
                self._format_line_justified(f"{self.template['header']['name']}", doc_number, width) + "\n",
            ]
        )  # Alinear documento y fecha/hora

        if self.template["format"].get("show_document_date", True):
            date_parts = data["document"]["document_date"].split("-")  # Formatear fecha DD-MM-AAAA
            formatted_date = f"FECHA: {date_parts[2]}-{date_parts[1]}-{date_parts[0]}"
            current_time = f"HORA: {datetime.now().strftime('%H:%M')}"
            sub_header.append(self._format_line_justified(formatted_date, current_time, width) + "\n")

        sub_header.append(f"{self.template['format']['separator'] * width}\n")
        if self.template["format"]["show_items_header"]:
            sub_header.extend(
                [
                    self.escpos_commands.CMD_ALIGN_CENTER,
                    self.escpos_commands.CMD_BOLD_ON,
                    "CANT  DESCRIPCION           PRECIO   TOTAL\n",
                    self.escpos_commands.CMD_BOLD_OFF,
                    f"{self.template['format']['separator'] * width}\n",
                ]
            )
        return sub_header

    def _format_customer_info(self, data: Dict[str, Any]) -> List[str]:
        """
        Formatea la información del cliente
        Args:
            data: Datos del documento
        Returns:
            List[str]: Líneas de información del cliente
        """
        customer = []
        width = self.template["format"]["width"]
        customer.append(self.escpos_commands.CMD_ALIGN_LEFT)
        customer_vat = data["customer"]["customer_vat"]
        customer_name = data["customer"]["customer_name"]
        customer.extend([f"RIF/C.I.: {customer_vat}\n", f"RAZON SOCIAL: {customer_name}\n"])

        if data["customer"].get("customer_address") and self.template["format"]["show_customer_address"]:
            address_format = normalize_text(f"DIR: {data['customer']['customer_address']}")
            address_lines = format_multiline(address_format, width)
            for line in address_lines:
                customer.append(f"{line}\n")

        if data["customer"].get("customer_phone") and self.template["format"]["show_customer_phone"]:
            customer.append(f"TEL: {data['customer']['customer_phone']}\n")

        if data["customer"].get("customer_email") and self.template["format"].get("show_customer_email", False):
            customer.append(f"EMAIL: {data['customer']['customer_email']}\n")

        if data["document"].get("document_number") and self.template["format"]["show_document_number"]:
            customer.append(f"NUM: {data['document']['document_number']}\n")

        if data["document"].get("doc_reference") and self.template["format"].get("show_document_reference", False):
            customer.append(f"REF: {data['document']['doc_reference']}\n")

        if data["document"].get("document_name") and self.template["format"]["show_document_name"]:
            customer.append(f"DOC: {data['document']['document_name']}\n")

        if self.template["format"].get("show_document_cashier", False) and data["document"].get("document_cashier"):
            normalized_cashier = normalize_text(data["document"]["document_cashier"])
            customer.append(f"CAJ: {normalized_cashier}\n")

        return customer

    def _format_items(self, data: Dict[str, Any]) -> List[str]:
        """
        Formatea los items del ticket
        Args:
            data: Datos del documento
        Returns:
            List[str]: Líneas de items
        """
        items = []
        width = self.template["format"]["width"]
        subtotal = 0.0

        currency_code = data.get("operation_metadata", {}).get("currency_code", "VEF")
        symbol = "USD" if currency_code == "USD" else "Bs"

        for item in data["items"]:  # Procesar cada item
            quantity = item.get("item_quantity", 1)
            price = item.get("item_price", 0.0)
            total = quantity * price  # Calcular valores
            tax_rate = item.get("item_tax", 0)

            subtotal += total  # Acumular subtotal

            if quantity > 1:  # Si es más de 1 item, mostrar cantidad y precio unitario
                items.append(f"{quantity}x{symbol} {price:.2f}\n")

            item_name = normalize_text(item.get("item_name", ""))
            if self.template["format"].get("combine_item_ref", False) and item.get("item_ref"):
                item_name = f"{item['item_ref']} {item_name}"

            tax_indicator = self._get_tax_indicator(tax_rate)  # Agregar indicador de impuesto
            if tax_indicator:
                item_name = f"{item_name} {tax_indicator}"

            right_text = f"{symbol} {total:.2f}"

            # Asegurar que haya suficiente espacio para el total
            item_width = self.template["format"].get("width_item_description", 15)
            reserved_space = max(item_width, len(right_text) + 1)

            max_name_len = width - reserved_space

            # Separamos el nombre en múltiples líneas
            name_lines = format_multiline(item_name, max_name_len) if item_name else [""]

            for i, line in enumerate(name_lines):
                if i == len(name_lines) - 1:
                    # El total se imprime en la última línea del producto
                    items.append(self._format_line_justified(line, right_text, width) + "\n")
                else:
                    # Líneas superiores solo con el texto descriptivo
                    items.append(line + "\n")

        if self.template["format"].get("show_subtotal", True):
            items.append(f"{self.template['format']['separator'] * width}\n")
            items.append(self._format_line_justified("SUBTOTAL:", f"{symbol} {subtotal:.2f}", width) + "\n")
        items.append(f"{self.template['format']['separator'] * width}\n")

        return items

    def _get_tax_indicator(self, tax_rate: float) -> str:
        """
        Obtiene el indicador de impuesto según la tasa
        Args:
            tax_rate: Tasa de impuesto
        Returns:
            str: Indicador de impuesto (G, R, E, S)
        """
        tax_indicators = {0: "(E)", 8: "(R)", 16: "(G)", 31: "(A)"}
        return tax_indicators.get(tax_rate, "")

    def _format_totals(self, data: Dict[str, Any]) -> List[str]:
        """
        Formatea los totales del ticket
        Args:
            data: Datos del documento
        Returns:
            List[str]: Líneas de totales
        """
        totals = []
        width = self.template["format"]["width"]

        currency_code = data.get("operation_metadata", {}).get("currency_code", "VEF")
        symbol = "USD" if currency_code == "USD" else "Bs"

        # Inicializar diccionarios para agrupar bases e impuestos
        tax_bases = {0: 0, 16: 0, 8: 0, 31: 0}
        tax_amounts = {0: 0, 16: 0, 8: 0, 31: 0}

        for item in data["items"]:  # Calcular bases e impuestos por tasa
            price = item.get("item_price", 0.0)
            quantity = item.get("item_quantity", 1)
            tax_rate = item.get("item_tax", 0)

            amount = price * quantity
            tax_bases[tax_rate] += amount
            if tax_rate > 0:
                tax_amounts[tax_rate] += amount * (tax_rate / 100)

        if tax_bases[0] > 0:  # Mostrar exentos si hay
            totals.append(self._format_line_justified("EXENTO", f"{symbol} {tax_bases[0]:.2f}", width) + "\n")

        tax_labels = {16: ("G", "16,00"), 8: ("R", "8,00"), 31: ("A", "31,00")}

        for rate, (letter, rate_str) in tax_labels.items():
            if tax_bases[rate] > 0:
                totals.append(
                    self._format_line_justified(f"BI {letter} ({rate_str}%)", f"{symbol} {tax_bases[rate]:.2f}", width)
                    + "\n"
                )  # Base imponible

                totals.append(
                    self._format_line_justified(
                        f"IVA {letter} ({rate_str}%)",
                        f"{symbol} {tax_amounts[rate]:.2f}",
                        width,
                    )
                    + "\n"
                )  # IVA

        totals.append(f"{self.template['format']['separator'] * width}\n")
        total = sum(tax_bases.values()) + sum(tax_amounts.values())
        totals.append(self._format_line_justified("TOTAL:", f"{symbol} {total:.2f}", width) + "\n\n")

        if data.get("payments"):  # Formas de pago
            for payment in data["payments"]:
                totals.append(
                    self._format_line_justified(
                        payment["payment_name"],
                        f"{symbol} {payment['payment_amount']:.2f}",
                        width,
                    )
                    + "\n"
                )
            totals.append("\n")

        return totals

    def _format_footer(self, data: Dict[str, Any]) -> List[str]:
        """
        Formatea el pie de página del ticket
        Args:
            data: Datos del documento
        Returns:
            List[str]: Líneas del pie de página
        """
        footer = []
        if self.template["format"].get("show_delivery_comments", True) and data.get("delivery", {}).get(
            "delivery_comments"
        ):
            for comment in data["delivery"]["delivery_comments"]:
                comment_format = normalize_text(comment)
                footer.append(f"{comment_format}\n")

        if data.get("delivery", {}).get("delivery_barcode") and self.config.get("barcode_enabled", False):
            footer.extend(["\n", self.escpos_commands.CMD_ALIGN_CENTER])

            if self.config.get("barcode_type") == "qr":
                footer.extend(self._get_qr_commands(data["delivery"]["delivery_barcode"]))
            else:
                footer.extend(
                    [
                        self.escpos_commands.CMD_BARCODE_TXT_BLW,  # Imprimir texto debajo del código
                        self.escpos_commands.command(
                            "\x1d\x77\x02"
                        ),  # Ancho 2 (es un poco más angosto/condensado que 3)
                        self.escpos_commands.CMD_BARCODE_HEIGHT,
                        self.escpos_commands.CMD_BARCODE_CODE128,
                        chr(len(data["delivery"]["delivery_barcode"])),  # Length
                        data["delivery"]["delivery_barcode"],  # Data
                    ]
                )

            footer.append("\n")

        footer.extend(
            [
                "\n",
                self.escpos_commands.CMD_ALIGN_CENTER,
                f"{self.template['footer']['message']}\n",
                f"{self.template['footer']['legal']}\n",
            ]
        )

        return footer

    def _get_qr_commands(self, data: str) -> List[str]:
        """
        Genera los comandos ESC/POS para el código QR según la configuración del template
        Args:
            data: Datos a codificar en QR
        Returns:
            List[str]: Lista de comandos ESC/POS
        """
        qr_config = self.template["format"].get("qr", {})
        size = qr_config.get("size", 6)  # Default: 6
        model = qr_config.get("model", 1)  # Default: 1

        error_levels = {
            "L": "\x30",  # 7%
            "M": "\x31",  # 15%
            "Q": "\x32",  # 25%
            "H": "\x33",  # 30%
        }  # Nivel de error a código ESC/POS
        error_level = error_levels.get(qr_config.get("error_level", "M"), "\x31")

        qr_length = len(data) + 3
        qr_length_low = qr_length & 0xFF
        qr_length_high = (qr_length >> 8) & 0xFF  # Calcular longitud de datos

        return [
            f"\x1d\x28\x6b\x04\x00\x31\x41{chr(model - 1)}\x00",  # Seleccionar modelo QR
            f"\x1d\x28\x6b\x03\x00\x31\x43{chr(size)}",  # Establecer tamaño
            f"\x1d\x28\x6b\x03\x00\x31\x45{error_level}",  # Establecer nivel de corrección de errores
            f"\x1d\x28\x6b{chr(qr_length_low)}{chr(qr_length_high)}\x31\x50\x30{data}",  # Almacenar datos
            "\x1d\x28\x6b\x03\x00\x31\x51\x30",  # Imprimir QR
        ]

    def _generate_document_content(self, data: Dict[str, Any]) -> str:
        """
        Genera el contenido del documento según el template
        Args:
            data: Datos del documento
        Returns:
            str: Contenido formateado con comandos ESC/POS
        """
        content = []
        font_choice = self.template.get("format", {}).get("font", "A").upper()
        font_cmd = self.escpos_commands.CMD_FONT_A
        if font_choice == "B":
            font_cmd = self.escpos_commands.CMD_FONT_B
        elif font_choice == "C":
            # Some printers support Font C with \x1b\x4d\x02, we can fallback to B or use raw command
            font_cmd = self.escpos_commands.command("\x1b\x4d\x02")

        content.extend(
            [
                self.escpos_commands.CMD_INIT,
                self.escpos_commands.CMD_CHARSET,
                font_cmd,
                self.escpos_commands.CMD_FONT_NORMAL,
            ]
        )

        content.extend(self._format_header())  # Encabezado
        content.extend(self._format_customer_info(data))  # Datos del cliente
        content.extend(self._format_sub_header(data))  # Sub-encabezado
        content.extend(self._format_items(data))  # Items
        content.extend(self._format_totals(data))  # Totales
        content.extend(self._format_footer(data))  # Pie de página

        content.extend(
            [
                self.escpos_commands.CMD_FEED,
                self.escpos_commands.CMD_CUT,
            ]
        )

        return "".join(content)

    def _load_template(self) -> None:
        """Carga la plantilla de impresión"""
        try:
            template_path = os.path.join(get_base_path(), "templates", self.template_name)
            with open(template_path, "r", encoding="utf-8") as f:
                self.template = json.load(f)
            logger.info("Template cargado: %s", self.template_name)
        except Exception as e:
            logger.error("Error cargando template: %s", str(e))
            raise

    def _align_text(self, text: str, width: int, align: str = "left") -> str:
        """
        Alinea el texto según el ancho especificado
        Args:
            text: Texto a alinear
            width: Ancho total disponible
            align: Tipo de alineación ('left', 'right', 'center')
        Returns:
            str: Texto alineado
        """
        if align == "right":
            return text.rjust(width)
        if align == "left":
            return text.ljust(width)
        return text.center(width)

    def _format_line_justified(self, left_text: str, right_text: str, width: int) -> str:
        """
        Formatea una línea con texto justificado a ambos lados
        Args:
            left_text: Texto alineado a la izquierda
            right_text: Texto alineado a la derecha
            width: Ancho total disponible
        Returns:
            str: Línea formateada
        """
        spaces = width - len(left_text) - len(right_text)
        if spaces < 0:
            spaces = 1
        return f"{left_text}{' ' * spaces}{right_text}"
