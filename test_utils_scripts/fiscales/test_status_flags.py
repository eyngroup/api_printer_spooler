#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para probar los métodos get_printer_status y read_flags
con impresoras fiscales TFHKA.
"""

import sys
import os
import time
import argparse

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from controllers.TfhkaPyGD import tf_ve_ifpython
from controllers.pfhka import FiscalPrinter


def test_original_implementation():
    """Prueba la implementación original con comandos de estado"""
    print("\n========== PRUEBA CON IMPLEMENTACIÓN ORIGINAL ==========\n")

    printer = tf_ve_ifpython()

    print("Intentando abrir puerto COM9...")
    if printer.OpenFpctrl("COM9"):
        print("Puerto COM9 abierto correctamente.\n")
    else:
        print("Error abriendo puerto COM9.")
        return

    print("Obteniendo estado de la impresora (ENQ)...")
    result = printer.ReadFpStatus()
    print(f"Resultado: {result}")
    print(f"Estado: {printer.status}")
    print(f"Error: {printer.error}")

    printer.CloseFpctrl()
    print("\nPuerto COM9 cerrado.")


def test_new_implementation():
    """Prueba la implementación nueva con comandos de estado y flags"""
    print("\n========== PRUEBA CON IMPLEMENTACIÓN NUEVA ==========\n")

    printer = FiscalPrinter(port="COM9")
    if printer.open_port():
        print("Puerto COM9 abierto correctamente.\n")
    else:
        print("Error abriendo puerto COM9.")
        return

    print("Obteniendo estado de la impresora (ENQ)...")
    status = printer.get_printer_status()
    print(f"Resultado: {status}")

    print("\nLeyendo flags de configuración (S3)...")
    flags = printer.read_flags()
    print(f"Flags: {flags}")

    printer.close_port()
    print("\nPuerto COM9 cerrado.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test para comandos de estado y flags de impresoras fiscales")
    parser.add_argument(
        "--implementation",
        choices=["original", "new", "both"],
        default="both",
        help="Implementación a probar: original, new o both (default)",
    )

    args = parser.parse_args()

    if args.implementation in ["original", "both"]:
        test_original_implementation()

    if args.implementation in ["new", "both"]:
        test_new_implementation()
