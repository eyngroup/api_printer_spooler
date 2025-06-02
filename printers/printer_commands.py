#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright © 2024, Iron Graterol
Licensed under the GNU Affero General Public License, version 3 or later.

Clase que contiene los comandos ESC/P, ESC/POS, TFHKA
"""

import ctypes
from typing import Dict, Any


class ESCPcmd:  # pylint: disable=R0903
    """Clase que contiene los comandos ESC/P para impresoras matriciales"""

    def __init__(self, use_escp=True):
        self.use_escp: bool = use_escp

        # Comandos básicos
        self.CMD_INIT: bytes = self.command(b"\x1b@")  # Inicializar impresora
        self.CMD_RESET: bytes = self.command(b"\x1b@")  # Reiniciar impresora
        self.CMD_FORM_FEED: bytes = self.command(b"\x0c")  # Avanzar alimentador
        self.CMD_CR: bytes = self.command(b"\x0d")  # Carriage return
        self.CMD_LF: bytes = self.command(b"\x0a")  # Line feed
        self.CMD_CR_LF: bytes = self.command(b"\x0d\x0a")  # Carriage return + Line feed

        # Comandos de página
        self.CMD_PAGE_LENGTH: bytes = self.command(b"\x1bC")  # Ajustar longitud de página en líneas
        self.CMD_PAGE_ZERO: bytes = self.command(b"\x1b\x43\x00")  # Ajustar longitud de página a 0
        self.CMD_MARGINS: bytes = self.command(b"\x1bQ")  # Set right and left margins

        # Comandos de fuente y calidad
        self.CMD_DRAFT: bytes = self.command(b"\x1bx0")  # Calidad draft
        self.CMD_NLQ: bytes = self.command(b"\x1bx1")  # NLQ (Calidad Cercana a Carta)

        # Comandos de alineación
        self.CMD_ALIGN_LEFT: bytes = self.command(b"\x1ba\x00")  # Alineación a la izquierda
        self.CMD_ALIGN_CENTER: bytes = self.command(b"\x1ba\x01")  # Alineación al centro
        self.CMD_ALIGN_RIGHT: bytes = self.command(b"\x1ba\x02")  # Alineación a la derecha

        # Comandos CPI (Caracteres por pulgada)
        self.CMD_CPI_10: bytes = self.command(b"\x1bP")  # Usar 10 CPI
        self.CMD_CPI_12: bytes = self.command(b"\x1bM")  # Usar 12 CPI
        self.CMD_CPI_15: bytes = self.command(b"\x1bg")  # Usar 15 CPI
        self.CMD_CPI_17: bytes = self.command(b"\x1bP\x1b\x0f")  # Usar 10 CPI + condensada
        self.CMD_CPI_20: bytes = self.command(b"\x1bM\x1b\x0f")  # Usar 12 CPI + condensada
        self.CMD_CONDENSED_ON: bytes = self.command(b"\x0f")  # ON fuente condensada
        self.CMD_CONDENSED_OFF: bytes = self.command(b"\x12")  # OFF fuente condensada

        # Comandos de tamaño comprimido
        self.CMD_COMPRESSED_ON: bytes = self.command(b"\x1b\x0f")  # ON Impresión comprimida
        self.CMD_COMPRESSED_OFF: bytes = self.command(b"\x1b\x12")  # OFF Impresión comprimida
        self.CMD_SUPERSCRIPT_ON: bytes = self.command(b"\x1bS0")  # ON Superíndice
        self.CMD_SUBSCRIPT_ON: bytes = self.command(b"\x1bS1")  # ON Subíndice
        self.CMD_SCRIPT_OFF: bytes = self.command(b"\x1bT")  # OFF Superíndice/Subíndice

        # Comandos de estilo
        self.CMD_BOLD_ON: bytes = self.command(b"\x1bE")  # ON fuente en negrita
        self.CMD_BOLD_OFF: bytes = self.command(b"\x1bF")  # OFF fuente en negrita
        self.CMD_EXPANDED_ON: bytes = self.command(b"\x1bW\x01")  # ON fuente ampliada
        self.CMD_EXPANDED_OFF: bytes = self.command(b"\x1bW\x00")  # OFF fuente ampliada
        self.CMD_CURSIVE_ON: bytes = self.command(b"\x1b4")  # ON fuente cursiva
        self.CMD_CURSIVE_OFF: bytes = self.command(b"\x1b5")  # OFF fuente cursiva
        self.CMD_UNDERLINE_ON: bytes = self.command(b"\x1b-\x01")  # ON fuente subrayada
        self.CMD_UNDERLINE_OFF: bytes = self.command(b"\x1b-\x00")  # OFF fuente subrayada

        # Comandos de espaciado
        self.CMD_LINE_SPACING_1_8: bytes = self.command(b"\x1b0")  # Interlineado de 1/8 de pulgada
        self.CMD_LINE_SPACING_1_6: bytes = self.command(b"\x1b2")  # Interlineado de 1/6 pulgadas
        self.CMD_LINE_SPACING_N_72: bytes = self.command(b"\x1bA")  # Espacio entre líneas de n/72 pulgadas
        self.CMD_LINE_SPACING_N_216: bytes = self.command(b"\x1b3")  # n/216 pulgadas de espacio entre líneas
        self.CMD_LINE_SPACING_TIGHT: bytes = self.command(b"\x1b3\x0c")  # Distancia entre líneas estrecha (12/216")
        self.CMD_LINE_SPACING_NORMAL: bytes = self.command(b"\x1b3\x18")  # Interlineado normal (24/216")
        self.CMD_LINE_SPACING_WIDE: bytes = self.command(b"\x1b3\x24")  # Amplia separación entre líneas (36/216")

        # Comandos de caracteres
        self.CMD_CHARSET_USA: bytes = self.command(b"\x1bR\x00")  # Seleccione el conjunto de caracteres de EE.UU.
        self.CMD_CHARSET_SPAIN: bytes = self.command(b"\x1bR\x06")  # Seleccione el juego de caracteres español
        self.CMD_CHARSET_PC850: bytes = self.command(b"\x1bt\x02")  # Select CP850 (multilingual)

    def command(self, value: bytes) -> bytes:
        """Retorna el comando si use_escp es True, sino retorna cadena vacía"""
        return value if self.use_escp else b""


class ESCPOScmd:  # pylint: disable=R0903
    """Clase que contiene los comandos ESC/POS para impresoras térmicas"""

    def __init__(self, use_escpos=True):
        self.use_escpos = use_escpos

        # Comandos básicos
        self.CMD_INIT = self.command("\x1b\x40")  # Inicializar impresora
        self.CMD_CHARSET = self.command("\x1b\x74\x12")  # character code table (PC850)
        self.CMD_CUT = self.command("\x1d\x56\x41\x00")  # Cut paper
        self.CMD_FEED = self.command("\x0a")  # Avanzar alimentador

        # Comandos de fuente
        self.CMD_FONT_A = self.command("\x1b\x4d\x00")  # Fuente A (12x24)
        self.CMD_FONT_B = self.command("\x1b\x4d\x01")  # Fuente B (9x17)
        self.CMD_FONT_NORMAL = self.command("\x1d\x21\x00")  # Tamaño normal
        self.CMD_FONT_DOUBLE = self.command("\x1d\x21\x11")  # Doble altura y anchura

        # Comandos de alineación
        self.CMD_ALIGN_LEFT = self.command("\x1b\x61\x00")  # Alineación a la izquierda
        self.CMD_ALIGN_CENTER = self.command("\x1b\x61\x01")  # Alineación al centro
        self.CMD_ALIGN_RIGHT = self.command("\x1b\x61\x02")  # Alineación a la derecha

        # Comandos de estilo
        self.CMD_BOLD_ON = self.command("\x1b\x45\x01")  # ON fuente en negrita
        self.CMD_BOLD_OFF = self.command("\x1b\x45\x00")  # OFF fuente en negrita
        self.CMD_UNDERLINE_ON = self.command("\x1b\x2d\x01")  # ON fuente subrayada
        self.CMD_UNDERLINE_OFF = self.command("\x1b\x2d\x00")  # OFF fuente subrayada
        self.CMD_INVERSE_ON = self.command("\x1d\x42\x01")  # ON blanco sobre negro
        self.CMD_INVERSE_OFF = self.command("\x1d\x42\x00")  # OFF blanco sobre negro

        # Comandos de código de barras
        self.CMD_BARCODE_HEIGHT = self.command("\x1d\x68\x50")  # Ajustar altura del código
        self.CMD_BARCODE_WIDTH = self.command("\x1d\x77\x02")  # Ajustar anchura del código
        self.CMD_BARCODE_FONT = self.command("\x1d\x66\x00")  # Ajustar fuente de código
        self.CMD_BARCODE_TXT_OFF = self.command("\x1d\x48\x00")  # HRI caracteres del código OFF
        self.CMD_BARCODE_TXT_ABV = self.command("\x1d\x48\x01")  # HRI caracteres del código arriba
        self.CMD_BARCODE_TXT_BLW = self.command("\x1d\x48\x02")  # HRI caracteres del código abajo
        self.CMD_BARCODE_TXT_BTH = self.command("\x1d\x48\x03")  # HRI tanto arriba como abajo
        self.CMD_BARCODE_CODE128 = self.command("\x1d\x6b\x49")  # Formato de código de barras 128

        # Comandos de código qr
        self.CMD_QR_SIZE = self.command("\x1d\x28\x6b\x03\x00\x31\x43")  # Ajustar tamaño QR
        self.CMD_QR_CORRECTION = self.command("\x1d\x28\x6b\x03\x00\x31\x45")  # Establecer corrección QR
        self.CMD_QR_STORE = self.command("\x1d\x28\x6b")  # Almacenar datos QR
        self.CMD_QR_PRINT = self.command("\x1d\x28\x6b\x03\x00\x31\x51\x30")  # Imprimir código QR

    def command(self, value):
        """Retorna el comando si use_escpos es True, sino retorna cadena vacía"""
        return value if self.use_escpos else ""


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
    PARTNER_ADDRESS = "i00DIR:{}"  # Dirección
    PARTNER_PHONE = "i01TEL:{}"  # Teléfono
    PARTNER_EMAIL = "i03EMAIL:{}"  # Email

    DOCUMENT_NUMBER = "i04REF:{}"  # Numero de documento origen
    DOCUMENT_DATE = "i05FECHA:{}"  # Fecha del documento origen
    DOCUMENT_NAME = "i06DOC:{}"  # Nombre del documento origen
    DOCUMENT_CASHIER = "i07CAJ:{}"  # Nombre del Cajero o Vendedor

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

    # Comandos para líneas adicionales
    COMMENTS = "@{}"  # comentarios en cuerpo del documento
    # COMMENTS = "i0{}{}"  # Líneas Adicionales

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


class PNPcmd: # pylint: disable=R0903
    """Clase que contiene las constantes para los tipos de datos de la impresora fiscal PNP"""

    # Tipos de datos básicos
    PRINTER_CHAR_P = ctypes.c_char_p
    PRINTER_NO_ARGS = []
    PRINTER_SINGLE_ARG = [ctypes.c_char_p]
    PRINTER_DOUBLE_ARG = [ctypes.c_char_p, ctypes.c_char_p]

    # Comandos fiscales
    CANCEL = "C|0"

    # Comandos para documentos fiscales
    OPEN_CREDIT = "@|{}|{}|{}|{}|{}|{}|D"  # cliente, rif, documento, serial, fecha, hora
    OPEN_INVOICE = "@|{}|{}|||||T"  # cliente, rif

    PARTNER_VAT = "RIF:{}"  # RIF o CI
    PARTNER_NAME = "CLI:{}"  # Razón Social
    PARTNER_ADDRESS = "DIR:{}"  # Dirección "A|DIR:{}"
    PARTNER_PHONE = "TEL:{}"  # Teléfono "A|TEL:{}"
    PARTNER_EMAIL = "EMAIL:{}"  # Email "A|EMAIL:{}"

    DOCUMENT_NUMBER = "REF:{}"  # Numero de documento origen "A|REF:{}"
    DOCUMENT_DATE = "FECHA:{}"  # Fecha del documento origen "A|FECHA:{}"
    DOCUMENT_NAME = "DOC:{}"  # Nombre del documento origen "A|DOC:{}"
    DOCUMENT_CASHIER = "CAJ:{}"  # Nombre del Cajero o Vendedor "A|CAJ:{}"

    INTER_LINE = "-" * 40

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

    # Comandos para código de barra de pie de ticket

    # Comandos para documentos NO fiscales
    DNF_OPEN = "H|{}"  # Abrir documento no fiscal
    DNF_TEXT = "I|{}"  # Imprimir línea en documento no fiscal
    DNF_CLOSE = "J|{}"  # Cerrar documento no fiscal

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
