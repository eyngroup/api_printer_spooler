#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright © 2024, Iron Graterol
Licensed under the GNU Affero General Public License, version 3 or later.

Script para probar impresión directa al puerto USB.
"""

import logging
import time
import win32file
import win32con
import pywintypes

# Configurar logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def test_direct_print(port_name: str = "USB004"):
    try:
        port_path = f"\\\\.\\{port_name}"
        logger.info(f"Intentando abrir puerto: {port_path}")

        handle = win32file.CreateFile(
            port_path,
            win32con.GENERIC_READ | win32con.GENERIC_WRITE,
            0,  # No compartir
            None,  # Sin atributos de seguridad
            win32con.OPEN_EXISTING,
            win32con.FILE_ATTRIBUTE_NORMAL,
            None,
        )

        if handle == win32file.INVALID_HANDLE_VALUE:
            logger.error("No se pudo abrir el puerto")
            return False

        logger.info("Puerto abierto exitosamente")

        tests = [
            {"name": "Prueba 1 - Solo beep", "content": b"\x07", "description": "Intentando hacer beep..."},
            {
                "name": "Prueba 2 - Texto plano",
                "content": "PRUEBA DIRECTA AL PUERTO\r\nTexto simple\r\n\r\n".encode("ascii"),
                "description": "Enviando texto plano...",
            },
            {
                "name": "Prueba 3 - Reset y texto",
                "content": (
                    b"\x1b@"  # Reset
                    + b"\x0d\x0a"  # CR+LF
                    + "PRUEBA CON RESET\r\n".encode("ascii")
                    + b"\x0c"  # Form feed
                ),
                "description": "Enviando reset y texto...",
            },
            {
                "name": "Prueba 4 - Modo draft",
                "content": (
                    b"\x1b@"  # Reset
                    + b"\x1bx\x00"  # Draft mode
                    + b"\x12"  # DC2 - Modo condensado OFF
                    + "PRUEBA MODO DRAFT\r\n".encode("ascii")
                    + b"\x0e"  # SO - Doble ancho ON
                    + "Texto ancho\r\n".encode("ascii")
                    + b"\x14"  # DC4 - Doble ancho OFF
                    + "Texto normal\r\n".encode("ascii")
                    + b"\x0c"  # Form feed
                ),
                "description": "Probando modo draft...",
            },
        ]

        for test in tests:
            try:
                logger.info(f"\nEjecutando {test['name']}")
                logger.info(test["description"])

                bytes_written = win32file.WriteFile(handle, test["content"])
                logger.info(f"Bytes enviados: {bytes_written[1]}")

                win32file.FlushFileBuffers(handle)

                logger.info(f"Test completado: {test['name']}")
                time.sleep(2)

            except Exception as e:
                logger.error(f"Error en {test['name']}: {str(e)}")
                continue

        logger.info("\nTodas las pruebas completadas")
        return True

    except pywintypes.error as e:
        logger.error(f"Error de Windows: {str(e)}")
        return False

    except Exception as e:
        logger.error(f"Error general: {str(e)}")
        return False

    finally:
        try:
            if "handle" in locals() and handle != win32file.INVALID_HANDLE_VALUE:
                win32file.CloseHandle(handle)
                logger.info("Puerto cerrado")
        except Exception as e:
            logger.error(f"Error cerrando puerto: {str(e)}")


if __name__ == "__main__":
    port_variants = ["USB004", "COM9", "COM96", "COM97", "COM98", "LPT1"]

    for port_name in port_variants:
        logger.info(f"\n{'=' * 50}")
        logger.info(f"Intentando con puerto: {port_name}")
        logger.info("=" * 50)

        success = test_direct_print(port_name)

        if success:
            logger.info(f"Pruebas completadas exitosamente en {port_name}")
            break
        else:
            logger.error(f"Las pruebas fallaron en {port_name}")
