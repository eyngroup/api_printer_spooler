#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time
import binascii

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from controllers.PnP import PnP


class ReporteX_Original:
    Printer = PnP()
    PORT = "COM96"

    try:
        print("=== PRUEBA CON IMPLEMENTACIÓN ORIGINAL (PnP.py) ===")
        PortOpen = Printer.OpenPnP(PORT)
        if PortOpen:
            print("Puerto: " + PORT + " ABIERTO")
            print("Enviando comando para Reporte X: '9|X|T'")

            comando_formateado = Printer._AssembleQueryToSend("9|X|T")
            print(f"Comando formateado: {comando_formateado}")
            print(f"Comando en hexadecimal: {binascii.hexlify(comando_formateado.encode()).decode()}")

            resultado = Printer.SendCmd("9|X|T")
            print(f"Respuesta: {resultado}")

            Printer.ClosePnP()
            print("Puerto cerrado")
        else:
            print(f"No se pudo abrir el puerto {PORT}")
    except Exception as e:
        print("OCURRIO UNA EXCEPCION: \nDetalles del Error: \n", e)


if __name__ == "__main__":
    ReporteX_Original()
