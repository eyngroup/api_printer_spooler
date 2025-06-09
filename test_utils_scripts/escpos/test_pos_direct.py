#!/usr/bin/env python
# -*- coding: utf-8 -*-

import win32print
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def test_printer(printer_name: str = "POS-80C"):
    try:
        logger.info(f"Intentando conectar con la impresora: {printer_name}")
        printer_handle = win32print.OpenPrinter(printer_name)

        printer_info = win32print.GetPrinter(printer_handle, 2)
        logger.info(f"Estado de la impresora: {printer_info['Status']}")

        if printer_info["Status"] != 0:  # 0 significa "Ready"
            logger.error(f"Impresora no lista. Estado: {printer_info['Status']}")
            win32print.ClosePrinter(printer_handle)
            return False

        test_content = (
            "=== PRUEBA DE IMPRESIÓN ===\n"
            "Línea 1: Texto normal\n"
            "Línea 2: 12345\n"
            "Línea 3: áéíóú\n"  # Probar caracteres especiales
            "=======================\n"
            "\n\n\n"  # Avanzar papel
        )

        try:
            logger.info("Inicio documento...")
            doc_info = ("Test Print", None, "RAW")  # (nombre_doc, nombre_output, tipo_datos)
            win32print.StartDocPrinter(printer_handle, 1, doc_info)

            logger.info("Inicio página...")
            win32print.StartPagePrinter(printer_handle)

            logger.info("Inicio contenido...")
            win32print.WritePrinter(printer_handle, test_content.encode("utf-8"))

            logger.info("Finalizo página...")
            win32print.EndPagePrinter(printer_handle)

            logger.info("Finalizo documento...")
            win32print.EndDocPrinter(printer_handle)

            logger.info("Impresión completada")
            return True

        except Exception as e:
            logger.error(f"Error durante la impresión: {str(e)}")
            return False

        finally:
            win32print.ClosePrinter(printer_handle)
            logger.info("Conexión cerrada")

    except Exception as e:
        logger.error(f"Error conectando con la impresora: {str(e)}")
        return False


if __name__ == "__main__":
    logger.info("Impresoras disponibles:")
    for printer in win32print.EnumPrinters(2):
        logger.info(f"  - {printer[2]}")

    printer_name = "POS-80C"  # Nombre por defecto, mismo que en config.json
    success = test_printer(printer_name)

    if success:
        logger.info("Prueba completada exitosamente")
    else:
        logger.error("La prueba falló")
