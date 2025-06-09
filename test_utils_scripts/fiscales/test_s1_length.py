#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para probar la longitud de la respuesta del comando S1 en diferentes impresoras.
- SRP350, HSP7000, TD1125, HKA112, KUBE: 100 bytes
- SRP812, DT230, HKA80, P3100DL, PP9, ACLAS, PP9-PLUS, TD1140: 113 bytes
"""

import sys
import os
import time
import argparse

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from controllers.pfhka import FiscalPrinter


def test_s1_command(port):
    """Prueba el comando S1 y verifica la longitud de la respuesta"""
    print(f"\n========== PRUEBA DE COMANDO S1 EN PUERTO {port} ==========\n")

    printer = FiscalPrinter(port=port)

    if printer.open_port():
        print(f"Puerto {port} abierto correctamente.\n")
    else:
        print(f"Error abriendo puerto {port}.")
        return

    try:
        if not printer._handle_cts_rts():
            print("Error: No se pudo establecer control de flujo CTS/RTS")
            return

        trama = bytes([0x02]) + b"S1" + bytes([0x03])
        lrc = printer.calculate_lrc("S1")
        trama += lrc

        print(f"[TX] {trama.hex().upper()}")
        printer.serial_printer.write(trama)
        printer.serial_printer.setRTS(False)
        time.sleep(1)

        bytes_waiting = printer.serial_printer.inWaiting()
        print(f"[RX] Bytes disponibles para S1: {bytes_waiting}")

        if bytes_waiting > 1:
            response = printer.serial_printer.read(bytes_waiting)
            print(f"[RX] Respuesta S1 completa (hex): {response.hex().upper()}")

            if len(response) >= 3 and response[0] == 0x02:
                # Encontrar ETX
                etx_pos = response.find(0x03)
                if etx_pos > 0:
                    # Extraer contenido entre STX y ETX
                    content = response[1:etx_pos]

                    # Decodificar contenido
                    try:
                        content_str = content.decode("iso-8859-1")
                        print(f"[RX] Contenido S1 decodificado: {content_str}")

                        clean_content = content_str.replace("\n", "").replace("\r", "")

                        # Analizar longitud
                        print(f"\nAnálisis de longitud:")
                        print(f"- Longitud total de la respuesta: {len(response)} bytes")
                        print(f"- Longitud del contenido con saltos de línea: {len(content)} bytes")
                        print(f"- Longitud del contenido sin saltos de línea: {len(clean_content)} bytes")

                        # Contar saltos de línea
                        newlines = content_str.count("\n")
                        print(f"- Número de saltos de línea: {newlines}")

                        # Mostrar bytes en hexadecimal para análisis
                        print(f"- Primeros 20 bytes del contenido (hex): {content[:20].hex().upper()}")

                        # Determinar tipo de impresora según longitud
                        if 95 <= len(clean_content) <= 105:  # Margen de tolerancia
                            print(
                                "Longitud aproximada corresponde a: SRP350, HSP7000, TD1125, HKA112, KUBE (100 bytes)"
                            )
                        elif 108 <= len(clean_content) <= 118:  # Margen de tolerancia
                            print(
                                "Longitud aproximada corresponde a: SRP812, DT230, HKA80, P3100DL, PP9, ACLAS, PP9-PLUS, TD1140 (113 bytes)"
                            )
                        else:
                            print(f"Longitud no estándar: {len(clean_content)} bytes (sin saltos de línea)")

                        print("\nEstructura de la respuesta:")
                        lines = content_str.split("\n")

                        field_names = [
                            "Status y Número de Cajero",
                            "Subtotal de Ventas (Bs.)",
                            "Número de la Última Factura",
                            "Cantidad de Facturas Emitidas en el día",
                            "Número de la última nota de débito",
                            "Cantidad de notas de débito del día",
                            "Número de Última Nota de Crédito",
                            "Cantidad de Notas de Crédito",
                            "Número del Último Documento No Fiscal",
                            "Cantidad de Documentos No Fiscales",
                            "Contador de Cierres Diarios (Z)",
                            "Contador de Reportes de Memoria Fiscal",
                            "RIF",
                            "Número de Registro de la Máquina",
                            "Hora Actual de la Impresora",
                            "Fecha Actual de la Impresora",
                        ]

                        print("\nValidación de campos según el manual:")
                        for i, line in enumerate(lines):
                            if line and i < len(
                                field_names
                            ):  # Solo mostrar líneas no vacías y que tengan nombre de campo
                                print(f"{i + 1}. {field_names[i]}: '{line}' ({len(line)} bytes)")
                    except Exception as e:
                        print(f"Error decodificando contenido: {str(e)}")
                else:
                    print("No se encontró ETX en la respuesta")
            else:
                print("Formato de respuesta inválido")
        else:
            print("No hay suficientes bytes para leer una respuesta")
    except Exception as e:
        print(f"Error en la prueba: {str(e)}")
    finally:
        printer.close_port()
        print(f"\nPuerto {port} cerrado.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test para verificar longitud de respuesta S1")
    parser.add_argument("--ports", nargs="+", default=["COM9"], help="Puertos a probar (por defecto: COM9 para física)")

    args = parser.parse_args()

    for port in args.ports:
        test_s1_command(port)
