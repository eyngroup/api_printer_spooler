#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para probar la longitud de la respuesta del comando S2 en la impresora virtual.
NOTA: Este comando solo funciona cuando hay un documento fiscal abierto.
"""

import sys
import os
import time
import argparse

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from controllers.pfhka import FiscalPrinter


def test_s2_command(port):
    """Prueba el comando S2 y verifica la longitud de la respuesta"""
    print(f"\n========== PRUEBA DE COMANDO S2 EN PUERTO {port} ==========\n")
    print("NOTA: Este comando solo funciona cuando hay un documento fiscal abierto.")
    print("      Si no hay documento abierto, es normal que falle o devuelva datos vacíos.\n")

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

        trama = bytes([0x02]) + b"S2" + bytes([0x03])
        lrc = printer.calculate_lrc("S2")
        trama += lrc

        print(f"[TX] {trama.hex().upper()}")
        printer.serial_printer.write(trama)
        printer.serial_printer.setRTS(False)
        time.sleep(1)

        # Leer todos los bytes disponibles
        bytes_waiting = printer.serial_printer.inWaiting()
        print(f"[RX] Bytes disponibles para S2: {bytes_waiting}")

        if bytes_waiting > 1:
            # Leer toda la respuesta
            response = printer.serial_printer.read(bytes_waiting)
            print(f"[RX] Respuesta S2 completa (hex): {response.hex().upper()}")

            # Verificar formato básico
            if len(response) >= 3 and response[0] == 0x02:
                # Encontrar ETX
                etx_pos = response.find(0x03)
                if etx_pos > 0:
                    # Extraer contenido entre STX y ETX
                    content = response[1:etx_pos]

                    # Decodificar contenido
                    try:
                        content_str = content.decode("iso-8859-1")
                        print(f"[RX] Contenido S2 decodificado: {content_str}")

                        # Limpiar contenido (eliminar saltos de línea)
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

                        # Analizar estructura de la respuesta
                        print("\nEstructura de la respuesta:")
                        lines = content_str.split("\n")
                        for i, line in enumerate(lines):
                            if line:  # Solo mostrar líneas no vacías
                                print(f"Línea {i + 1}: '{line}' ({len(line)} bytes)")
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
    parser = argparse.ArgumentParser(description="Test para verificar longitud de respuesta S2")
    parser.add_argument("--port", default="COM9", help="Puerto a usar (por defecto: COM9)")

    args = parser.parse_args()

    test_s2_command(args.port)
