#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright © 2024, Iron Graterol
Licensed under the GNU Affero General Public License, version 3 or later.
"""

from typing import Any, Dict, Optional, Union
import logging
import serial

# Configuración del logging
logger = logging.getLogger(__name__)


class FiscalPrinterPnp:
    """Clase para manejar la comunicación con impresoras fiscales PNP."""

    SEQ_MIN = 0x20  # Valor mínimo de secuencia
    SEQ_MAX = 0x7F  # Valor máximo de secuencia

    def __init__(self, port: str = "COM96", baudrate: int = 9600, timeout: int = 2) -> None:
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
        self._last_sequence = self.SEQ_MAX  # Iniciar al máximo para que el primer comando use SEQ_MIN

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
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=self.timeout,
                write_timeout=5,
                xonxoff=0,
                rtscts=0,
                dsrdtr=0,
            )

            logger.debug("Puerto %s abierto correctamente.", self.port)
            return True
        except Exception as e:
            logger.debug("Error al abrir el puerto: %s", e)
            return False

    def close_port(self) -> None:
        """Cierra el puerto serial si está abierto."""
        if self.serial_printer and self.serial_printer.is_open:
            self.serial_printer.close()
            logger.debug("Puerto %s cerrado.", self.port)

    def _next_sequence(self) -> bytes:
        """
        Obtiene el siguiente número de secuencia válido.
        Asegura que sea diferente al anterior y esté en el rango correcto.
        Returns:
            bytes: Número de secuencia como byte
        """
        next_seq = self._last_sequence + 1
        if next_seq > self.SEQ_MAX or next_seq < self.SEQ_MIN:
            next_seq = self.SEQ_MIN

        self._last_sequence = next_seq
        return bytes([next_seq])

    def _calculate_bcc(self, data: bytes) -> str:
        """
        Calcula el BCC (Block Check Character) para los datos dados.
        Args:
            data (bytes): Datos para calcular el BCC.
        Returns:
            str: BCC calculado como string hexadecimal de 4 caracteres.
        """
        bcc = 0
        for byte in data:
            bcc += byte
        return f"{bcc:04X}"

    def _build_cmd(self, command: str) -> bytes:
        """
        Construye la trama a enviar, con secuencia rotativa y BCC.
        Args:
            command (str): Comando a enviar.
        Returns:
            bytes: Trama construida como bytes.
        """
        seq = self._next_sequence()
        cmd_str = command.replace("|", chr(0x1C))
        cmd_bytes = bytes([0x02]) + seq + cmd_str.encode("latin-1") + bytes([0x03])
        bcc = self._calculate_bcc(cmd_bytes)
        cmd_with_bcc = cmd_bytes + bcc.encode("latin-1")
        return cmd_with_bcc

    def _parse_status(self, codigo: str) -> str:
        """
        Parsea el códigos de estado y lo mapea según la documentación.
        Args:
            codigo (str): Código de estado de la impresora (Campo 4 de la respuesta al comando 8|N)
        Returns:
            str: Descripción del estado de la impresora
        """
        estados = {
            "00": "Impresora lista para abrir una factura, abrir un documento no fiscal, hacer un reporte Z o un reporte de memoria fiscal.",  # pylint: disable=C0301
            "01": "Factura fiscal en curso. Esperando por un ítem, cerrar/cancelar la factura. Solo se admitirán comandos relacionados a la factura fiscal.",  # pylint: disable=C0301
            "02": "Documento no fiscal en curso. Esperando por línea de texto, cerrar el documento. Solo se admitirán comandos relacionados a documentos no fiscales.",  # pylint: disable=C0301
            "03": "SLIP activo. Solo se admitirán comandos relacionados a documentos no fiscales o comandos para el formato de cheques.",  # pylint: disable=C0301
            "04": "Más de un día desde el último reporte Z. Es necesario un reporte Z. Para poder realizar una venta se deberá efectuar previamente un reporte Z.",  # pylint: disable=C0301
            "05": "Primeras líneas descriptivas de una factura fiscal impresas.",
            "08": "Equipo bloqueado a la espera de impresión de cierre Z. Esto ocurre solo en caso de producirse un error durante la impresión de un cierre Z. Por ejemplo, si se acaba el papel cuando se está imprimiendo un cierre Z. Se debe hacer un RESET al equipo.",  # pylint: disable=C0301
            "10": "Error crítico. Error en BCC RAM. Es necesaria la intervención del servicio técnico.",
            "11": "Error crítico. Error en BCC ROM. Es necesaria la intervención del servicio técnico.",
            "12": "Error crítico. Error de formato de FECHA en RAM. Es necesaria la intervención del servicio técnico.",
            "13": "Error crítico. Error de formato de datos al realizar un Z. Es necesaria la intervención del servicio técnico.",  # pylint: disable=C0301
            "14": "Error crítico. Límite de memoria fiscal. Es necesaria la intervención del servicio técnico.",
        }
        return estados.get(codigo, f"Código desconocido: {codigo}")

    def send_cmd(self, command: str) -> list:
        """
        Envía un comando y gestiona la respuesta
        Args:
            command (str): Comando a enviar.
        Returns:
            list: Respuesta lista o None.
        """
        try:
            logger.debug("Enviando comando: %s", command)
            self.serial_printer.flushInput()
            self.serial_printer.flushOutput()

            self.serial_printer.reset_input_buffer()
            self.serial_printer.reset_output_buffer()

            cmd_bytes = self._build_cmd(command)  # Construir y enviar comando
            self.serial_printer.write(cmd_bytes)
            logger.debug("Enviado con BCC : %s", cmd_bytes.hex())

            rt = self.serial_printer.read_until(expected=b"\x03", size=500)
            logger.debug("Respuesta hexa  : %s", rt.hex())
            logger.debug("Respuesta byte  : %s", rt)

            clean_stx_etx = rt.replace(b"\x02", b"").replace(b"\x03", b"")
            rt_split = clean_stx_etx.split(b"\x1c")
            fields = [p.decode("latin-1") for p in rt_split[1:]]
            logger.debug("Respuesta fields  : %s", fields)
            fields = [field for field in fields if field]
            logger.debug("Respuesta Validada: %s", fields)

            return fields

        except Exception as e:
            logger.debug("Error enviando comando: %s", e)
            return []

    def status_if(self, tipo: str) -> Union[Dict[str, str], bytes, bool]:
        """
        Obtiene el estado de la impresora fiscal usando el comando 8|tipo.
        Args:
            tipo (str): Tipo de estado a consultar (N, V, etc.)
        Returns:
            Union[Dict[str, str], bytes, bool]: Diccionario con los campos de respuesta o la respuesta en bruto
        """
        command = f"8|{tipo}"
        response = self.send_cmd(command)
        logger.debug("Número de campos recibidos: %d", len(response))
        if response:
            try:
                if len(response) >= 3:
                    result = {}
                    for i, field in enumerate(response):
                        field_value = field.strip()
                        result[f"campo_{i:02d}"] = field_value

                    return result
            except Exception as e:
                logger.debug("Error formateando respuesta: %s", e)
        return response

    def get_status(self) -> Optional[Dict[str, Any]]:
        """
        Obtiene el estado de la impresora fiscal usando el comando 8|V
        Returns:
            Optional[Dict[str, Any]]: Diccionario con información del estado o None en caso de error.
        """
        try:
            response = self.status_if("V")
            if not response:
                logger.debug("Respuesta inválida o vacía")
                return None

            status = {}
            if "campo_01" in response:  # campo_01: status_impresora
                status["status_code"] = response["campo_00"]

            if "campo_02" in response:  # campo_02: status_fiscal
                status["error_code"] = response["campo_01"]

            if "campo_04" in response:  # campo_04: codigo_impresora
                codigo = response["campo_03"]
                status["status"] = codigo
                status["status_detallado"] = self._parse_status(codigo)

                # Verificar si hay error crítico (primer byte distinto de "0")
                if codigo and len(codigo) >= 1 and codigo[0] != "0":
                    status["error_critico"] = True
                    status["requiere_servicio"] = True
                else:
                    status["error_critico"] = False
                    status["requiere_servicio"] = False

            status["campos_referenciales"] = response
            return status
        except Exception as e:
            logger.debug("Error leyendo estado de la impresora: %s", e)
            return None

    def get_counters(self) -> Optional[Dict[str, Any]]:
        """
        Obtiene información fiscal y contadores usando el comando 8|N
        - Campo 1: Estado de impresora (0000)
        - Campo 2: Estado fiscal (0000)
        - Campo 3: Último valor de secuencia
        - Campo 4: Código del status actual de la impresora
        - Campo 5: Código último comando ejecutado
        - Campo 6: Fecha en la IF (AAMMDD)
        - Campo 7: Hora en la IF (HHMMSS)
        - Campo 8: # Acumulados fiscales del periodo fiscal
        - Campo 9: # facturas del periodo fiscal
        - Campo 10: # Acumulados DNF
        - Campo 11: # último reporte Z
        - Campo 12: # Desconocido
        Returns:
            Optional[Dict[str, Any]]: Diccionario con información o None en caso de error.
        """
        try:
            response = self.send_cmd("8|N")
            if not response:
                logger.debug("Respuesta inválida o vacía")
                return None

            if len(response) >= 3:
                counters = {}
                field_names = {
                    0: "status_code",
                    1: "error_code",
                    2: "ultima_secuencia",
                    3: "status",
                    4: "ultimo_comando",
                    5: "fecha",
                    6: "hora",
                    7: "acumulados_fiscales",
                    8: "facturas",
                    9: "acumulados_dnf",
                    10: "ultimo_z",
                    11: "desconocido",
                }

                logger.debug("Número de campos recibidos: %d", len(response))
                for i, field in enumerate(response):
                    if i < len(field_names):
                        field_value = field.strip()
                        counters[field_names[i]] = field_value

                if "fecha" in counters and len(counters["fecha"]) == 6:
                    fecha = counters["fecha"]
                    counters["fecha_formateada"] = f"20{fecha[0:2]}-{fecha[2:4]}-{fecha[4:6]}"

                if "hora" in counters and len(counters["hora"]) == 6:
                    hora = counters["hora"]
                    counters["hora_formateada"] = f"{hora[0:2]}:{hora[2:4]}:{hora[4:6]}"

                if "status" in counters:
                    codigo = counters["status"]
                    counters["status_detallado"] = self._parse_status(codigo)

                    if codigo and len(codigo) >= 1 and codigo[0] != "0":
                        counters["error_critico"] = True
                        counters["requiere_servicio"] = True
                    else:
                        counters["error_critico"] = False
                        counters["requiere_servicio"] = False

                return counters
            return None
        except Exception as e:
            logger.debug("Error leyendo contadores de la impresora: %s", e)
            return None

    def get_version(self) -> Optional[Dict[str, str]]:
        """
        Obtiene la información de la version de la impresora.
        Returns:
            Optional[Dict[str, str]]: Diccionario con información o None en caso de error.
        """
        try:
            response = self.send_cmd("\x80|")
            logger.debug("Respuesta: %s", response)
            if response:
                data = {}
                field_names = {
                    0: "status_code",
                    1: "error_code",
                    2: "serial",
                    3: "rif",
                    4: "version",
                    5: "modelo",
                    6: "numero_registro",
                }
                model_map = {"Z71": "PF-330", "1df0de": "PF-220"}
                for i, line in enumerate(response):
                    if line and i < len(field_names):
                        clean_line = line.strip()
                        if i == 5:
                            clean_line = model_map.get(clean_line, f"Desconocido ({clean_line})")
                        data[field_names[i]] = clean_line
                return data
            return None
        except Exception as e:
            logger.debug("Error leyendo version de la impresora: %s", e)
            return None
