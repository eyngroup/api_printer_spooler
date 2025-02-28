#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Implementación de la impresora dot-matrix."""

import json
import logging
import os
from typing import Dict, Any, List, Optional, Tuple

import win32print
from utils.tools import get_base_path, normalize_text, format_multiline

from .printer_base import BasePrinter
from .printer_commands import ESCPcmd
from .printer_counter import FiscalCounter

logger = logging.getLogger(__name__)


class MatrixPrinter(BasePrinter):
    """Clase para manejar la impresión en impresoras matriciales"""

    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa la impresora matricial
        Args:
            config (dict): Configuración de la impresora
        """
        super().__init__(config)
        self.printer_name = config.get("matrix_port")
        self.direct_print = config.get("matrix_direct", False)
        default_output = os.path.join(get_base_path(), "docs", "matrix_output.txt")
        self.output_file = config.get("matrix_file", default_output)
        self.template_name = config.get("matrix_template", "template_matriz_carta.json")
        self.paper_size = config.get("matrix_paper", "carta")
        self.printer_handle = None
        self.columns = None
        self.column_widths = None
        self.column_format = None

        use_escp = config.get("matrix_use_escp", True)  # Inicializar comandos ESC/POS
        self.escp_commands = ESCPcmd(use_escp)

        self._load_template()

        template_path = os.path.join(get_base_path(), "templates", self.template_name)  # Inicializar contador fiscal
        self.counter = FiscalCounter(template_path)

        self.separator = self.template["format"]["separator"]
        self.page_width = self.template["format"]["page_width"]

    def _get_printer_info(self) -> Tuple[bool, str, Optional[Dict]]:
        """
        Obtiene informacion detallada de la impresora
        Returns:
            Tuple[bool, str, Optional[Dict]]: (exito, mensaje, info)
        """
        try:
            printer_handle = win32print.OpenPrinter(self.printer_name)
            try:
                printer_info = win32print.GetPrinter(printer_handle, 2)
                # is_generic = "Generic" in printer_info.get("pDriverName", "")
                status_msg = f"Impresora: {self.printer_name}"
                status_msg += f"\nControlador: {printer_info.get('pDriverName', 'N/A')}"
                status_msg += f"\nPuerto: {printer_info.get('pPortName', 'N/A')}"
                status_msg += f"\nEstado: {printer_info.get('Status', 'N/A')}"

                return True, status_msg, printer_info
            finally:
                win32print.ClosePrinter(printer_handle)
        except Exception as e:
            return False, f"Error obteniendo info: {str(e)}", None

    def connect(self) -> bool:
        """
        Conecta con la impresora
        Returns:
            bool: True si se conectó correctamente
        """
        try:
            if self.direct_print:
                success, status_msg, printer_info = self._get_printer_info()
                if not success:  # Verificar impresora y controlador
                    raise RuntimeError(status_msg)

                logger.debug(status_msg)
                if printer_info["Status"] != 0:  # Verificar si está lista
                    raise RuntimeError(f"Impresora no lista. Estado: {printer_info['Status']}")

                # Advertir si no es controlador genérico
                if "Generic" not in printer_info.get("pDriverName", ""):
                    logger.warning(
                        "ADVERTENCIA: No se detectó controlador genérico. "
                        "Se recomienda usar 'Generic / Text Only' para mejor compatibilidad."
                    )

                self.printer_handle = win32print.OpenPrinter(self.printer_name)
                return True

            logger.info("Modo impresión a archivo: %s", self.output_file)
            return True

        except Exception as e:
            logger.error("Error conectando a impresora: %s", str(e))
            if self.printer_handle:
                self.disconnect()
            raise RuntimeError(f"No se puede conectar a la impresora: {str(e)}") from e

    def disconnect(self) -> None:
        """Desconecta la impresora"""
        try:
            if self.printer_handle:
                win32print.ClosePrinter(self.printer_handle)
            self.printer_handle = None
            logger.info("Impresora desconectada")
        except Exception as e:
            logger.error("Error desconectando impresora: %s", str(e))

    def print_document(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Imprime un documento
        Args:
            data (dict): Datos del documento a imprimir
        Returns:
            dict: Resultado de la impresión
        """
        if not self.config["matrix_enabled"]:
            return {
                "status": False,
                "message": "Impresora matricial deshabilitada en configuración",
                "data": None,
            }

        try:
            if not self.connect():
                return {
                    "status": False,
                    "message": f"No se pudo conectar a la impresora {self.printer_name}",
                    "data": None,
                }

            document_content = self._format_document(data)  # Formatea el documento si usa ESC/P
            fiscal_data = self.counter.update_counter(data.get("operation_type", "invoice"))  # Actualizar contador

            if self.direct_print:
                try:
                    try:  # Enviar directamente los bytes a la impresora
                        doc_info = ("Matrix Document", None, "RAW")
                        win32print.StartDocPrinter(self.printer_handle, 1, doc_info)
                        win32print.StartPagePrinter(self.printer_handle)

                        # No decodificar/codificar, mantener como bytes
                        win32print.WritePrinter(self.printer_handle, document_content)

                        win32print.EndPagePrinter(self.printer_handle)
                        win32print.EndDocPrinter(self.printer_handle)
                    finally:
                        self.disconnect()
                except Exception as e:
                    error_msg = f"Error imprimiendo documento: {str(e)}"
                    logger.error(error_msg, exc_info=True)
                    return {"status": False, "message": error_msg, "data": None}

                return {
                    "status": True,
                    "message": "Documento enviado a imprimir correctamente",
                    "data": fiscal_data,
                }

            try:
                with open(self.output_file, "wb") as f:
                    f.write(document_content)  # Escribir el archivo en modo binario

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
            message = f"Error imprimiendo documento: {str(e)}"
            logger.error(message, exc_info=True)
            return {"status": False, "message": message, "data": None}

    def check_status(self) -> Dict[str, Any]:
        """
        Verifica el estado de la impresora
        Returns:
            Dict[str, Any]: Estado de la impresora
        """
        status = {"online": False, "paper": True, "error": None}

        try:
            if self.direct_print:
                if self.connect():
                    status["online"] = True
                    self.disconnect()
                else:
                    status["error"] = f"No se puede conectar a la impresora {self.printer_name}"
            else:
                if os.path.exists(os.path.dirname(self.output_file)):
                    status["online"] = True
                else:
                    status["error"] = f"Directorio no existe: {os.path.dirname(self.output_file)}"
        except Exception as e:
            status["error"] = str(e)
            logger.error("Error verificando estado de impresora: %s", str(e))

        return status

    def _format_document(self, data: Dict[str, Any]) -> bytes:
        """
        Formatea el documento para impresión
        Args:
            data (dict): Datos del documento
        Returns:
            bytes: Documento formateado
        """
        content = []
        # content.extend(self._init_printer())

        # if self.paper_size == "media_carta": # Configurar tamaño de papel
        #     content.extend(self._set_page_length(43))  # 43 líneas para media carta
        # else:
        #     content.extend(self._set_page_length(66))  # 66 líneas para carta

        # Inicializar impresora y configurar página
        content.append(self.escp_commands.CMD_INIT)  # Reset printer
        content.append(self.escp_commands.CMD_PAGE_ZERO)  # Continuous form
        content.append(self.escp_commands.CMD_CHARSET_PC850)  # CP850 charset
        content.append(self.escp_commands.CMD_CPI_12)  # 12 CPI para el texto general

        # Formatear documento
        content.extend(self._format_header(data))
        content.extend(self._format_customer_info(data))
        content.extend(self._format_items(data))
        content.extend(self._format_totals(data))
        content.extend(self._format_footer(data))

        # Finalizar documento
        content.append(self.escp_commands.CMD_FORM_FEED)
        content.append(self.escp_commands.CMD_INIT)

        # Unir todo el contenido como bytes
        return b"".join(content)

    def _format_header(self, data: Dict[str, Any]) -> List[bytes]:
        """
        Formatea el encabezado del documento
        Args:
            data: Datos del documento
        Returns:
            List[bytes]: Líneas del encabezado
        """
        header = []
        header_info = self.template["header"]

        # Para el encabezado usamos texto más grande y centrado
        header.append(self.escp_commands.CMD_ALIGN_CENTER)
        header.append(self.escp_commands.CMD_CPI_12)  # 12 CPI para el encabezado
        header.append(self.escp_commands.CMD_BOLD_ON)
        for line in [
            header_info["title"],
            header_info["subtitle"],
            header_info["company"],
            header_info["address"],
            header_info["phone"],
        ]:
            header.append(line.encode("ascii", errors="replace") + b"\n")

        header.append(self.escp_commands.CMD_BOLD_OFF)
        header.append(b"\n")  # Línea en blanco

        header.append(self.escp_commands.CMD_CPI_15)  # 15 CPI para el resto

        document_mapping = {
            "invoice": "FACTURA",
            "credit": "NOTA DE CREDITO",
            "debit": "NOTA DE DEBITO",
            "note": "NOTA DE ENTREGA",
        }

        header_type = header_info["type"]
        document_type = (
            document_mapping.get(data["operation_type"], "NOTA DE DESPACHO") if header_type == "*" else header_type
        )

        header.append(self.escp_commands.CMD_ALIGN_RIGHT)
        doc_line = (
            f"FECHA: {data['document']['document_date']} | {document_type}: {data['document']['document_number']}\n"
        )
        header.append(doc_line.encode("ascii", errors="replace"))
        header.append(self.escp_commands.CMD_ALIGN_LEFT)
        header.append((self.separator * self.page_width + "\n").encode("ascii", errors="replace"))
        return header

    def _format_customer_info(self, data: Dict[str, Any]) -> List[bytes]:
        """
        Formatea la información del cliente
        Args:
            data: Datos del documento
        Returns:
            List[bytes]: Líneas de información del cliente
        """
        customer_info = []
        customer = data.get("customer", {})
        customer_line = f"RIF/CI:{customer['customer_vat']} | CLIENTE:{customer['customer_name']}\n"
        customer_info.append(customer_line.encode("ascii", errors="replace"))
        address = normalize_text(customer.get("customer_address", ""))
        phone = normalize_text(customer.get("customer_phone", ""))
        contact_line = f"DIR.: {address} | TEL.: {phone}\n"

        wrapped_lines = format_multiline(contact_line, self.page_width)
        if wrapped_lines:
            for line in wrapped_lines[:2]:  # Máximo 2 líneas
                customer_info.append((line + "\n").encode("ascii", errors="replace"))

        # Asegurar que haya al menos 3 líneas (con espacios en blanco si es necesario)
        while len(customer_info) < 3:
            customer_info.append(b"\n")

        customer_info.append((self.separator * self.page_width + "\n").encode("ascii", errors="replace"))
        return customer_info

    def _format_items(self, data: Dict[str, Any]) -> List[bytes]:
        """
        Formatea los items del documento
        Args:
            data: Datos del documento
        Returns:
            List[bytes]: Líneas de items
        """
        items_lines = []
        # items = data.get("items", [])

        # Obtener formato de columnas del template
        self.columns = self.template["header"]["columns"]
        self.column_widths = self.template["header"]["column_widths"]
        self.column_format = self.template["header"]["column_format"]

        # Verificar configuración de columnas
        if not len(self.columns) == len(self.column_widths) == len(self.column_format):
            raise ValueError("La configuración de columnas debe tener la misma longitud")

        # Encabezado de columnas
        header_line = ""
        for col, width in zip(self.columns, self.column_widths):
            header_line += f"{col:<{width}}"

        items_lines.append(self.escp_commands.CMD_BOLD_ON)
        items_lines.append((self.separator * self.page_width + "\n").encode("ascii", errors="replace"))
        items_lines.append((header_line + "\n").encode("ascii", errors="replace"))
        items_lines.append((self.separator * self.page_width + "\n").encode("ascii", errors="replace"))
        items_lines.append(self.escp_commands.CMD_BOLD_OFF)
        for item in data["items"]:
            item_line = ""
            values = [
                str(item["item_ref"]),
                str(item["item_name"]),
                item["item_quantity"],
                item["item_price"],
                item["item_quantity"] * item["item_price"],
            ]

            for val, width, fmt in zip(values, self.column_widths, self.column_format):
                if fmt == "s":
                    val_str = str(val)[:width]  # Truncar texto si es muy largo
                    item_line += f"{val_str:<{width}}"
                elif fmt == "f":
                    item_line += f"{float(val):>{width}.2f}"

            items_lines.append((item_line + "\n").encode("ascii", errors="replace"))

            if item.get("item_comment") and self.template["format"].get("show_items_comment", False):
                comment_line = f"{'':8}Nota: {item['item_comment']}\n"
                items_lines.append(comment_line.encode("ascii", errors="replace"))

        return items_lines

    def _format_totals(self, data: Dict[str, Any]) -> List[bytes]:
        """
        Formatea los totales del documento
        Args:
            data: Datos del documento
        Returns:
            List[bytes]: Líneas de totales
        """
        totals = []  # Calcular totales
        subtotal = sum(item["item_quantity"] * item["item_price"] for item in data["items"])
        tax = sum(item["item_quantity"] * item["item_price"] * (item["item_tax"] / 100) for item in data["items"])
        total = subtotal + tax
        totals.append((self.separator * self.page_width + "\n").encode("ascii", errors="replace"))
        totals.append(self.escp_commands.CMD_ALIGN_RIGHT)
        totals.append(self.escp_commands.CMD_BOLD_ON)
        totals.append(f"SUBTOTAL: {subtotal:>14.2f}\n".encode("ascii", errors="replace"))
        totals.append(f"IVA: {tax:>14.2f}\n".encode("ascii", errors="replace"))
        totals.append(f"TOTAL: {total:>14.2f}\n".encode("ascii", errors="replace"))

        totals.append(self.escp_commands.CMD_BOLD_OFF)

        # Agregar pagos si están habilitados
        if data.get("payments") and self.template["format"].get("show_payments", False):
            totals.append(self.escp_commands.CMD_BOLD_ON)
            totals.append((self.separator * self.page_width + "\n").encode("ascii", errors="replace"))
            totals.append(self.escp_commands.CMD_BOLD_OFF)

            for payment in data["payments"]:
                payment_line = f"{payment['payment_name']}: {payment['payment_amount']:>10.2f}\n"
                totals.append(payment_line.encode("ascii", errors="replace"))

        totals.append(self.escp_commands.CMD_ALIGN_LEFT)  # Volver a alineación izquierda

        return totals

    def _format_footer(self, data: Dict[str, Any]) -> List[bytes]:
        """
        Formatea el pie del documento
        Args:
            data: Datos del documento
        Returns:
            List[bytes]: Líneas del pie
        """
        footer = []
        footer_info = self.template["footer"]
        footer.append(b"\n")  # Agregar línea en blanco
        footer.append((self.separator * self.page_width + "\n").encode("ascii", errors="replace"))  # Separador
        footer.append(self.escp_commands.CMD_CPI_17)

        if data.get("delivery", {}).get("delivery_comments") and self.template["format"].get(
            "show_delivery_comment", False
        ):
            footer.append(self.escp_commands.CMD_BOLD_ON)
            footer.append("COMENTARIOS\n".encode("ascii", errors="replace"))
            footer.append(self.escp_commands.CMD_BOLD_OFF)
            footer.append(b"\n")

            for comment in data["delivery"]["delivery_comments"]:
                footer.append((comment + "\n").encode("ascii", errors="replace"))

        footer.append(b"\n")
        footer.append(self.escp_commands.CMD_ALIGN_CENTER)
        footer.append((footer_info["message"] + "\n").encode("ascii", errors="replace"))
        footer.append((footer_info["legal"] + "\n").encode("ascii", errors="replace"))

        footer.append(self.escp_commands.CMD_ALIGN_LEFT)
        return footer

    def _end_document(self) -> List[bytes]:
        """Comandos para finalizar el documento"""
        return [
            self.escp_commands.CMD_FORM_FEED,  # Avanzar página
            self.escp_commands.CMD_INIT,  # Reiniciar impresora
        ]

    def _load_template(self) -> None:
        """Carga el template de impresión"""
        try:
            template_path = os.path.join(get_base_path(), "templates", self.template_name)
            with open(template_path, "r", encoding="utf-8") as f:
                self.template = json.load(f)
            logger.debug("Template cargado: %s", self.template)
        except Exception as e:
            logger.error("Error cargando template: %s", str(e))
            raise
