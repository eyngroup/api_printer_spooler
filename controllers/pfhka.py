#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
LIBRERIA PARA GESTIONAR LA IMPRESORA FISCAL TFHKA
Proyecto desarrollado por Iron Graterol
https://github.com/eyngroup/api_printer_server
"""
import time
from enum import Enum
import serial


class PrinterResponse(Enum):
    """ class """
    ACK = b"\x06"
    NAK = b"\x15"
    ENQ = b"\x05"
    STX = b"\x02"
    ETX = b"\x03"


class FiscalPrinter:
    """ class """

    def __init__(self, port="COM9"):
        self.port = port
        self.serial_printer = None
        self.timeout = 2  # Aumentar timeout
        self.wait_time = 1  # Tiempo de espera entre operaciones

    def open_port(self):
        """Abre el puerto serial"""
        try:
            self.serial_printer = serial.Serial(
                port=self.port,
                baudrate=9600,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_EVEN,
                stopbits=serial.STOPBITS_ONE,
                timeout=self.timeout,
                write_timeout=5,
                rtscts=True,  # Habilitar control de flujo RTS/CTS
            )
            print(f"Puerto {self.port} abierto correctamente.")
            return True
        except Exception as e:
            print(f"Error al abrir el puerto: {e}")
            return False

    def close_port(self):
        """Cierra el puerto serial"""
        if self.serial_printer and self.serial_printer.is_open:
            self.serial_printer.close()
            print(f"Puerto {self.port} cerrado.")

    def calculate_lrc(self, data):
        """Calcula LRC para una trama dada"""
        lrc = 0
        for byte in data.encode("ascii"):
            lrc ^= byte
        lrc ^= 0x03  # XOR con ETX
        return bytes([lrc])

    def send_command(self, command, retries=0):
        """
        Envía un comando al dispositivo fiscal y maneja la respuesta.
        Args:
            command (str): Comando a enviar.
            retries (int): Número de reintentos en caso de error.
        Returns:
            bool: True si el comando fue enviado correctamente, False en caso contrario.
        """
        print(retries)
        try:
            self.serial_printer.flushInput()
            self.serial_printer.flushOutput()

            # Construir trama
            trama = bytes([0x02]) + command.encode("ascii") + bytes([0x03])
            lrc = self.calculate_lrc(command)
            trama += lrc

            print(f"[TX] {trama.hex().upper()}")

            # Enviar comando
            self.serial_printer.write(trama)

            # Leer ACK/NAK
            ack = self.serial_printer.read(1)

            if ack == b"\x06":
                print("[RX] ACK - Comando aceptado")

                # Comandos que no generan respuesta extendida
                if command[0] in ("i", "P", "!"):  # Configuraciones y items
                    print("Comando simple: OK")
                    return True

                # Comandos fiscales con respuesta extendida
                print("Leyendo respuesta fiscal...")
                response = self._read_fiscal_response()
                return response if response else False

            if ack == b"\x15":
                print("[RX] NAK - Error en el comando")
                return False

            print(f"[RX] Respuesta inválida: {ack.hex() if ack else 'Timeout'}")
            return False

        except Exception as e:
            print(f"Error: {str(e)}")
            return False

    def _read_fiscal_response(self):
        """Lee respuesta fiscal con timeout extendido"""
        timeout = 5  # 5 segundos para impresoras lentas
        start = time.time()
        response = b""

        while (time.time() - start) < timeout:
            byte = self.serial_printer.read(1)
            if byte:
                response += byte
                if byte == b"\x03":  # ETX
                    lrc = self.serial_printer.read(1)
                    if lrc:
                        response += lrc
                        if self._validate_lrc(response):
                            print(f"[RX] Respuesta completa: {response.hex().upper()}")
                            return self._parse_fiscal_response(response)
                        print("[RX] Error LRC")
                        return False
        print("[RX] Timeout")
        return False

    def _validate_lrc(self, response):
        lrc_calculado = self.calculate_lrc(response[1:-2].decode("ascii"))[0]
        return response[-1] == lrc_calculado

    def _parse_fiscal_response(self, response):
        """Parsea respuestas de comandos fiscales según Tabla 29 del manual"""
        try:
            data = response[1:-2].decode("ascii")  # Remover STX, ETX, LRC
            print(f"Datos fiscales: {data}")
            return data
        except UnicodeDecodeError:
            return response.hex()

    def _read_full_response(self):
        """Lee toda la trama de respuesta incluyendo STX, DATA, ETX y LRC."""
        response = b""
        start_time = time.time()

        while True:
            if time.time() - start_time > self.timeout:
                print("Timeout esperando respuesta.")
                return None

            byte = self.serial_printer.read(1)
            if not byte:
                continue

            response += byte

            # Detectar fin de trama (ETX + LRC)
            if len(response) >= 4 and response[-2] == 0x03:
                lrc_received = response[-1]
                lrc_calculated = self.calculate_lrc(response[1:-2].decode("ascii"))[0]
                if lrc_received == lrc_calculated:
                    print("LRC válido.")
                    return response
                print(f"Error de LRC: Esperado {lrc_calculated}, Recibido {lrc_received}")
                return None

    def get_printer_status(self):
        """Versión mejorada con manejo robusto de ENQ"""
        try:
            self.serial_printer.flushInput()
            self.serial_printer.flushOutput()

            # Enviar ENQ
            self.serial_printer.write(b"\x05")

            # Esperar antes de leer
            time.sleep(self.wait_time)

            # Leer 4 bytes (STS1 + STS2 + ETX + LRC)
            status_data = self.serial_printer.read(5)

            if len(status_data) == 5:
                sts1 = status_data[1]  # Segundo byte es STS1
                sts2 = status_data[2]  # Tercer byte es STS2
                return self._parse_status(sts1, sts2)

            print(f"Respuesta incompleta: {status_data}")
            return {"status": "Desconocido", "error": "Respuesta inválida"}

        except Exception as e:
            print(f"Error ENQ: {str(e)}")
            return None

    def _parse_status(self, sts1, sts2):
        # Mapeo actualizado según Tabla 7 y 8 del manual
        status_codes = {
            0x40: "Modo Entrenamiento y en Espera",
            0x60: "Modo Fiscal y en Espera",
            0x61: "Documento fiscal abierto",
            0x68: "Memoria Fiscal llena",
        }

        error_codes = {
            0x40: "Sin errores",
            0x41: "Papel agotado",
            0x42: "Error mecánico",
            0x43: "Papel agotado + error mecánico",
            0x60: "Error fiscal",
            0x64: "Error en la memoria fiscal",
            0x6C: "Memoria fiscal llena",
        }

        return {
            "status": status_codes.get(sts1, f"Estado desconocido (0x{sts1:02X})"),
            "error": error_codes.get(sts2, f"Error desconocido (0x{sts2:02X})"),
        }

    def read_flags(self, flags_to_read=None):
        """
        Lee los flags de configuración según Tabla 72 del manual (página 79)
        Args:
            flags_to_read (list): Lista de flags a leer (ej: [21, 50])
        Returns:
            dict: {flag: valor} o None si hay error
        """
        if flags_to_read is None:
            flags_to_read = [21, 50, 30, 43]

        try:
            self.serial_printer.flushInput()
            self.serial_printer.write(b"\x02S3\x03")  # Comando S3
            time.sleep(0.5)
            response = self._read_full_response()

            if response and len(response) >= 150:  # Longitud mínima S3
                data = response[1:-2].decode("ascii")  # Remover STX, ETX, LRC
                flags = {}

                # Mapeo de posiciones según manual (página 79)
                flag_positions = {
                    21: (146, 2),  # Posición 146-147, 2 dígitos
                    50: (26, 2),  # Posición 26-27
                    30: (20, 2),  # Posición 20-21
                    43: (88, 2),  # Posición 88-89
                }

                for flag in flags_to_read:
                    if flag in flag_positions:
                        start, length = flag_positions[flag]
                        flags[flag] = data[start : start + length]

                return flags
            return None

        except Exception as e:
            print(f"Error leyendo flags: {str(e)}")
            return None

    def get_printer_model(self):
        """
        Lee el modelo de impresora usando comando SV (Status SV)
        Returns:
            str: Modelo detectado o None
        """
        try:
            response = self.send_command("SV")
            print(response)
            if response and len(response) >= 3:
                model_code = str(response)[:3] if response else ""
                model_map = {
                    "Z7C": "HKA-80",
                    "Z7A": "HKA-112",
                    "Z1A": "SRP-270",
                    "Z1B": "SRP-350",
                    "Z1E": "SRP-280",
                    "Z1F": "SRP-812",
                    "ZPA": "HSP7000",
                    "Z6A": "TALLY 1125",
                    "Z6B": "DT-230",
                    "Z6C": "TALLY 1140",
                    "ZYA": "P3100DL",
                    "ZZH": "PP9",
                    "ZZP": "PP9-PLUS",
                } # Tabla 27 (página 31)
                return model_map.get(model_code, "Desconocido")
            return None
        except Exception as e:
            print(f"Error detectando modelo: {str(e)}")
            return None


# Uso mejorado
if __name__ == "__main__":
    printer = FiscalPrinter(port="COM9")

    if printer.open_port():
        responde = printer.get_printer_model()
        print(responde)

        # responde = printer.read_flags([21, 50])
        # print(responde)

        # # 1. Configurar Flags esenciales
        # printer.send_command("PJ5001")  # Flag 50=01
        # print("1")
        # # 2. Configurar encabezados
        # printer.send_command("iR*J-123456789")  # RIF
        # print("2")
        # printer.send_command("iS*Tienda Demo")  # Razón Social
        # print("3")
        # # 3. Transacción demo
        # printer.send_command("!0000000100000001000Producto 1")  # Item
        # print("4")
        # printer.send_command("101")  # Pago completo 100.00 Bs
        # print("5")
        # printer.send_command("199")  # Cierre
        # print("6")

        printer.close_port()
