#!/usr/bin/env python
# -*- coding: utf-8 -*-

import win32print
from printers.printer_commands import ESCPcmd

# Probar diferentes tamaños de fuente en la impresora de matriz de punto
def test_font_sizes():
    escp = ESCPcmd(use_escp=True)
    test_text = "ABCDEFGHIJKLMNOPQRSTUVWXYZ 1234567890"
    content = []

    content.append(escp.CMD_INIT)
    content.append(escp.CMD_CHARSET_PC850)  # Para caracteres especiales
    content.append(b"\n")

    content.append(b"=== PRUEBA DE CPI BASICOS ===\n\n")

    content.append(escp.CMD_CPI_10)
    content.append(b"10 CPI: ")
    content.append(test_text.encode("ascii") + b"\n\n")

    content.append(escp.CMD_CPI_12)
    content.append(b"12 CPI: ")
    content.append(test_text.encode("ascii") + b"\n\n")

    content.append(escp.CMD_CPI_15)
    content.append(b"15 CPI: ")
    content.append(test_text.encode("ascii") + b"\n\n")

    content.append(escp.CMD_CPI_17)
    content.append(b"17 CPI: ")
    content.append(test_text.encode("ascii") + b"\n\n")

    content.append(b"\n" + b"=" * 80 + b"\n\n")

    content.append(b"=== PRUEBA DE MODO CONDENSADO ===\n\n")

    content.append(escp.CMD_CPI_10)
    content.append(escp.CMD_CONDENSED_ON)
    content.append(b"10 CPI Condensado: ")
    content.append(test_text.encode("ascii") + b"\n\n")
    content.append(escp.CMD_CONDENSED_OFF)

    content.append(escp.CMD_CPI_12)
    content.append(escp.CMD_CONDENSED_ON)
    content.append(b"12 CPI Condensado: ")
    content.append(test_text.encode("ascii") + b"\n\n")
    content.append(escp.CMD_CONDENSED_OFF)

    content.append(escp.CMD_CPI_15)
    content.append(escp.CMD_CONDENSED_ON)
    content.append(b"15 CPI Condensado: ")
    content.append(test_text.encode("ascii") + b"\n\n")
    content.append(escp.CMD_CONDENSED_OFF)

    content.append(escp.CMD_CPI_17)
    content.append(escp.CMD_CONDENSED_ON)
    content.append(b"17 CPI Condensado: ")
    content.append(test_text.encode("ascii") + b"\n\n")
    content.append(escp.CMD_CONDENSED_OFF)

    content.append(b"\n" + b"=" * 80 + b"\n\n")

    content.append(b"=== PRUEBA DE MODO COMPRIMIDO ===\n\n")

    content.append(escp.CMD_CPI_17)
    content.append(escp.CMD_COMPRESSED_ON)
    content.append(b"17 CPI Comprimido: ")
    content.append(test_text.encode("ascii") + b"\n\n")
    content.append(escp.CMD_COMPRESSED_OFF)

    content.append(escp.CMD_FORM_FEED)
    content.append(escp.CMD_INIT)

    document = b"".join(content)

    try:
        printer_name = win32print.GetDefaultPrinter()
        printer_handle = win32print.OpenPrinter(printer_name)
        try:
            doc_info = ("Test Font Sizes", None, "RAW")
            win32print.StartDocPrinter(printer_handle, 1, doc_info)
            win32print.StartPagePrinter(printer_handle)

            win32print.WritePrinter(printer_handle, document)

            win32print.EndPagePrinter(printer_handle)
            win32print.EndDocPrinter(printer_handle)

            print("Documento de prueba enviado a la impresora")

        finally:
            win32print.ClosePrinter(printer_handle)

    except Exception as e:
        print(f"Error imprimiendo documento: {str(e)}")


if __name__ == "__main__":
    test_font_sizes()
