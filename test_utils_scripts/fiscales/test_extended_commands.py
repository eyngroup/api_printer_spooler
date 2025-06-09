#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import time
import argparse

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from controllers.TfhkaPyGD import tf_ve_ifpython
from controllers.pfhka import FiscalPrinter


def test_original_implementation():
    """Implementación original con comandos extendidos"""
    print("\n========== PRUEBA CON IMPLEMENTACIÓN ORIGINAL ==========\n")

    printer = tf_ve_ifpython()

    print("Intentando abrir puerto COM3...")
    if printer.OpenFpctrl("COM3"):
        print("Puerto COM3 abierto correctamente.\n")
    else:
        print("Error abriendo puerto COM3.")
        return

    print("Enviando comando SV (modelo)...")
    result = printer.SendCmd("SV")
    print(f"Resultado: {result}")

    # # Probar comando I0X (estado fiscal)
    # print("\nEnviando comando I0X (estado fiscal)...")
    # result = printer.SendCmd("I0X")
    # print(f"Resultado: {result}")

    printer.CloseFpctrl()
    print("\nPuerto COM3 cerrado.")


def test_new_implementation():
    """Prueba la implementación nueva con comandos extendidos"""
    print("\n========== PRUEBA CON IMPLEMENTACIÓN NUEVA ==========\n")

    printer = FiscalPrinter(port="COM3")

    if printer.open_port():
        print("Puerto COM3 abierto correctamente.\n")
    else:
        print("Error abriendo puerto COM3.")
        return

    print("Enviando comando SV (modelo)...")
    result = printer.send_cmd("SV")
    print(f"Resultado: {result}")

    # # Probar comando I0X (estado fiscal)
    # print("\nEnviando comando I0X (estado fiscal)...")
    # result = printer.send_command("I0X")
    # print(f"Resultado: {result}")

    print("\nObteniendo modelo con get_printer_model()...")
    model = printer.get_printer_model()
    print(f"Modelo detectado: {model}")

    printer.close_port()
    print("\nPuerto COM3 cerrado.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test para comandos extendidos de impresoras fiscales")
    parser.add_argument(
        "--impl",
        choices=["original", "nueva", "ambas"],
        default="ambas",
        help="Implementación a probar (original, nueva o ambas)",
    )

    args = parser.parse_args()

    if args.impl == "original":
        test_original_implementation()
    elif args.impl == "nueva":
        test_new_implementation()
    else:
        test_original_implementation()
        test_new_implementation()
