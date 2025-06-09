#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para probar el comando S2 en la impresora virtual.
Este script abre una factura, agrega un ítem y luego consulta el estado con S2.
"""

import sys
import os
import time
import argparse

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from controllers.pfhka import FiscalPrinter


def test_s2_virtual(port):
    """Prueba el comando S2 en la impresora virtual"""
    print(f"\n========== PRUEBA DE COMANDO S2 EN PUERTO {port} ==========\n")

    printer = FiscalPrinter(port=port)

    if printer.open_port():
        print(f"Puerto {port} abierto correctamente.\n")
    else:
        print(f"Error abriendo puerto {port}.")
        return

    try:
        print("\n=== Enviando comando: Abrir factura con RIF ===")
        response = printer.send_cmd("iR*V-12345678-1")
        if not response:
            print("Error abriendo factura. Abortando prueba.")
            return
        print(f"Respuesta: {response}")

        print("\n=== Enviando comando: Establecer cliente ===")
        response = printer.send_cmd("iS*Cliente de Mostrador")
        if not response:
            print("Error estableciendo cliente. Abortando prueba.")
            return
        print(f"Respuesta: {response}")

        print("\n=== Enviando comando: Agregar ítem ===")
        response = printer.send_cmd("!000000010000001000Producto de Servicio")
        if not response:
            print("Error agregando ítem. Abortando prueba.")
            return
        print(f"Respuesta: {response}")

        print("\n=== Consultando estado del documento con S2 ===")
        status = printer.get_document_status()

        if status:
            print("\nEstado del documento obtenido:")
            print("--------------------------------------------------")

            field_order = [
                "subtotal_base",
                "subtotal_impuesto",
                "uso_futuro",
                "cantidad_articulos",
                "monto_pagar",
                "cantidad_pagos",
                "tipo_documento",
                "tipo_documento_desc",
            ]

            field_descriptions = {
                "subtotal_base": "Subtotal de bases imponibles",
                "subtotal_impuesto": "Subtotal de Impuesto",
                "uso_futuro": "Para uso futuro",
                "cantidad_articulos": "Cantidad de artículos",
                "monto_pagar": "Monto a Pagar",
                "cantidad_pagos": "Cantidad de pagos realizados",
                "tipo_documento": "Tipo de Documento",
                "tipo_documento_desc": "Descripción del Tipo de Documento",
            }

            for field in field_order:
                if field in status:
                    print(f"{field_descriptions.get(field, field)}: {status[field]}")
                else:
                    print(f"{field_descriptions.get(field, field)}: [No disponible]")

            print("--------------------------------------------------")
        else:
            print("No se pudo obtener el estado del documento.")

        input("\nPresione Enter para cerrar la factura...")
        print("\n=== Enviando comando: Cerrar factura ===")
        response = printer.send_cmd("101")
        if not response:
            print("Error cerrando factura.")
        else:
            print(f"Respuesta: {response}")

    finally:
        printer.close_port()
        print(f"\nPuerto {port} cerrado.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test para comando S2 en impresora virtual")
    parser.add_argument("--port", default="COM9", help="Puerto a usar (por defecto: COM9)")

    args = parser.parse_args()

    test_s2_virtual(args.port)
