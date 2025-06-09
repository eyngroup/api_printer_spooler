#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de prueba para la clase PnP del archivo PnP.py - Factura simple
"""

import os
import sys
import time
import binascii

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from controllers.PnP import PnP


class FacturaSimple_Original:
    Printer = PnP()
    PORT = "COM96" 

    try:
        print("=== PRUEBA DE FACTURA CON IMPLEMENTACIÓN ORIGINAL (PnP.py) ===")
        PortOpen = Printer.OpenPnP(PORT)
        if PortOpen:
            print("Puerto: " + PORT + " ABIERTO")

            print("\n=== Enviando comando: Abre Factura (@|Nombre|Rif) ===")

            # Para NOTA DE CREDITO: Printer.SendCmd("@|PRUEBA|J000000000|00000001|EOG0123654|05052023|150400|D")
            # Para FACTURA: Printer.SendCmd("@|Nombre Cliente|J000000000| | | | |T")

            comando = "@|Nombre|Rif|||||T"
            comando_formateado = Printer._AssembleQueryToSend(comando)
            print(f"Comando formateado: {comando_formateado}")
            print(f"Comando en hexadecimal: {binascii.hexlify(comando_formateado.encode()).decode()}")
            resultado = Printer.SendCmd(comando)
            print(f"Respuesta: {resultado}")

            print("\n=== Enviando comando: Renglón (B|Producto|1000|1000|1600|M) ===")
            comando = "B|Producto|1000|1000|1600|M"
            comando_formateado = Printer._AssembleQueryToSend(comando)
            print(f"Comando formateado: {comando_formateado}")
            print(f"Comando en hexadecimal: {binascii.hexlify(comando_formateado.encode()).decode()}")
            resultado = Printer.SendCmd(comando)
            print(f"Respuesta: {resultado}")

            print("\n=== Enviando comando: Texto Fiscal (A|Texto adicional) ===")
            comando = "A|Texto adicional"
            comando_formateado = Printer._AssembleQueryToSend(comando)
            print(f"Comando formateado: {comando_formateado}")
            print(f"Comando en hexadecimal: {binascii.hexlify(comando_formateado.encode()).decode()}")
            resultado = Printer.SendCmd(comando)
            print(f"Respuesta: {resultado}")

            print("\n=== Enviando comando: Cierre (E|T) ===")
            comando = "E|T"
            comando_formateado = Printer._AssembleQueryToSend(comando)
            print(f"Comando formateado: {comando_formateado}")
            print(f"Comando en hexadecimal: {binascii.hexlify(comando_formateado.encode()).decode()}")
            resultado = Printer.SendCmd(comando)
            print(f"Respuesta: {resultado}")

            Printer.ClosePnP()
            print("\nPuerto cerrado")

        else:
            print(f"No se pudo abrir el puerto {PORT}")
    except Exception as e:
        print("OCURRIO UNA EXCEPCION: \nDetalles del Error: \n", e)


if __name__ == "__main__":
    FacturaSimple_Original()
