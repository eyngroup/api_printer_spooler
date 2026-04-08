#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright 2024, Iron Graterol
Licensed under the GNU Affero General Public License, version 3 or later.

Clase que contiene los comandos ESC/P, ESC/POS, TFHKA
"""

import ctypes
from typing import Dict, Any


class HKAcmd:  # pylint: disable=R0903
    """Clase que contiene los comandos para las impresoras fiscales TFHKA"""

    # Comandos fiscales
    CANCEL = "7"  # Cancelar documento fiscal en progreso.
    SUBTOTAL = "3"  # Mostrar subtotal en el documento
    DAILY_REPORT = "I0X"
    DAILY_CLOSE = "I0Z"
    IGTF_CLOSE = "199"  # Cierre para documentos con flag 50 = 01

    # Comandos para documentos fiscales
    AFFECTED_NUMBER = "iF*{}"  # Numero del documento afectado
    AFFECTED_DATE = "iD*{}"  # Fecha del documento afectado
    AFFECTED_SERIAL = "iI*{}"  # Serial del equipo afectado

    PARTNER_VAT = "iR*{}"  # RIF o CI
    PARTNER_NAME = "iS*{}"  # Razón Social
    PARTNER_ADDRESS = "i{}{}"  # Dirección - usa índice dinámico (i00, i01, etc.)
    PARTNER_PHONE = "i{}{}"  # Teléfono - usa índice dinámico
    PARTNER_EMAIL = "i{}{}"  # Email - usa índice dinámico

    DOCUMENT_NUMBER = "i{}{}"  # Numero de documento origen - usa índice dinámico
    DOCUMENT_REFERENCE = "i{}{}"  # Referencia del documento origen - usa índice dinámico
    DOCUMENT_DATE = "i{}{}"  # Fecha del documento origen - usa índice dinámico
    DOCUMENT_NAME = "i{}{}"  # Nombre del documento origen - usa índice dinámico
    DOCUMENT_CASHIER = "i{}{}"  # Nombre del Cajero o Vendedor - usa índice dinámico

    # Comandos para items fiscales
    ITEM_LINE = "{}{}{}{}"  # impuesto, precio, cantidad, nombre del producto
    ITEM_DISCOUNT_PERCENTAGE = "p-{}"  # porcentaje de descuento
    ITEM_SURCHARGE_PERCENTAGE = "p+{}"  # porcentaje de recargo
    ITEM_DISCOUNT_AMOUNT = "q-{}"  # importe del descuento
    ITEM_SURCHARGE_AMOUNT = "q+{}"  # importe del recargo
    ITEM_COMMENT = "@{}"  # comentarios en cuerpo del documento

    # Comandos de pagos fiscales
    PAY_UNIQUE = "101"  # cierre solo con unico pago, aqui usado EFECTIVO
    PAY_FULL = "1{}"  # Pago total
    PAY_PARTIAL = "2{}{}"  # Pago parcial

    # Comandos para líneas adicionales (pie de página, antes del barcode)
    ADDITIONAL_LINES = "i0{}{}"  # Líneas Adicionales (i01 a i09)

    # Comandos para código de barra de pie de ticket
    BARCODE_LINE = "y{}"  # Código de barra de pie de ticket

    # Comandos para documentos NO fiscales
    DNF_OPEN = "800{}"  # Abrir documento NO FISCAL
    DNF_CENTERED = "80!{}"  # Texto NO FISCAL centrado
    DNF_EXPANDED = "80>{}"  # Texto NO FISCAL expandido
    DNF_BOLD = "80*{}"  # Texto NO FISCAL en negritas
    DNF_BOLD_CENTERED = "80¡{}"  # Texto NO FISCAL en negritas centrado
    DNF_BOLD_CENTERED_DOUBLE = "80${}"  # Texto NO FISCAL en negritas, centrado y doble tamaño
    DNF_CLOSE = "810{}"  # Cerrar documento NO FISCAL


class PNPcmd:  # pylint: disable=R0903
    """Clase que contiene las constantes para los tipos de datos de la impresora fiscal PNP"""

    # Tipos de datos básicos
    PRINTER_CHAR_P = ctypes.c_char_p
    PRINTER_NO_ARGS = []
    PRINTER_SINGLE_ARG = [ctypes.c_char_p]
    PRINTER_DOUBLE_ARG = [ctypes.c_char_p, ctypes.c_char_p]

    # Comandos fiscales
    CANCEL = "C|0"
    DAILY_REPORT = "9|X"
    DAILY_CLOSE = "9|Z"

    # Comandos para documentos fiscales
    OPEN_CREDIT = "@|{}|{}|{}|{}|{}|{}|D"  # cliente, rif, documento, serial, fecha, hora
    OPEN_INVOICE = "@|{}|{}|||||T"  # cliente, rif

    PARTNER_VAT = "RIF:{}"  # RIF o CI
    PARTNER_NAME = "CLI:{}"  # Razón Social
    PARTNER_ADDRESS = "DIR:{}"  # Dirección "A|DIR:{}"
    PARTNER_PHONE = "TEL:{}"  # Teléfono "A|TEL:{}"
    PARTNER_EMAIL = "EMAIL:{}"  # Email "A|EMAIL:{}"

    DOCUMENT_NUMBER = "NUM:{}"  # Numero de documento origen "A|NUM:{}"
    DOCUMENT_REFERENCE = "REF:{}"  # Referencia del documento origen "A|REF:{}"
    DOCUMENT_DATE = "FECHA:{}"  # Fecha del documento origen "A|FECHA:{}"
    DOCUMENT_NAME = "DOC:{}"  # Nombre del documento origen "A|DOC:{}"
    DOCUMENT_CASHIER = "CAJ:{}"  # Nombre del Cajero o Vendedor "A|CAJ:{}"

    # Comandos para items fiscales
    ITEM_LINE = "B|{}|{}|{}|{}|M"  # Agregar ítem fiscal
    ITEM_LINE_DEL = "B|{}|{}|{}|{}|m"  # Anular ítem fiscal

    # Comandos de pagos fiscales
    SUBTOTAL = b"C"  # Obtener subtotal
    CLOSE_TOTAL = "E|T"  # Cierre total "E|T"
    CLOSE_PARTIAL = "E|A|{}"  # Cierre parcial "E|A|{}"
    CLOSE_TOTAL_IGTF = "E|U|{}"  # Cierre total con IGTF "E|U|{}"
    CLOSE_PARTIAL_IGTF = "E|B|{}"  # Cierre parcial con IGTF  "E|B|{}"

    # Comandos para líneas adicionales
    COMMENTS = "A|{}"  # comentarios en cuerpo del documento
    INTER_LINE = "-" * 40

    # Comandos para código de barra de pie de ticket
    BARCODE = "T|{}"

    # Comandos para documentos NO fiscales
    DNF_OPEN = "H|"  # Abrir documento no fiscal
    DNF_TEXT = "I|{}"  # Imprimir línea en documento no fiscal
    DNF_CLOSE = "J|"  # Cerrar documento no fiscal

    # Estados de la impresora (Campo 4 del comando "V")
    PRINTER_STATES = {
        "00": "Impresora lista",
        "01": "Factura fiscal en curso",
        "02": "Documento no fiscal en curso",
        "03": "SLIP activo",
        "04": "Requiere reporte Z",
        "05": "Primeras líneas descriptivas impresas",
        "08": "Equipo bloqueado esperando cierre Z",
        "10": "Error crítico: BCC RAM",
        "11": "Error crítico: BCC ROM",
        "12": "Error crítico: Formato FECHA RAM",
        "13": "Error crítico: Formato datos Z",
        "14": "Error crítico: Límite memoria fiscal",
    }

    # Bits de error de impresora
    PRINTER_ERROR_BITS = {2: "Error y/o falla de impresora", 3: "Impresora fuera de línea", 14: "Impresora sin papel"}

    # Bits de estado fiscal
    FISCAL_STATUS_BITS = {
        0: "Error de comprobación de memoria fiscal",
        1: "Error de comprobación de memoria de trabajo",
        3: "Comando no reconocido",
        4: "Campo de datos inválido",
        5: "Comando no válido para estado fiscal",
        6: "Desbordamiento de totales",
        7: "Memoria fiscal llena",
        8: "Memoria fiscal casi llena",
        11: "Es necesario hacer cierre de jornada fiscal",
        12: "Factura fiscal abierta",
        13: "Documento no fiscal abierto",
    }

    @staticmethod
    def parse_status(error_code: str, status_code: str) -> Dict[str, Any]:
        """
        Analiza los códigos de estado de la impresora y retorna las descripciones de error
        Args:
            error_code (str): Código de error de la impresora en hexadecimal
            status_code (str): Código de estado fiscal en hexadecimal
        Returns:
            Dict[str, Any]: Diccionario con los códigos y sus descripciones
        """
        try:
            error_bits = format(int(error_code, 16), "016b")[::-1]  # Invertir para que bit 0 sea el menos significativo
            status_bits = format(int(status_code, 16), "016b")[::-1]
        except ValueError:
            error_bits = "0" * 16
            status_bits = "0" * 16

        printer_errors = [
            desc for bit, desc in PNPcmd.PRINTER_ERROR_BITS.items() if error_bits[bit] == "1"
        ]  # Analizar bits del estado de impresora

        fiscal_errors = [
            desc for bit, desc in PNPcmd.FISCAL_STATUS_BITS.items() if status_bits[bit] == "1"
        ]  # Analizar bits del estado fiscal

        return {
            "error_code": error_code,
            "status_code": status_code,
            "error_description": " | ".join(printer_errors) if printer_errors else "Sin errores de impresora",
            "status_description": " | ".join(fiscal_errors) if fiscal_errors else "Sin errores fiscales",
        }
