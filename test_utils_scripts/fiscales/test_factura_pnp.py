#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de prueba para la librería pfpnp.py que simula una factura simple
"""

import os
import sys
import time
import binascii

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from controllers.pfpnp import FiscalPrinter


class FacturaSimple:
    Printer = FiscalPrinter()
    PORT = "COM96"
    PortOpen = False
    Respuesta = None

    try:
        print("=== PRUEBA DE FACTURA CON IMPLEMENTACIÓN NUEVA (pfpnp.py) ===")
        PortOpen = Printer.open_port()
        if PortOpen:
            print("Puerto: " + Printer.port + " ABIERTO")

            print("\n=== Enviando comando: Abre Factura ===")
            # Para NOTA DE CREDITO: Printer.send_command("@|PRUEBA|J000000000|00000001|EOG0123654|05052023|150400|D")
            # Para FACTURA: Printer.send_command("@|Nombre Cliente|J000000000| | | | |T")

            comando = "@|Nombre|Rif|||||T"
            comando_formateado = Printer._build_cmd(comando)
            print(f"Comando formateado (bytes): {comando_formateado}")
            print(f"Comando en hexadecimal: {binascii.hexlify(comando_formateado).decode()}")
            print(f"Secuencia utilizada: {Printer._last_sequence} (hex: {hex(Printer._last_sequence)})")
            Respuesta = Printer.send_cmd(comando)
            print(f"Respuesta: {Respuesta}")

            print("\n=== Enviando comando: Renglón ===")
            comando = "B|Producto|1000|1000|1600|M"
            comando_formateado = Printer._build_cmd(comando)
            print(f"Comando formateado (bytes): {comando_formateado}")
            print(f"Comando en hexadecimal: {binascii.hexlify(comando_formateado).decode()}")
            print(f"Secuencia utilizada: {Printer._last_sequence} (hex: {hex(Printer._last_sequence)})")
            Respuesta = Printer.send_cmd(comando)
            print(f"Respuesta: {Respuesta}")

            print("\n=== Enviando comando: Texto Fiscal ===")
            comando = "A|Texto adicional"
            comando_formateado = Printer._build_cmd(comando)
            print(f"Comando formateado (bytes): {comando_formateado}")
            print(f"Comando en hexadecimal: {binascii.hexlify(comando_formateado).decode()}")
            print(f"Secuencia utilizada: {Printer._last_sequence} (hex: {hex(Printer._last_sequence)})")
            Respuesta = Printer.send_cmd(comando)
            print(f"Respuesta: {Respuesta}")

            print("\n=== Enviando comando: Cierre ===")
            comando = "E|T"
            comando_formateado = Printer._build_cmd(comando)
            print(f"Comando formateado (bytes): {comando_formateado}")
            print(f"Comando en hexadecimal: {binascii.hexlify(comando_formateado).decode()}")
            print(f"Secuencia utilizada: {Printer._last_sequence} (hex: {hex(Printer._last_sequence)})")
            Respuesta = Printer.send_cmd(comando)
            print(f"Respuesta: {Respuesta}")

            Printer.close_port()

            print("\nPuerto cerrado")

        else:
            print("NO SE PUDO ESTABLECER COMUNICACION CON LA IMPRESORA")
            print("PUERTO: " + Printer.port + " CERRADO")

    except Exception as e:
        print("OCURRIO UNA EXCEPCION: \nDetalles del Error: \n", type(e).__name__)
        print(e)


if __name__ == "__main__":
    FacturaSimple()
