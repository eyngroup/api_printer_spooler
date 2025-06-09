#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de prueba para la librería pfpnp.py
"""

import os
import sys
import time
import logging
import json

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from controllers.pfpnp import FiscalPrinter


def test_connection(printer, port):
    """Prueba la conexión con la impresora."""
    print(f"\n=== Probando conexión en puerto {port} ===")
    result = printer.open_port()
    if result:
        print(f"Conexión exitosa en puerto {port}")
        return True
    else:
        print(f"No se pudo conectar en puerto {port}")
        return False


def test_command(printer, command, description):
    """Prueba el envío de un comando a la impresora."""
    print(f"\n=== Enviando comando {command}: {description} ===")
    result = printer.send_command(command)
    if result is True:
        print(f"Comando {command} enviado correctamente")
    elif result is False:
        print(f"Error al enviar comando {command}")
    else:
        print(f"Respuesta: {result}")
    return result


def main():
    """Función principal de prueba."""
    ports = ["COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9"]

    baudrate = 9600
    timeout = 1

    printer = None
    connected_port = None

    for port in ports:
        try:
            printer = FiscalPrinter(port=port, baudrate=baudrate, timeout=timeout)
            if test_connection(printer, port):
                connected_port = port
                break
            printer.close_port()
        except Exception as e:
            print(f"Error al probar puerto {port}: {e}")

    if not connected_port:
        print("No se pudo conectar a ningún puerto")
        return

    try:
        print("\n=== Probando comandos básicos para impresora PNP ===")

        # Comandos de estado
        test_command(printer, "S1", "Obtener estado fiscal")
        test_command(printer, "S2", "Obtener totales diarios")
        test_command(printer, "S3", "Obtener datos de inicialización")
        test_command(printer, "S5", "Obtener datos de memoria de trabajo")
        test_command(printer, "SV", "Obtener datos de la impresora")

        test_command(printer, "I0", "Obtener información de la impresora")

        print("\n=== Pruebas completadas ===")
    except Exception as e:
        print(f"Error durante las pruebas: {e}")
    finally:
        if printer:
            printer.close_port()
            print(f"Puerto {connected_port} cerrado")


if __name__ == "__main__":
    main()
