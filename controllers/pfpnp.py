#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright © 2024, Iron Graterol
Licensed under the GNU Affero General Public License, version 3 or later.

LIBRERIA PARA GESTIONAR LA IMPRESORA FISCAL PNP
Proyecto desarrollado por Iron Graterol
https://github.com/eyngroup/api_printer_server
"""

import time
from typing import Optional

import serial


class FiscalPrinter:
    """Clase mejorada para manejar la comunicación con una impresora fiscal mediante puerto serial."""

    # Constantes para caracteres de control
    STX = b"\x02"  # Inicio de texto
    ETX = b"\x03"  # Fin de texto
    SEP = b"\x1c"  # Separador de campo
    DEL = b"\x7f"  # Carácter de control para cierre

    # Constantes para comandos
    CMD_STATUS = b"\x02 8\x1c"  # Comando de estado
    CMD_REPORT_X = b"\x02 9\x1cX\x1cT\x03"  # Reporte X
    CMD_REPORT_Z = b"\x02 9\x1cZ\x1cT\x03"  # Reporte Z
    CMD_SERIAL_INFO = b"\x02\x45\x80\x03"  # Información de serial

    # Comandos para documentos NO fiscales
    CMD_OPEN_NONFISCAL = b"\x48"  # Abrir documento no fiscal
    CMD_PRINT_NONFISCAL = b"\x49"  # Imprimir línea en documento no fiscal
    CMD_CLOSE_NONFISCAL = b"\x4a"  # Cerrar documento no fiscal

    # Comandos para documentos fiscales
    CMD_OPEN_FISCAL = b"\x40"  # Abrir documento fiscal
    CMD_ADD_FISCAL_TEXT = b"\x41"  # Agregar texto fiscal
    CMD_ADD_FISCAL_ITEM = b"\x42"  # Agregar ítem fiscal
    CMD_GET_SUBTOTAL = b"\x43"  # Obtener subtotal
    CMD_CLOSE_FISCAL = b"\x45"  # Cerrar documento fiscal

    # Calificadores de documento fiscal
    DOC_TYPE_INVOICE = b"\x54"  # Factura fiscal
    DOC_TYPE_CREDIT_NOTE = b"\x44"  # Nota de crédito

    # Calificadores de cierre fiscal
    CLOSE_PARTIAL = b"\x41"  # Cierre parcial
    CLOSE_PARTIAL_IGTF = b"\x42"  # Cierre parcial con IGTF
    CLOSE_TOTAL = b"\x54"  # Cierre total
    CLOSE_TOTAL_IGTF = b"\x55"  # Cierre total con IGTF

    # Calificadores de operación
    OP_ADD = b"\x4d"  # Suma (M)
    OP_SUB = b"\x6d"  # Resta (m)

    # Constantes para secuencia
    SEQ_MIN = 0x20  # Valor mínimo de secuencia (32 decimal)
    SEQ_MAX = 0x7F  # Valor máximo de secuencia (127 decimal)

    status_connection = False
    message_connection = ""
    message_command = ""
    time_delay = 0.8
    is_debug = False

    def __init__(self, port: str):
        self.port = port
        self.serial_connection: Optional[serial.Serial] = None
        self._last_sequence = self.SEQ_MAX  # Iniciar al máximo para que el primer comando use SEQ_MIN

    @staticmethod
    def _calculate_bcc(data: bytes) -> str:
        """Calcula el BCC para los datos dados"""
        bcc = 0
        for byte in data:
            bcc += byte
        return f"{bcc:04X}"  # Convertir a string hexadecimal de 4 caracteres

    def open_port(self) -> bool:
        """
        Abre el puerto serial.
        Returns:
            bool: True si se abrió correctamente, False en caso contrario
        """
        try:
            self.serial_connection = serial.Serial(
                port=self.port,
                baudrate=9600,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=2,
                write_timeout=5,
                xonxoff=False,
                rtscts=False,
                dsrdtr=False,
            )

            # buffers de lectura/escritura
            self.serial_connection.set_buffer_size(rx_size=4096, tx_size=4096)

            if self.serial_connection.is_open:
                self.status_connection = True
                if self.is_debug:
                    print(f"Puerto {self.port} abierto correctamente.")
                return True
            print(f"No se pudo abrir el puerto {self.port}.")
            return False

        except Exception as e:
            print(f"Error al abrir el puerto {self.port}: {str(e)}")
            return False

    def close_port(self):
        """Cierra el puerto serial"""
        if self.status_connection:
            self.serial_connection.close()
            if self.is_debug:
                print(f"Puerto {self.port} cerrado correctamente.")
            self.status_connection = False

    def _read_response(self) -> bytes:
        """
        Lee la respuesta completa de la impresora fiscal.
        La respuesta debe comenzar con STX y terminar con ETX + BCC.
        Returns:
            bytes: Respuesta completa de la impresora
        """
        buffer = bytearray()
        timeout_counter = 0
        max_timeout = 20  # 2 segundos máximo de espera

        # Esperar a tener datos
        while self.serial_connection.in_waiting == 0:
            time.sleep(0.5)
            timeout_counter += 1
            if timeout_counter >= max_timeout:
                raise TimeoutError("No se recibió respuesta de la impresora")

        # Leer todos los bytes
        time.sleep(0.5)
        while self.serial_connection.in_waiting > 0:
            buffer.extend(self.serial_connection.read(self.serial_connection.in_waiting))

        if not buffer:
            raise ValueError("No se recibieron datos")

        if self.ETX not in buffer:  # Buscamos STX y ETX
            raise ValueError(f"Respuesta no contiene ETX: {buffer}")

        etx_pos = buffer.index(self.ETX)
        if len(buffer) < etx_pos + 5:  # Aseguramos que tenemos 4 bytes después del ETX para el BCC
            raise ValueError(f"Respuesta no contiene BCC completo: {buffer}")

        return bytes(buffer)

    @staticmethod
    def _printer_status(status: bytes) -> dict:
        """
        Parsea el estado de la impresora (4 bytes en hexadecimal)
        Args:
            status: Estado de la impresora en bytes
        Returns:
            dict: Diccionario con los estados parseados
        """
        status_int = int.from_bytes(status, "big")
        return {
            "error_impresora": bool(status_int & (1 << 2)),
            "fuera_linea": bool(status_int & (1 << 3)),
            "sin_papel": bool(status_int & (1 << 14)),
            "error_general": bool(status_int & (1 << 15)),
        }

    @staticmethod
    def _fiscal_status(status: bytes) -> dict:
        """
        Parsea el estado fiscal (4 bytes en hexadecimal)
        Args:
            status: Estado fiscal en bytes
        Returns:
            dict: Diccionario con los estados parseados
        """
        status_int = int.from_bytes(status, "big")
        return {
            "error_memoria_fiscal": bool(status_int & (1 << 0)),
            "error_memoria_trabajo": bool(status_int & (1 << 1)),
            "comando_desconocido": bool(status_int & (1 << 3)),
            "datos_invalidos": bool(status_int & (1 << 4)),
            "comando_invalido": bool(status_int & (1 << 5)),
            "desborde_totales": bool(status_int & (1 << 6)),
            "memoria_fiscal_llena": bool(status_int & (1 << 7)),
            "memoria_fiscal_casi_llena": bool(status_int & (1 << 8)),
            "necesita_cierre_z": bool(status_int & (1 << 11)),
            "factura_fiscal_abierta": bool(status_int & (1 << 12)),
            "documento_no_fiscal_abierto": bool(status_int & (1 << 13)),
        }

    def _process_response(self, response: bytes, command: bytes) -> list:
        """
        Procesa la respuesta de la impresora según el tipo de comando.
        Args:
            response: Respuesta completa de la impresora en bytes
            command: Comando que generó la respuesta
        Returns:
            list: Lista de campos extraídos
        """
        try:
            if command[1:2] == b"9":
                stx_pos = response.rindex(self.STX)
                response = response[stx_pos:]

            etx_pos = response.index(self.ETX)

            if command[2:3] in [b"\x48", b"\x49", b"\x4a"]:
                content = response[etx_pos + 1 : response.rindex(self.ETX)]
                fields = [field.decode("iso-8859-1") for field in content.split(self.SEP) if field]
                if not fields:
                    fields = ["0080"]  # Código de éxito por defecto
                return fields

            if command[2:3] == b"\x80":
                content = response[etx_pos + 1 : response.rindex(self.ETX)]
            else:
                first_sep = response.index(self.SEP)
                content = response[first_sep:etx_pos]

            fields = [field.decode("iso-8859-1") for field in content.split(self.SEP) if field]

            if not fields:
                raise ValueError("No se encontraron campos en la respuesta")

            return fields

        except Exception as e:
            raise ValueError(f"Error procesando respuesta: {str(e)}") from e

    def send_command(self, cmd: bytes) -> dict:
        """
        Envía un comando a la impresora fiscal y espera la respuesta.
        Args:
            cmd: Cadena del comando a enviar, formateada según el protocolo.
        Returns:
            dict: Diccionario con la respuesta parseada
        """
        if self.status_connection:
            try:
                if self.is_debug:
                    print(f"Comando recibido: {cmd}")
                bcc = self._calculate_bcc(cmd)
                cmd_bcc = cmd + bcc.encode("iso-8859-1")
                if self.is_debug:
                    print(f"Comando enviado: {cmd_bcc}")

                if self.serial_connection.in_waiting:
                    self.serial_connection.reset_input_buffer()
                if self.serial_connection.out_waiting:
                    self.serial_connection.reset_output_buffer()

                self.serial_connection.write(cmd_bcc)
                time.sleep(self.time_delay)

                response = self._read_response()
                if self.is_debug:
                    print(f"Respuesta completa: {response}")

                fields = self._process_response(response, cmd)
                if not fields:
                    return {
                        "status": "error",
                        "error": "No se obtuvieron campos en la respuesta",
                    }

                if "ERROR" in fields:
                    return {"status": "error", "error": fields[1]}

                if cmd[2:3] in [b"\x48", b"\x49", b"\x4a"]:
                    return {"status": "ok", "fields": fields}

                if cmd[2:3] == b"\x80":
                    return {"status": "ok", "fields": fields}

                return {
                    "status": "ok",
                    "printer_status": self._printer_status(fields[0].encode("iso-8859-1")),
                    "fiscal_status": self._fiscal_status(fields[1].encode("iso-8859-1")),
                    "fields": fields,
                }

            except Exception as e:
                return {"status": "error", "error": str(e)}
        else:
            return {"status": "error", "error": "No hay conexión con la impresora"}

    def _next_sequence(self) -> bytes:
        """
        Obtiene el siguiente número de secuencia válido.
        Asegura que sea diferente al anterior y esté en el rango correcto.
        Returns:
            bytes: Número de secuencia en formato bytes
        """
        next_seq = self._last_sequence + 1
        if next_seq > self.SEQ_MAX or next_seq < self.SEQ_MIN:
            next_seq = self.SEQ_MIN

        self._last_sequence = next_seq
        return bytes([next_seq])

    def _build_command(self, cmd: bytes, *args: bytes) -> bytes:
        """
        Construye un comando para enviar a la impresora.
        Args:
            cmd: Comando base o comando completo
            *args: Argumentos adicionales para el comando
        Returns:
            bytes: Comando completo formateado
        """
        if cmd.startswith(self.STX) and cmd.endswith(self.ETX):
            return cmd  # Si el comando ya tiene STX y ETX, lo devolvemos tal cual

        if cmd.startswith(self.STX):  # Si el comando ya tiene STX pero no ETX, solo agregamos argumentos y ETX
            result = bytearray(cmd[:-1] if cmd.endswith(self.ETX) else cmd)
        else:
            result = bytearray(self.STX)
            result.extend(cmd)  # Si no tiene STX, construimos desde cero

        for arg in args:
            result.extend(self.SEP)  # Agregamos los argumentos separados por FS
            result.extend(arg)

        if not result.endswith(self.ETX):
            result.extend(self.ETX)  # Si no termina en ETX, lo agregamos

        return bytes(result)

    @staticmethod
    def _report_fields(fields: list) -> dict:
        """
        Parsea los campos específicos de los reportes X y Z.
        Args:
            fields: Lista de campos de la respuesta
        Returns:
            dict: Diccionario con los campos parseados
        """
        return {
            "numero_ultima_factura": fields[3] if len(fields) > 3 else "",
            "fecha": fields[11] if len(fields) > 11 else "",
            "hora": fields[22] if len(fields) > 22 else "",
            "numero_ultima_nota_credito": fields[23] if len(fields) > 23 else "",
        }

    def report_x(self) -> dict:
        """
        Genera un reporte X (reporte de auditoría sin cierre).
        Returns:
            dict: Respuesta de la impresora fiscal
        """
        cmd = self._build_command(self.CMD_REPORT_X)
        response = self.send_command(cmd)

        if response["status"] == "ok":
            response["report_info"] = self._report_fields(response["fields"])

        return response

    def report_z(self) -> dict:
        """
        Genera un reporte Z (reporte de cierre diario).
        Returns:
            dict: Respuesta de la impresora fiscal
        """
        cmd = self._build_command(self.CMD_REPORT_Z)
        response = self.send_command(cmd)

        if response["status"] == "ok":
            response["report_info"] = self._report_fields(response["fields"])

        return response

    def status_if(self, tipo: str = "N") -> dict:
        """
        Obtiene el estado de la impresora fiscal.
        Args:
            tipo: Tipo de estado a consultar ('N' = Normal, 'E' = Extendido)
        Returns:
            dict: Estado de la impresora fiscal
        """
        cmd = self.CMD_STATUS + tipo.encode("iso-8859-1") + self.ETX
        return self.send_command(cmd)

    def serial_info(self) -> dict:
        """
        Obtiene la información de serial y registro del equipo.
        Returns:
            dict: Diccionario con la información del equipo
        """
        cmd = self._build_command(self.CMD_SERIAL_INFO)
        response = self.send_command(cmd)

        if response["status"] == "ok" and response["fields"]:
            fields = response["fields"]
            # Los campos vienen en este orden:
            # 0080 (código respuesta), 8620 (status impresora), EOO9000001 (status fiscal),
            # J-29366870-0 (serial), 26.5 (rif), 1df0de (version),
            # 22003c000947313037363132 (memoria fiscal), B (numero registro)
            serial_info = {
                "codigo_respuesta": fields[0] if len(fields) > 0 else "",
                "status_impresora": fields[1] if len(fields) > 1 else "",
                "status_fiscal": fields[2] if len(fields) > 2 else "",
                "serial": fields[3] if len(fields) > 3 else "",
                "rif": fields[4] if len(fields) > 4 else "",
                "version": fields[5] if len(fields) > 5 else "",
                "memoria_fiscal": fields[6] if len(fields) > 6 else "",
                "numero_registro": fields[7] if len(fields) > 7 else "",
                "fields": fields,  # Todos los campos para referencia
            }
            return {"status": "ok", **serial_info}
        return response

    def dnf_open(self) -> dict:
        """
        Abre un documento NO fiscal.
        Returns:
            dict: Respuesta de la impresora fiscal
        """
        seq = self._next_sequence()
        cmd = self.STX + seq + self.CMD_OPEN_NONFISCAL + self.ETX
        return self.send_command(cmd)

    def dnf_text(self, text: str) -> dict:
        """
        Imprime una línea de texto en el documento NO fiscal.
        Args:
            text: Texto a imprimir (máximo 40 caracteres, sin acentos)
        Returns:
            dict: Respuesta de la impresora fiscal
        """
        text = text[:40]
        text_bytes = text.encode("ascii", "ignore")
        seq = self._next_sequence()
        cmd = self.STX + seq + self.CMD_PRINT_NONFISCAL + self.SEP + text_bytes + self.ETX
        return self.send_command(cmd)

    def dnf_close(self) -> dict:
        """
        Cierra el documento NO fiscal actual.
        Returns:
            dict: Respuesta de la impresora fiscal
        """
        seq = self._next_sequence()
        cmd = self.STX + seq + self.CMD_CLOSE_NONFISCAL + self.SEP + self.DEL + self.ETX
        return self.send_command(cmd)

    def fiscal_open(
        self,
        customer_name: str,
        customer_rif: str,
        doc_type: bytes,
        ref_number: str = None,
        ref_serial: str = None,
        ref_date: str = None,
        ref_time: str = None,
    ) -> dict:
        """
        Abre un documento fiscal.
        Args:
            customer_name: Nombre o razón social del cliente (máx. 38 caracteres)
            customer_rif: RIF del cliente (máx. 12 caracteres)
            doc_type: Tipo de documento (DOC_TYPE_INVOICE o DOC_TYPE_CREDIT_NOTE)
            ref_number: Número de factura en devolución (solo para notas de crédito)
            ref_serial: Serial de la máquina fiscal de la factura (solo para notas de crédito)
            ref_date: Fecha de la factura en devolución (formato: dd/mm/yy)
            ref_time: Hora de la factura en devolución (formato: HH:MM)
        Returns:
            dict: Respuesta de la impresora fiscal
        """
        customer_name = customer_name[:38]
        customer_rif = customer_rif[:12]
        seq = self._next_sequence()

        fields = [
            customer_name.encode("ascii", "ignore"),
            customer_rif.encode("ascii", "ignore"),
            ref_number.encode("ascii", "ignore") if ref_number else self.DEL,
            ref_serial.encode("ascii", "ignore") if ref_serial else self.DEL,
            ref_date.encode("ascii", "ignore") if ref_date else self.DEL,
            ref_time.encode("ascii", "ignore") if ref_time else self.DEL,
            doc_type,
            self.DEL,  # Campo para uso futuro
            self.DEL,  # Campo para uso futuro
        ]

        cmd = bytearray(self.STX + seq + self.CMD_OPEN_FISCAL)
        for field in fields:
            cmd.extend(self.SEP)
            cmd.extend(field if isinstance(field, bytes) else field)

        cmd.extend(self.ETX)
        return self.send_command(bytes(cmd))

    def fiscal_text(self, text: str) -> dict:
        """
        Agrega una línea de texto al documento fiscal.
        Args:
            text: Texto a agregar (máx. 40 caracteres)
        Returns:
            dict: Respuesta de la impresora fiscal
        """
        text = text[:40]
        seq = self._next_sequence()
        fields = [
            text.encode("ascii", "ignore"),
            b"\x53",  # Calificador de texto fiscal
        ]

        cmd = bytearray(self.STX + seq + self.CMD_ADD_FISCAL_TEXT)
        for field in fields:
            cmd.extend(self.SEP)
            cmd.extend(field)

        cmd.extend(self.ETX)
        return self.send_command(bytes(cmd))

    def fiscal_item(
        self,
        description: str,
        quantity: float,
        price: float,
        tax_rate: float,
        operation: bytes = OP_ADD,
    ) -> dict:
        """
        Agrega un ítem al documento fiscal.
        Args:
            description: Descripción del ítem (máx. 20 caracteres)
            quantity: Cantidad (formato: nnnn.nnn)
            price: Precio unitario sin impuesto (formato: nnnnnn.nn)
            tax_rate: Tasa de impuesto (0000=0%, 0800=8%, 1600=16%, 3100=31%)
            operation: Tipo de operación (OP_ADD=suma, OP_SUB=resta)
        Returns:
            dict: Respuesta de la impresora fiscal
        """
        description = description[:20]
        qty = str(int(quantity * 1000))  # 3 decimales sin punto
        prc = str(int(price * 100))  # 2 decimales sin punto
        tax = str(int(tax_rate * 100))  # 2 decimales sin punto
        tax = tax.zfill(4)  # Rellenamos con ceros a la izquierda

        seq = self._next_sequence()
        fields = [
            description.encode("ascii", "ignore"),
            qty.encode("ascii"),
            prc.encode("ascii"),
            tax.encode("ascii"),
            operation,
            self.DEL,  # Campo para uso futuro
            self.DEL,  # Campo para uso futuro
            self.DEL,  # Campo para uso futuro
        ]

        cmd = bytearray(self.STX + seq + self.CMD_ADD_FISCAL_ITEM)
        for field in fields:
            cmd.extend(self.SEP)
            cmd.extend(field)

        cmd.extend(self.ETX)
        return self.send_command(bytes(cmd))

    def get_subtotal(self) -> dict:
        """
        Obtiene el subtotal del documento fiscal actual.
        Returns:
            dict: Respuesta de la impresora fiscal
        """
        seq = self._next_sequence()
        cmd = self.STX + seq + self.CMD_GET_SUBTOTAL + self.SEP + self.CLOSE_PARTIAL + self.ETX
        return self.send_command(cmd)

    def fiscal_close(self, amount: float = 0, add_igtf: bool = False) -> dict:
        """
        Cierra el documento fiscal actual.
        Args:
            amount: Monto recibido (formato: nnnnnn.nn)
            add_igtf: Si True, agrega el IGTF al cierre
        Returns:
            dict: Respuesta de la impresora fiscal
        """
        amount_str = str(int(amount * 100))  # 2 decimales sin punto
        seq = self._next_sequence()
        close_type = self.CLOSE_TOTAL_IGTF if add_igtf else self.CLOSE_TOTAL

        fields = [close_type, amount_str.encode("ascii")]
        cmd = bytearray(self.STX + seq + self.CMD_CLOSE_FISCAL)
        for field in fields:
            cmd.extend(self.SEP)
            cmd.extend(field if isinstance(field, bytes) else field)

        cmd.extend(self.ETX)
        return self.send_command(bytes(cmd))
