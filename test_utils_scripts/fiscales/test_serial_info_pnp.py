#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script simple para probar el método serial_info de la impresora PNP
"""

import os
import sys
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from controllers.pfpnp import FiscalPrinter


class InfoSerialImpresora:
    Printer = FiscalPrinter()
    PORT = "COM96" 

    try:
        print("=== PRUEBA DE INFORMACIÓN SERIAL CON IMPLEMENTACIÓN NUEVA (pfpnp.py) ===")
        PortOpen = Printer.open_port()
        if PortOpen:
            print("Puerto: " + Printer.port + " ABIERTO")

            print("\n=== Enviando comando: Información Serial ===")
            resultado = Printer.serial_info()

            print("\nRespuesta:")
            for key, value in resultado.items():
                if key == "raw_response" and isinstance(value, bytes):
                    print(f"{key}: {value}")
                else:
                    print(f"{key}: {value}")

            print("\nCampos individuales:")
            print(f"Código de respuesta: {resultado.get('codigo_respuesta', 'N/A')}")
            print(f"Status impresora: {resultado.get('status_impresora', 'N/A')}")
            print(f"Status fiscal: {resultado.get('status_fiscal', 'N/A')}")
            print(f"Serial: {resultado.get('serial', 'N/A')}")
            print(f"RIF: {resultado.get('rif', 'N/A')}")
            print(f"Versión: {resultado.get('version', 'N/A')}")
            print(f"Memoria fiscal: {resultado.get('memoria_fiscal', 'N/A')}")
            print(f"Número de registro: {resultado.get('numero_registro', 'N/A')}")

            Printer.close_port()
            print("\nPuerto cerrado")
        else:
            print(f"No se pudo abrir el puerto {Printer.port}")
    except Exception as e:
        print("OCURRIO UNA EXCEPCION: \nDetalles del Error: \n", e)


if __name__ == "__main__":
    InfoSerialImpresora()
