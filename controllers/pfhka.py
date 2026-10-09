#!/usr/bin/env python
"""
Copyright © 2024, Iron Graterol
Licensed under the GNU Affero General Public License, version 3 or later.
"""

import logging
import time
from typing import Any

import serial

# Configuración del logging
logger = logging.getLogger(__name__)


class FiscalPrinterHka:
    """Clase para manejar la comunicación con impresoras fiscales TFHKA."""

    def __init__(self, port: str = "COM9", baudrate: int = 9600, timeout: int = 2) -> None:
        """
        Inicializa la clase FiscalPrinter.
        Args:
            port (str): Puerto COM a utilizar.
            baudrate (int): Velocidad de comunicación.
            timeout (int): Tiempo de espera para operaciones de lectura/escritura.
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_printer = None
        self.printer_model = None

    def open_port(self) -> bool:
        """
        Abre el puerto serial con la configuración establecida.
        Returns:
            bool: True si se abrió correctamente, False en caso contrario.
        """
        try:
            self.serial_printer = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_EVEN,
                stopbits=serial.STOPBITS_ONE,
                timeout=self.timeout,
                write_timeout=5,
                # Sin XON/XOFF: el protocolo es binario y usa RTS/CTS. Con xonxoff=True el sistema descartaba el
                # byte LRC cuando valía 0x11/0x13 (medido en HKA80: 11 de 500 lecturas S1 sin LRC; 0 sin xonxoff).
                xonxoff=False,
                rtscts=True,
                dsrdtr=True,
            )
            logging.debug("Puerto %s abierto correctamente.", self.port)
            return True
        except Exception as e:
            logging.debug("Error al abrir el puerto: %s", e)
            return False

    def close_port(self) -> None:
        """Cierra el puerto serial si está abierto."""
        if self.serial_printer and self.serial_printer.is_open:
            self.serial_printer.close()
            logging.debug("Puerto %s cerrado.", self.port)

    def _calculate_lrc(self, data: str) -> bytes:
        """
        Calcula el LRC (Longitudinal Redundancy Check) para la cadena de datos.
        Args:
            data (str): Datos a procesar.
        Returns:
            bytes: LRC calculado.
        """
        data_con_etx = data + chr(0x03)
        lrc = 0
        for char in data_con_etx:
            lrc ^= ord(char)
        return bytes([lrc])

    def _build_cmd(self, command: str) -> None:
        """
        Construye y envía la trama, incluyendo STX, comando, ETX, LRC y libera RTS.
        Args:
            command (str): Comando a enviar.
        """
        cmd = bytes([0x02]) + command.encode("latin-1") + bytes([0x03])
        cmd += self._calculate_lrc(command)
        logging.debug("[TX] %s", cmd.hex().upper())
        self.serial_printer.write(cmd)
        self.serial_printer.setRTS(False)

    def _handle_cts_rts(self) -> bool:
        """
        Maneja los buffers de entrada/salida y el control de flujo CTS/RTS.
        Returns:
            bool: True si fue exitosa, False en caso contrario.
        """
        try:
            self.serial_printer.flushInput()
            self.serial_printer.flushOutput()
            self.serial_printer.reset_input_buffer()
            self.serial_printer.reset_output_buffer()

            self.serial_printer.setRTS(True)
            return True
        except Exception as e:
            logging.error("Error en control CTS/RTS: %s", e)
            return False

    def _read_status(self, command: str) -> str | bool:
        """
        Maneja comandos extendidos para leer el estado de la impresora.
        Args:
            command (str): Comando extendido a enviar.
        Returns:
            Union[str, bool]: Respuesta decodificada o False en caso de error.
        """
        try:
            if not self._handle_cts_rts():
                return False

            self._build_cmd(command)
            time.sleep(0.5)
            available_bytes = self.serial_printer.inWaiting()
            if available_bytes > 0:
                response = self.serial_printer.read(available_bytes)
                if len(response) >= 4 and response[0] == 0x02 and 0x03 in response:
                    etx_pos = response.find(0x03)
                    logging.debug("Reponse _read_status: %s", etx_pos)
                    try:
                        return response[1:etx_pos].decode("latin-1")
                    except UnicodeDecodeError:
                        return response.hex()
            return False
        except Exception as e:
            logging.debug("Error leyendo estado: %s", e)
            return False

    def _clean_response(self, response: str, command: str) -> list[str]:
        """
        Limpia y prepara la respuesta de comandos S1-S5,SV.
        Args:
            response: Respuesta raw de la impresora
            command: Comando que se ejecutó (S1,S2,etc)
        Returns:
            Lista de líneas limpias
        """
        lines = []
        # No hacer strip() porque elimina los ceros iniciales de la línea de flags
        for i, line in enumerate(response.split("\n")):
            # Remover solo el comando del inicio (S1, S2, etc) pero mantener ceros
            clean = line.strip()
            if i == 0 and clean.startswith(command):
                # Remover "S3" o "S3" del inicio, pero mantener todo lo demás
                clean = clean[len(command) :] if len(clean) > len(command) else ""
            if clean:
                lines.append(clean)
        return lines

    def _parse_status(self, sts1: int, sts2: int) -> dict[str, Any]:
        """
        Parsea los códigos de estado y error y los mapea a descripciones.
        Args:
            sts1 (int): Código de estado.
            sts2 (int): Código de error.
        Returns:
            Dict[str, Any]: Diccionario con la información del estado.
        """
        logging.debug("sts1: %s sts2: %s", str(sts1), str(sts2))
        status_codes = {
            0x00: "Estado desconocido",
            0x40: "En modo prueba y en espera",
            0x41: "En modo prueba y en emisión de documentos fiscales",
            0x42: "En modo prueba y en emisión de documentos no fiscales",
            0x60: "En modo fiscal y en espera",
            0x61: "En modo fiscal y en emisión de documentos fiscales",
            0x62: "En modo fiscal y en emisión de documentos no fiscales",
            0x68: "En modo fiscal, carga completa de la memoria fiscal y en espera",
            0x69: "En modo fiscal, carga completa de la memoria fiscal y emisión de documentos fiscales",
            0x6A: "En modo fiscal, carga completa de la memoria fiscal y emisión de documentos no fiscales",
            0x70: "En modo fiscal, cercana carga completa de la memoria fiscal y en espera",
            0x71: "En modo fiscal, cercana carga completa de la memoria fiscal y en emisión de documentos fiscales",
            0x72: "En modo fiscal, cercana carga completa de la memoria fiscal y en emisión de documentos no fiscales",
        }
        error_codes = {
            0x00: "Error desconocido",
            0x40: "Sin errores",
            0x41: "Fin en la entrega de papel",
            0x42: "Error mecánico en la entrega de papel",
            0x43: "Fin en la entrega de papel y error mecánico",
            0x48: "Error de gaveta",
            0x50: "Comando/Valor inválido",
            0x54: "Tasa inválida",
            0x58: "No hay asignadas directivas",
            0x5C: "Comando inválido",
            0x60: "Error fiscal",
            0x64: "Error en memoria fiscal",
            0x6C: "Memoria fiscal llena",
            0x04: "Buffer completo",
            0x80: "Error de comunicación",
            0x89: "NAK recibido",
            0x90: "Error de paridad",
            0xA0: "Error de sobrecarga",
            0xB0: "Error de formato",
            0xC0: "Dispositivo ocupado",
            0xD0: "Timeout",
            0xE0: "Error de frame",
            0xF0: "Error desconocido",
        }
        error_desc = error_codes.get(sts2, f"Error desconocido (0x{sts2:02X})")
        if sts2 == 114:
            error_desc = "Impresora no responde o ocupada"
        elif sts2 == 128:
            error_desc = "CTS en falso"
        elif sts2 == 137:
            error_desc = "No hay respuesta"
        elif sts2 == 144:
            error_desc = "Error LRC"
        return {
            "status_code": sts1,
            "error_code": sts2,
            "status": status_codes.get(sts1, f"Estado desconocido (0x{sts1:02X})"),
            "error": error_desc,
        }

    def send_cmd(self, command: str, retries: int = 3) -> bool | str:
        """
        Envía un comando y gestiona la respuesta.
        Args:
            command (str): Comando a enviar.
            retries (int): Número de reintentos (por defecto 3).
        Returns:
            Union[bool, str]: True o respuesta si fue exitoso, False en caso contrario.
        """
        # Comandos especiales que requieren manejo extendido
        command_ext = ["SV", "S1", "S2", "S3", "S5"]
        if command in command_ext:
            return self._read_status(command)

        max_attempts = retries + 1
        for attempt in range(1, max_attempts + 1):
            logging.debug("Intento %s/%s para comando %s", attempt, max_attempts, command)
            if not self._handle_cts_rts():
                logging.debug("Error: No se pudo establecer control de flujo CTS/RTS")
                time.sleep(0.5)
                continue

            self._build_cmd(command)
            ack = None
            max_read_attempts = 5
            for _ in range(max_read_attempts):
                ack = self.serial_printer.read(1)
                logging.debug("ACK: %s", ack)
                if ack:
                    break
                time.sleep(0.2)

            if not ack:
                logging.debug("Timeout esperando ACK/NAK")
                time.sleep(0.3)
                continue

            if ack == b"\x06":
                logging.debug("ACK recibido - Comando aceptado")
                return True

            if ack == b"\x15":
                logging.debug("NAK recibido - Error en el comando")
                time.sleep(0.3)
                continue

            logging.debug("Respuesta inválida: %s", ack.hex() if ack else "Timeout")
            time.sleep(0.3)
            continue
        return False

    def get_status(self) -> dict[str, Any]:
        """
        Obtiene el estado actual de la impresora usando el comando ENQ.
        Returns:
            Dict[str, Any]: Diccionario con estado, error, código de estado y código de error.
        """
        try:
            if not self._handle_cts_rts():
                logging.debug("Error: No se pudo establecer control de flujo CTS/RTS")
                return {"status_code": 0, "error_code": 128, "status": "Error", "error": "CTS en falso"}

            self.serial_printer.write(b"\x05")
            time.sleep(0.5)
            status_data = self.serial_printer.read(5)
            self.serial_printer.setRTS(False)

            if len(status_data) == 5:
                sts1 = status_data[1]  # Valor decimal del estado de la impresora.
                sts2 = status_data[2]  # Valor decimal del error de la impresora.
                lrc_calculated = sts1 ^ sts2 ^ 0x03
                if lrc_calculated == status_data[4]:
                    return self._parse_status(sts1, sts2)

                logging.debug("Error LRC: Calculado=%s, Recibido=%s", lrc_calculated, status_data[4])
                return {"status_code": 0, "error_code": 144, "status": "Error", "error": "Error LRC"}
            logging.debug("Respuesta incompleta: %s", status_data.hex() if status_data else "Vacía")
            return {"status_code": 0, "error_code": 114, "status": "Desconocido", "error": "Respuesta inválida"}
        except Exception as e:
            logging.debug("Error ENQ: %s", e)
            return {"status_code": 0, "error_code": 137, "status": "Error", "error": str(e)}

    def get_s1(self) -> dict[str, str] | None:
        """
        Obtiene información fiscal y contadores usando el comando S1.
        Returns:
            Optional[Dict[str, str]]: Diccionario con información fiscal o None en caso de error.
        """
        try:
            response = self.send_cmd("S1")
            logging.debug("S1: %s", response)
            if response:
                s1 = {}
                field_names = {
                    0: "status_cajero",
                    1: "subtotal_ventas",
                    2: "ultima_factura",
                    3: "facturas_dia",
                    4: "ultima_nota_debito",
                    5: "notas_debito_dia",
                    6: "ultima_nota_credito",
                    7: "notas_credito_dia",
                    8: "ultimo_doc_no_fiscal",
                    9: "docs_no_fiscales_dia",
                    10: "contador_reportes_memoria",
                    11: "contador_cierres_z",
                    12: "rif",
                    13: "registro_maquina",
                    14: "hora_impresora",
                    15: "fecha_impresora",
                }
                lines = self._clean_response(response, "S1")
                for i, line in enumerate(lines):
                    if i < len(field_names):
                        s1[field_names[i]] = line
                return s1
            return None
        except Exception as e:
            logging.error("Error leyendo estado S1 de la impresora: %s", e)
            return None

    def get_s2(self) -> dict[str, str] | None:
        """
        Obtiene el estado del documento fiscal en curso usando el comando S2.
        Returns:
            Optional[Dict[str, str]]: Diccionario con información fiscal o None en caso de error.
        """
        try:
            response = self.send_cmd("S2")
            logging.debug("S2: %s", response)
            if response:
                s2 = {}
                field_names = {
                    0: "subtotal_base",
                    1: "subtotal_impuesto",
                    2: "uso_futuro",
                    3: "cantidad_articulos",
                    4: "monto_pagar",
                    5: "cantidad_pagos",
                    6: "tipo",
                }
                doc_type = {
                    "0": "Sin transacción",
                    "1": "En Factura",
                    "2": "En Nota de Crédito",
                    "3": "En Nota de Débito",
                }
                lines = self._clean_response(response, "S2")
                for i, line in enumerate(lines):
                    if i < len(field_names):
                        s2[field_names[i]] = line
                if "tipo" in s2:
                    type_doc = s2["tipo"]
                    if type_doc in doc_type:
                        s2["tipo_documento"] = doc_type[type_doc]
                return s2
            return None
        except Exception as e:
            logging.error("Error leyendo estado S2 del documento: %s", e)
            return None

    def get_s3(self, flags_to_read: list[int] | None = None) -> dict[str, str] | None:
        """
        Comando S3, lee los impuestos y flags según la Tabla 72 del manual.
        La respuesta puede tener:
        - 4 líneas: 3 taxes + flags (Flag 63 = 00)
        - 5 líneas: 3 taxes + IGTF + flags (Flag 63 = 01,02,03)
        Args:
            flags_to_read (Optional[List[int]]): Lista de flags a leer (0-63).
        Returns:
            Optional[Dict[str, str]]: Diccionario con claves tipo 'flag_X' e impuestos.
        """
        if flags_to_read is None:
            flags_to_read = [21, 30, 43, 50, 63]
        try:
            response = self.send_cmd("S3")
            logging.debug("S3 raw response: %s", response)
            if response:
                s3 = {}
                tax_name = {0: "General", 1: "Reducido", 2: "Adicional", 3: "IGTF"}
                code_type = {"0": "[Percibido]", "1": "[Excluido]", "2": "[Incluido]"}
                lines = self._clean_response(response, "S3")
                logging.debug("S3 lines: %s (count: %d)", lines, len(lines))

                # Las primeras líneas son impuestos (3 o 4 dependiendo de Flag 63)
                # La última línea es la cadena de flags (128 caracteres)
                num_tax_lines = len(lines) - 1  # Asumir última línea es flags
                tax_lines_to_process = min(num_tax_lines, 4)  # Max 4 taxes (incluyendo IGTF)

                for i in range(tax_lines_to_process):
                    if i < len(lines):
                        line = lines[i]
                        type_code = line[0] if line else "0"
                        tipo = code_type.get(type_code, "Desconocido")
                        valor_raw = line[1:] if len(line) > 1 else "0000"
                        valor = f"{valor_raw[:2]}.{valor_raw[2:4]}"
                        nombre = f"{tax_name[i]} {tipo}"
                        s3[nombre] = valor

                # Los flags están en la última línea (siempre 128 caracteres)
                if len(lines) > 1:
                    flags = lines[-1]  # Última línea = flags
                    logging.debug("S3 flags string length: %d (expected 128 for flags 0-63)", len(flags))
                    logging.debug("S3 flags string (first 50 chars): %s", flags[:50])

                    if len(flags) >= 128:
                        for flag in flags_to_read:
                            if 0 <= flag <= 63:
                                start = flag * 2
                                end = start + 2
                                s3[f"flag_{flag}"] = flags[start:end]
                        # Logging de los flags específicos que nos interesan
                        logging.debug(
                            "Parsed flags: flag_21=%s, flag_30=%s, flag_43=%s, flag_50=%s, flag_63=%s",
                            s3.get("flag_21", "N/A"),
                            s3.get("flag_30", "N/A"),
                            s3.get("flag_43", "N/A"),
                            s3.get("flag_50", "N/A"),
                            s3.get("flag_63", "N/A"),
                        )
                    else:
                        logging.warning("S3 flags string incompleto: %d caracteres (esperado 128)", len(flags))

                return s3
            return None
        except Exception as e:
            logging.error("Error leyendo estado S3 de la impresora: %s", str(e))
            return None

    def get_s5(self) -> dict[str, str] | None:
        """
        Obtiene el estado de la memoria fiscal usando el comando S5.
        Returns:
            Optional[Dict[str, str]]: Diccionario con información fiscal o None en caso de error.
        """
        try:
            response = self.send_cmd("S5")
            logging.debug("S5: %s", response)
            if response:
                s5 = {}
                field_names = {
                    0: "rif",
                    1: "serial",
                    2: "numero_memoria_auditoria",
                    3: "capacidad_mb_memoria",
                    4: "disponible_mb_memoria",
                    5: "documentos_registrados",
                }
                lines = self._clean_response(response, "S5")
                for i, line in enumerate(lines):
                    if i < len(field_names):
                        s5[field_names[i]] = line
                return s5
            return None
        except Exception as e:
            logging.error("Error leyendo estado S5 de la impresora: %s", e)
            return None

    def get_sv(self) -> dict[str, str] | None:
        """
        Lee el modelo de la impresora usando el comando SV.
        Returns:
            Optional[Dict[str, Any]]: Diccionario con el modelo detectado y el país, o None.
        """
        try:
            response = self.send_cmd("SV")
            if response:
                lines = self._clean_response(response, "SV")
                if len(lines) >= 2:
                    model_code = lines[0]
                    country_code = lines[1]
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
                    }
                    model = model_map.get(model_code, f"Desconocido ({model_code})")
                    self.printer_model = model
                    return {"modelo": model, "pais": country_code}
            return None
        except Exception as e:
            logging.error("Error leyendo estado S5 de la impresora: %s", e)
            return None

    # Comandos de extracción de información permitidos en upload_report (solo lectura; nunca cierres Z)
    _UPLOAD_ALLOWED = frozenset({"U0X", "U0X4", "U0X5", "U0X6", "U0X7"})

    def get_s4(self) -> dict[str, str] | None:
        """
        Obtiene los 24 acumuladores de formas de pago usando el comando S4 (solo lectura).
        S4 no pasa por send_cmd: se lee directamente con _read_status, igual que S1/S3/S5.
        Returns:
            Optional[Dict[str, str]]: Acumuladores por código "01".."24" (13 dígitos, 2 decimales
            implícitos) o None en caso de error.
        """
        try:
            response = self._read_status("S4")
            logger.debug("S4: %s", response)
            if response:
                lines = self._clean_response(response, "S4")
                return {f"{i:02d}": line for i, line in enumerate(lines[:24], start=1)}
            return None
        except Exception as e:  # noqa: BLE001 - lectura informativa: cualquier fallo devuelve None
            logger.error("Error leyendo estado S4 de la impresora: %s", e)
            return None

    def _read_info_frame(self, timeout: float = 5.0) -> tuple[str, str] | None:
        """
        Lee un bloque de una extracción de información: EOT, o una trama STX...ETX|ETB LRC verificada.
        Responde NAK si el LRC no coincide.
        Args:
            timeout (float): Segundos máximos de espera del bloque.
        Returns:
            Optional[Tuple[str, str]]: ("EOT", "") al terminar, ("ETX"|"ETB", texto) con la carga útil
            (latin-1, sin STX/terminador/LRC), o None por timeout, trama inválida o LRC incorrecto.
        """
        buffer = bytearray()
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            waiting = self.serial_printer.in_waiting
            chunk = self.serial_printer.read(waiting if waiting > 0 else 1)
            if chunk:
                buffer.extend(chunk)
            if buffer[:1] == b"\x04":  # EOT: fin de la extracción
                return "EOT", ""
            if buffer[:1] != b"\x02":
                if buffer:
                    logger.debug("Byte inesperado al leer la extracción: %s", bytes(buffer).hex())
                    return None
                continue
            end = next((i for i in range(1, len(buffer)) if buffer[i] in (0x03, 0x17)), -1)
            if end != -1 and len(buffer) > end + 1:
                body = bytes(buffer[1 : end + 1])  # Carga útil + terminador (el LRC los incluye)
                lrc = 0
                for byte in body:
                    lrc ^= byte
                if lrc != buffer[end + 1]:
                    logger.debug("LRC inválido en la extracción: calculado=%02X recibido=%02X", lrc, buffer[end + 1])
                    self.serial_printer.write(b"\x15")
                    return None
                return ("ETX" if buffer[end] == 0x03 else "ETB"), body[:-1].decode("latin-1")
        logger.debug("Timeout leyendo bloque de la extracción")
        return None

    def upload_report(self, command: str) -> str | None:
        """
        Extrae información de la máquina con un comando U0X* (solo lectura, protocolo ENQ/ACK).
        Flujo: envía la trama, la impresora responde ENQ (0x05), el PC responde ACK, la impresora envía
        la trama de datos, el PC verifica el LRC y responde ACK. Si el terminador es ETB hay más bloques:
        se confirman con ACK hasta recibir EOT o un ETX final. Nunca envía cierres Z.
        Args:
            command (str): Uno de U0X, U0X4, U0X5, U0X6, U0X7.
        Returns:
            Optional[str]: Texto concatenado de la carga útil (latin-1) o None si hubo timeout, NAK o LRC
            incorrecto.
        Raises:
            ValueError: Si el comando no está en la lista de extracciones permitidas.
        """
        if command not in self._UPLOAD_ALLOWED:
            raise ValueError(f"Comando de extracción no permitido: {command}")
        try:
            if not self._handle_cts_rts():
                return None

            self._build_cmd(command)
            first = self.serial_printer.read(1)  # La impresora pregunta ENQ "¿listo?"; sin ACK a tiempo envía NAK
            if first not in (b"\x05", b"\x06"):
                logger.debug("Respuesta inesperada a %s: %s", command, first.hex() if first else "timeout")
                return None
            self.serial_printer.write(b"\x06")

            parts: list[str] = []
            for _ in range(200):  # Límite de seguridad de bloques
                frame = self._read_info_frame()
                if frame is None:
                    return None
                kind, text = frame
                if kind == "EOT":
                    break
                parts.append(text)
                self.serial_printer.write(b"\x06")
                if kind == "ETX":
                    break
            else:
                return None
            return "".join(parts) if parts else None
        except Exception as e:  # noqa: BLE001 - lectura informativa: cualquier fallo devuelve None
            logger.error("Error extrayendo información %s: %s", command, e)
            return None
        finally:
            try:
                self.serial_printer.setRTS(False)
            except Exception as e:  # noqa: BLE001 - fallo al liberar RTS no debe propagarse
                logger.debug("No se pudo liberar RTS: %s", e)
