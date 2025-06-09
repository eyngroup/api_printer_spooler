#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script simple para probar el método status_if de la impresora PNP
"""

import os
import sys
import binascii

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from controllers.pfpnp import FiscalPrinter


class EstadoImpresora:
    Printer = FiscalPrinter()
    PORT = "COM96" 

    try:
        print("=== PRUEBA DE ESTADO CON IMPLEMENTACIÓN NUEVA (pfpnp.py) ===")
        PortOpen = Printer.open_port()
        if PortOpen:
            print("Puerto: " + Printer.port + " ABIERTO")

            print("\n=== Enviando comando: Estado Normal ===")
            resultado = Printer.status_if("N")
            print(f"Respuesta: {resultado}")
            if resultado is not False and isinstance(resultado, bytes):
                print(f"Respuesta en hexadecimal: {binascii.hexlify(resultado).decode()}")
                campos = resultado.split(b"|")
                print("Campos de respuesta:")
                for i, campo in enumerate(campos):
                    print(f"  Campo {i}: {campo}")

            print("\n=== Enviando comando: Estado Extendido ===")
            resultado = Printer.status_if("E")
            print(f"Respuesta: {resultado}")
            if resultado is not False and isinstance(resultado, bytes):
                print(f"Respuesta en hexadecimal: {binascii.hexlify(resultado).decode()}")
                # Mostrar campos separados por |
                campos = resultado.split(b"|")
                print("Campos de respuesta:")
                for i, campo in enumerate(campos):
                    print(f"  Campo {i}: {campo}")

            print("\n=== Probando método _read_status ===")
            resultado = Printer._read_status("X")  # Debería usar status_if con "X"
            print(f"Respuesta: {resultado}")

            Printer.close_port()
            print("\nPuerto cerrado")
        else:
            print(f"No se pudo abrir el puerto {Printer.port}")
    except Exception as e:
        print("OCURRIO UNA EXCEPCION: \nDetalles del Error: \n", e)


if __name__ == "__main__":
    EstadoImpresora()
