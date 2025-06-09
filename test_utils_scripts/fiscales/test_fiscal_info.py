#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para probar los métodos get_fiscal_info (S1) y get_document_status (S2)
de la clase FiscalPrinter.
"""

import sys
import os
import argparse

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from controllers.pfhka import FiscalPrinter


def test_fiscal_info(port):
    """Prueba el método get_fiscal_info (S1)"""
    print("\n========== PRUEBA DE INFORMACIÓN FISCAL (S1) ==========\n")

    printer = FiscalPrinter(port=port)

    if printer.open_port():
        print(f"Puerto {port} abierto correctamente.")
    else:
        print(f"Error abriendo puerto {port}.")
        return

    try:
        print("\nObteniendo información fiscal (S1)...")
        info = printer.get_fiscal_info()

        if info:
            print("\nInformación fiscal obtenida:")
            print("--------------------------------------------------")

            field_order = [
                "status_cajero",
                "subtotal_ventas",
                "ultima_factura",
                "facturas_dia",
                "ultima_nota_debito",
                "notas_debito_dia",
                "ultima_nota_credito",
                "notas_credito_dia",
                "ultimo_doc_no_fiscal",
                "docs_no_fiscales_dia",
                "contador_cierres_z",
                "contador_reportes_memoria",
                "rif",
                "registro_maquina",
                "hora_impresora",
                "fecha_impresora",
            ]

            field_descriptions = {
                "status_cajero": "Status y Número de Cajero",
                "subtotal_ventas": "Subtotal de Ventas (Bs.)",
                "ultima_factura": "Número de la Última Factura",
                "facturas_dia": "Cantidad de Facturas Emitidas en el día",
                "ultima_nota_debito": "Número de la última nota de débito",
                "notas_debito_dia": "Cantidad de notas de débito del día",
                "ultima_nota_credito": "Número de Última Nota de Crédito",
                "notas_credito_dia": "Cantidad de Notas de Crédito",
                "ultimo_doc_no_fiscal": "Número del Último Documento No Fiscal",
                "docs_no_fiscales_dia": "Cantidad de Documentos No Fiscales",
                "contador_cierres_z": "Contador de Cierres Diarios (Z)",
                "contador_reportes_memoria": "Contador de Reportes de Memoria Fiscal",
                "rif": "RIF",
                "registro_maquina": "Número de Registro de la Máquina",
                "hora_impresora": "Hora Actual de la Impresora (HHMMSS)",
                "fecha_impresora": "Fecha Actual de la Impresora (DDMMAA)",
            }

            for field in field_order:
                if field in info:
                    print(f"{field_descriptions.get(field, field)}: {info[field]}")
                else:
                    print(f"{field_descriptions.get(field, field)}: [No disponible]")

            print("--------------------------------------------------")
        else:
            print("No se pudo obtener información fiscal.")
    finally:
        printer.close_port()
        print(f"\nPuerto {port} cerrado.")


def test_document_status(port):
    """Prueba el método get_document_status (S2)"""
    print("\n========== PRUEBA DE ESTADO DE DOCUMENTO (S2) ==========\n")
    print("NOTA: Este comando solo funciona cuando hay un documento fiscal abierto.")
    print("      Si no hay documento abierto, es normal que falle o devuelva datos vacíos.\n")

    printer = FiscalPrinter(port=port)

    if printer.open_port():
        print(f"Puerto {port} abierto correctamente.")
    else:
        print(f"Error abriendo puerto {port}.")
        return

    try:
        print("\nObteniendo estado del documento en curso (S2)...")
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
    finally:
        printer.close_port()
        print(f"\nPuerto {port} cerrado.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test para métodos S1 y S2")
    parser.add_argument("--port", default="COM9", help="Puerto a usar (por defecto: COM9)")
    parser.add_argument(
        "--test",
        choices=["fiscal", "document", "both"],
        default="both",
        help="Test a ejecutar: fiscal (S1), document (S2) o both (ambos)",
    )

    args = parser.parse_args()

    if args.test == "fiscal" or args.test == "both":
        test_fiscal_info(args.port)

    if args.test == "document" or args.test == "both":
        test_document_status(args.port)
