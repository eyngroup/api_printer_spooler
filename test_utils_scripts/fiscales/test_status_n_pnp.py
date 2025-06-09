#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script simple para probar el comando de estado normal (8|V) de la impresora PNP
"""

import os
import sys
import binascii

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from controllers.pfpnp import FiscalPrinter


class EstadoNormalImpresora:
    Printer = FiscalPrinter()
    PORT = "COM96"

    try:
        print("=== PRUEBA DE ESTADO NORMAL (8|V) CON IMPLEMENTACIÓN MEJORADA ===")
        PortOpen = Printer.open_port()
        if PortOpen:
            print("Puerto: " + Printer.port + " ABIERTO")

            print("\n=== Enviando comando: Estado Normal (8|V) ===")
            resultado_raw = Printer.serial_printer.flushInput()
            Printer.serial_printer.flushOutput()

            cmd_bytes = Printer._build_cmd("8|V")
            Printer.serial_printer.write(cmd_bytes)
            print(f"Comando enviado (hex): {cmd_bytes.hex()}")

            print("\n=== Respuesta byte a byte ===")
            respuesta_bytes = b""
            timeout_count = 0
            max_timeout = 30

            while timeout_count < max_timeout:
                byte = Printer.serial_printer.read(1)
                if byte:
                    respuesta_bytes += byte
                    print(f"Byte recibido: {byte.hex()} (ASCII: {byte if byte >= b' ' and byte <= b'~' else b'.'!r})")
                    # Si ETX (0x03), esperar más para el BCC
                    if byte == b"\x03":
                        print("ETX encontrado, esperando BCC...")
                        # Leer 4 bytes más para el BCC
                        for _ in range(4):
                            bcc_byte = Printer.serial_printer.read(1)
                            if bcc_byte:
                                respuesta_bytes += bcc_byte
                                print(
                                    f"Byte BCC: {bcc_byte.hex()} (ASCII: {bcc_byte if bcc_byte >= b' ' and bcc_byte <= b'~' else b'.'!r})"
                                )
                        break
                else:
                    timeout_count += 1
                    import time

                    time.sleep(0.1)

            print("\n=== Respuesta completa ===")
            print(f"Respuesta (hex): {respuesta_bytes.hex()}")

            print("\n=== Campos según el manual ===")

            # Buscar STX, SEC, CMD
            stx_pos = respuesta_bytes.find(b"\x02")
            if stx_pos >= 0:
                print(f"STX: {respuesta_bytes[stx_pos : stx_pos + 1].hex()}")
                sec = respuesta_bytes[stx_pos + 1 : stx_pos + 2]
                print(f"SEC: {sec.hex()} (ASCII: {sec!r})")
                cmd = respuesta_bytes[stx_pos + 2 : stx_pos + 3]
                print(f"CMD: {cmd.hex()} (ASCII: {cmd!r})")

                # Separar los campos por 0x1C
                campos_raw = respuesta_bytes[stx_pos + 3 :].split(b"\x1c")
                print(f"Número de campos separados por 0x1C: {len(campos_raw)}")

                for i, campo in enumerate(campos_raw):
                    # Eliminar ETX y BCC si están presentes
                    if b"\x03" in campo:
                        etx_pos = campo.find(b"\x03")
                        campo_limpio = campo[:etx_pos]
                        bcc = campo[etx_pos + 1 :]
                        print(f"Campo {i + 1}: {campo_limpio!r} (hex: {campo_limpio.hex()})")
                        print(f"ETX: {campo[etx_pos : etx_pos + 1].hex()}")
                        print(f"BCC: {bcc!r} (hex: {bcc.hex()})")
                    else:
                        print(f"Campo {i + 1}: {campo!r} (hex: {campo.hex()})")

            resultado = Printer.send_cmd("8|V")
            print("\n=== Respuesta procesada con send_command ===")
            print(f"Respuesta: {resultado}")

            if resultado and isinstance(resultado, bytes):
                # Mostrar campos separados por |
                campos = resultado.split(b"|")
                print(f"Número de campos: {len(campos)}")
                print("Campos de respuesta:")
                for i, campo in enumerate(campos):
                    if campo:  # Solo mostrar campos no vacíos
                        print(f"  Campo {i}: {campo!r}")

            Printer.close_port()
            print("\nPuerto cerrado")
        else:
            print(f"No se pudo abrir el puerto {Printer.port}")
    except Exception as e:
        import traceback

        print("OCURRIO UNA EXCEPCION: \nDetalles del Error: \n", e)
        print(traceback.format_exc())


if __name__ == "__main__":
    EstadoNormalImpresora()
