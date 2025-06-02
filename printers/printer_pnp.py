#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright © 2024, Iron Graterol
Licensed under the GNU Affero General Public License, version 3 or later.

Clase para el manejo de la impresora fiscal PNP
"""

import ctypes
import datetime
import time
import json
import logging
import os
from decimal import Decimal, ROUND_HALF_UP, getcontext
from typing import Any, Dict, Union

from printers.printer_base import BasePrinter
from printers.printer_commands import PNPcmd
from utils.tools import get_base_path, normalize_text, normalize_date, normalize_number, format_date, format_time

# Configuración del logging
logger = logging.getLogger(__name__)


class PnpPrinter(BasePrinter):
    """Clase para manejar la impresión en impresoras fiscales PNP"""

    # Constantes de error
    ERROR_CONNECTION = "Error: {}"
    ERROR_STATUS = "Código Impresora: {} || Código Fiscal: {}"

    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa la impresora fiscal y establece la conexión
        Args:
            config (dict): Configuración de la impresora
        """
        super().__init__(config)
        self.template_config = self._load_config("template_fiscal_printer.json", "templates")
        self.baudrate = config.get("fiscal_baudrate", 9600)
        self.enabled = config.get("fiscal_enabled", False)
        self.printer = config.get("fiscal_name", "pnp")
        self.port = config.get("fiscal_port")
        self.timeout = config.get("fiscal_timeout", 3)
        self.dll_path = os.path.join(get_base_path(), "library", "pnpdll.dll")
        self._printer = None
        self._model = self.template_config.get("fiscal", {}).get("model", "PF-220")  # Modelo de la impresora
        self._serial = None  # Serial de la impresora
        self._last_document = "0000000000"
        self._error = None

        self._initialize_printer()
        if not self.connect():
            raise ConnectionError(self.ERROR_CONNECTION.format(self._error))

    def _load_config(self, filename: str, directory: str) -> Dict[str, Any]:
        """
        Carga un archivo de configuración JSON desde el directorio especificado.
        Args:
            filename (str): Nombre del archivo de configuración
            directory (str): Directorio donde se encuentra el archivo
        Returns:
            Dict[str, Any]: Configuración cargada del archivo JSON
        """
        try:
            config_path = os.path.join(get_base_path(), directory, filename)
            if not os.path.exists(config_path):
                logger.error("Archivo de configuración no encontrado: %s", config_path)
                return {}

            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error("Error al cargar configuración %s: %s", filename, str(e))
            return {}

    def _initialize_printer(self) -> None:
        """Inicializa la conexión con el DLL y crea la instancia de la impresora"""
        try:
            self._printer = ctypes.CDLL(self.dll_path)  # Cargar la DLL
            function_config = self._load_config("pnp_functions.json", "config")
            if not function_config:
                raise RuntimeError("No se pudo cargar la configuración de funciones PNP")

            type_mapping = {
                "PRINTER_CHAR_P": ctypes.c_char_p,
                "PRINTER_NO_ARGS": [],
                "PRINTER_SINGLE_ARG": [ctypes.c_char_p],
                "PRINTER_DOUBLE_ARG": [ctypes.c_char_p, ctypes.c_char_p],
            }  # Mapeo de nombres de tipos a constantes reales

            for group in function_config.values():  # Configurar todas las funciones desde el JSON
                for func_name, func_config in group.items():
                    if not hasattr(self._printer, func_name):
                        logger.warning("Función %s no encontrada en el DLL", func_name)
                        continue

                    func = getattr(self._printer, func_name)
                    restype = func_config.get("restype")  # Establecer tipo de retorno
                    if restype in type_mapping:
                        func.restype = type_mapping[restype]

                    argtypes = func_config.get("argtypes")  # Establecer tipos de argumentos
                    if isinstance(argtypes, list):  # Si es una lista, mapear cada tipo
                        func.argtypes = [type_mapping["PRINTER_CHAR_P"] for _ in argtypes]
                    elif argtypes in type_mapping:  # Si es un string, usar el mapeo directamente
                        func.argtypes = type_mapping[argtypes]
                    elif argtypes == "PRINTER_NO_ARGS":  # Si no tiene argumentos, no establecer argtypes
                        func.argtypes = None

            logger.info("Inicialización de funciones PNP completada")
        except Exception as e:
            logger.error("Error al inicializar la impresora PNP: %s", str(e))
            raise RuntimeError(f"Error al inicializar la impresora PNP: {str(e)}") from e

    def connect(self) -> bool:
        """
        Establece la conexión con la impresora
        Returns:
            bool: True si la conexión fue exitosa
        """
        try:
            port_number = self.port.replace("COM", "") if self.port.startswith("COM") else self.port
            open_port = self._printer.PFabrepuerto(str(port_number).encode())

            if open_port.decode("utf-8") == "OK":
                logger.debug("Conexion con el puerto OK")

                # Tipo o Modelo de Impresora
                if self._model == "PF-300":
                    if self._printer.PFTipoImp(b"300").decode("utf-8") != "OK":
                        raise RuntimeError("Error al establecer tipo de impresora Matriz")
                else:
                    if self._printer.PFTipoImp(b"220").decode("utf-8") != "OK":
                        raise RuntimeError("Error al establecer tipo de impresora Ticket")

                # Serial de la impresora
                if self._printer.PFSerial().decode("utf-8") != "OK":
                    raise RuntimeError("Error al obtener serial de la impresora")

                printer_data = self._printer.PFultimo().decode("utf-8").split(",")
                self._serial = printer_data[2]

                logger.info("Conexión establecida con la impresora Modelo: %s, Serial: %s", self._model, self._serial)
                return True

            self._error = f"Conexion al puerto: {self.port}"
            logger.error("Error: %s", self._error)
            return False
        except Exception as e:
            logger.error("Error al conectar: %s", str(e))
            return False

    def format_number(self, value: Union[float, int, str], field_type: str) -> str:
        """
        Formatea un número como string según el tipo de campo para la impresora PNP.
        Los números se formatean con punto decimal y el número de decimales depende del tipo.
        Args:
            value: Valor a formatear (puede ser float, int o str)
            field_type: Tipo de campo ('quantity', 'price', 'payment', 'discount')
        Returns:
            str: Valor formateado como string con punto decimal
        """
        try:
            getcontext().rounding = ROUND_HALF_UP  # Configurar contexto para redondeo bancario (half-up)
            decimal_value = Decimal(str(value))

            if field_type == "quantity":  # Configurar decimales según el tipo de campo
                decimals = 3
            else:
                decimals = 2

            format_str = f"{{:.{decimals}f}}"
            formatted = format_str.format(float(decimal_value))
            formatted = formatted.replace(",", ".")
            return formatted

        except Exception as e:
            logger.error("Error al formatear número (%s): %s", field_type, str(e))
            raise

    def format_text(self, text: str, field_type: str) -> str:
        """
        Formatea texto según los límites del modelo de impresora PNP.
        Normaliza el texto y lo trunca según el tipo de campo y modelo.
        Args:
            text: Texto a formatear
            field_type: Tipo de campo ('product', 'comment', 'line', 'header', 'footer', 'partner', 'vat')
        Returns:
            str: Texto formateado según las especificaciones del modelo
        """
        try:
            max_char_config = self._load_config("pnp_max_char.json", "config")
            if not max_char_config:
                logger.warning("No se pudo cargar la configuración de caracteres máximos")
                max_chars = 40 if self._model == "PF-300" else 20 if field_type == "product" else 40
            else:
                model_config = max_char_config.get(self._model, max_char_config["PF-220"])  # PF-220 como fallback
                max_chars = model_config.get(field_type, 40)  # 40 como valor por defecto

            normalized = normalize_text(text)
            return normalized[:max_chars]

        except Exception as e:
            logger.error("Error al formatear texto (%s): %s", field_type, str(e))
            # Valores seguros por defecto en caso de error
            normalized = normalize_text(text)
            return normalized[:40]

    def cancel_doc(self, operation_type: str) -> str:
        """Metodo para cancelar, anular o cerrar documento"""
        msg = ""
        result = self._printer.PFCancelaDoc(b"D", b"0").decode("utf-8")
        if result == "OK":
            msg = "Documento Cancelado"
        if result == "TO":
            msg = "Se excedió el tiempo de respuesta esperado del equipo"
        if result == "NP":
            msg = "Puerto NO Abierto"
        if result == "ER":
            if operation_type == "note":
                self._printer.PFCierraNF()
                msg = "Impresión Interrumpida"
            else:
                self._printer.PFComando(b"C")
                result = self._printer.PFultimo().decode("utf-8").split(",")
                if int(result[15]) > 0:
                    msg = "Impresora con documento fiscal abierto. Cancelar la operación reiniciando la impresora"
                else:
                    self._printer.PFComando(b"E|T")
                    msg = "Impresora con documento fiscal en cero. Se procede a cancelar la operación"
        return msg

    def disconnect(self) -> None:
        """Desconecta la impresora fiscal y libera el DLL"""
        try:
            if self._printer:
                self._printer.PFcierrapuerto()
                # Get DLL handle using safer method
                handle = ctypes.c_void_p.from_address(id(self._printer)).value
                self._printer = None

                if handle:  # Free DLL from memory
                    ctypes.windll.kernel32.FreeLibrary(handle)

            logger.info("Desconexión y liberación de DLL exitosa")
        except Exception as e:
            logger.error("Error al desconectar: %s", str(e))

    def send_command(self, command: str, wait_time: float = 0.0) -> bool:
        """
        Envía un comando a la impresora
        Args:
            command (str): Comando a enviar
            wait_time (float): Tiempo de espera después del comando
        Returns:
            bool: True si el comando se ejecutó correctamente
        """
        try:
            result = self._printer.PFComando(command.encode())
            # print(f"send_command: {command} | {result}")
            if result.decode("utf-8") == "OK":
                logger.info(command)
                if wait_time > 0:
                    time.sleep(wait_time)
                value = True
            else:
                logger.error("Error al enviar comando: %s", command)
                # status = self.get_printer_status()
                # logger.error(
                #     "Estado: %s %s ",
                #     status["status_description"],
                #     status["error_description"],
                # )
                # print("en metodo send_command")
                # print(status["error_code"], status["status_code"])
                # print(status["error_description"], status["status_description"])
                # self._printer.PFCancelaDoc(PNPcommand.CANCEL)
                value = False
            return value
        except Exception as e:
            logger.error("Error al enviar comando: %s", str(e))
            return False

    def check_status(self) -> bool:
        """
        Verifica si la impresora está lista para operar
        Returns:
            bool: True si la impresora está lista, False en caso contrario
        """
        try:
            printer_data = self.get_printer_data("V")
            if not printer_data["status"] or not printer_data["data"]:
                logger.error("Error al obtener estado de la impresora")
                return False

            printer_state_code = printer_data["data"]["printer_state"]["code"]
            return printer_state_code == "00"

        except Exception as e:
            logger.error("Error al verificar estado de la impresora: %s", str(e))
            return False

    def get_printer_status(self) -> Dict[str, Any]:
        """
        Obtiene el estado detallado de la impresora
        Returns:
            Dict[str, Any]: Diccionario con la información del estado
        """
        try:
            check_status = self._printer.PFestatus(b"V").decode("utf-8")
            if check_status != "OK":
                logger.error("Error al obtener estado de la impresora")
                return {
                    "error_code": "0000",
                    "status_code": "0000",
                    "error_description": "Error al obtener estado",
                    "status_description": "Error al obtener estado",
                }

            logger.debug("Estado de la impresora: %s", self._printer.PFultimo().decode("utf-8"))
            status = self._printer.PFultimo().decode("utf-8").split(",")
            error_code = status[0]  # Estado de la impresora
            status_code = status[1]  # Estado fiscal
            return PNPcmd.parse_status(error_code, status_code)

        except Exception as e:
            logger.error("Error al obtener estado de impresora: %s", str(e))
            return {
                "error_code": "0000",
                "status_code": "0000",
                "error_description": f"Error inesperado: {str(e)}",
                "status_description": f"Error inesperado: {str(e)}",
            }

    def get_printer_data(self, model: str) -> Dict[str, Any]:
        """
        Obtiene información específica de la impresora según el modelo solicitado
        Args:
            model (str): Tipo de información a solicitar
                'N' = datos de los contadores
                'T' = Numero de última nota de crédito generada
                'U' = Valor IGTF fac, y nota de credito/devolucion
                'V' = Envia versión del FW del equipo
        Returns:
            Dict[str, Any]: Diccionario con la información solicitada según el modelo
        """
        try:
            printer_states = PNPcmd.PRINTER_STATES
            cmd = f"8|{model}".encode()
            if self._printer.PFComando(cmd).decode("utf-8") != "OK":
                logger.error("Error al obtener datos de la impresora con modelo %s", model)
                return {"status": False, "error": "Error al obtener datos de la impresora", "data": None}

            response = self._printer.PFultimo().decode("utf-8")
            response_data = response.split(",")

            if len(response_data) < 2:
                return {"status": False, "error": "Respuesta incompleta de la impresora", "data": None}

            # Procesar respuesta según el modelo
            if model == "V":  # Versión del FW
                if len(response_data) >= 8:
                    printer_state_code = response_data[3]  # Obtener estado de la impresora (Campo 4)
                    printer_state_desc = printer_states.get(printer_state_code, "Estado desconocido")
                    return {
                        "status": True,
                        "error": None,
                        "data": {
                            "sequence": response_data[2],  # Campo 3: Último valor de secuencia
                            "printer_state": {  # Campo 4: Estado actual de la impresora
                                "code": printer_state_code,
                                "description": printer_state_desc,
                            },
                            "last_command": int(response_data[4], 16),  # Campo 5: Código último comando (en decimal)
                            "date": format_date(response_data[5]),  # Campo 6: Fecha formateada
                            "time": format_time(response_data[6]),  # Campo 7: Hora formateada
                            "firmware_version": response_data[7],  # Campo 8: Version del firmware
                        },
                    }
            elif model == "U":  # IGTF factura y nota de crédito
                if len(response_data) >= 9:
                    return {
                        "status": True,
                        "error": None,
                        "data": {
                            "igtf_amount": str(response_data[7]),  # Campo 8: IGTF acumulado en el periodo
                            "credit_amount": str(response_data[8]),  # Campo 9: Crédito acumulado en el periodo
                        },
                    }
            elif model == "T":  # Número de última nota de crédito
                if len(response_data) >= 8:
                    return {
                        "status": True,
                        "error": None,
                        "data": {
                            "date": format_date(response_data[5]),  # Campo 6: Fecha formateada
                            "time": format_time(response_data[6]),  # Campo 7: Hora formateada
                            "last_credit_note": normalize_number(
                                response_data[7], 10
                            ),  # Campo 8: Último # de nota de crédito
                        },
                    }
            elif model == "N":  # Datos de los contadores
                if len(response_data) >= 11:
                    return {
                        "status": True,
                        "error": None,
                        "data": {
                            "date": format_date(response_data[5]),  # Campo 6: Fecha formateada
                            "time": format_time(response_data[6]),  # Campo 7: Hora formateada
                            "total_fiscal_docs": normalize_number(
                                response_data[7], 10
                            ),  # Campo 8: Total documentos fiscales
                            "last_document_invoice": normalize_number(
                                response_data[8], 8
                            ),  # Campo 9: Ultima factura fiscal
                            "last_document_note": normalize_number(
                                response_data[9], 8
                            ),  # Campo 10: Ultima nota no fiscal
                            "last_machine_report": normalize_number(response_data[10], 4),  # Campo 11: Último reporte Z
                        },
                    }

            # Si el modelo no coincide retornar error
            return {
                "status": False,
                "error": f"Modelo {model} no soportado o sin implementación específica",
                "data": None,
            }

        except Exception as e:
            logger.error("Error al obtener datos de la impresora: %s", str(e))
            return {"status": False, "error": str(e), "data": None}

    def report_x(self) -> bool:
        """Imprime reporte X (reporte diario sin cierre)"""
        try:
            response = self._printer.PFrepx()
            if response.decode("utf-8") != "OK":
                logger.error("Error en PFrepx: %s", response.decode("utf-8"))
                return False
            return True
        except Exception as e:
            logger.error("Error al generar reporte X: %s", str(e))
            return False

    def report_z(self) -> bool:
        """Imprime reporte Z (cierre diario)"""
        try:
            return self._printer.PFrepz()
        except Exception as e:
            logger.error("Error al generar reporte Z: %s", str(e))
            return False

    def print_document(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Imprime un documento fiscal
        Args:
            data (Dict[str, Any]): Documento a imprimir
        Returns:
            Dict[str, Any]: Resultado de la impresión
        """
        logger.debug("Procesando documento")
        try:
            operation_type = data.get("operation_type", "").lower()
            status = self.get_printer_status()
            message = f"Estado: {status['error_description']} | {status['status_description']}"

            if operation_type not in ("credit", "debit", "invoice", "note"):
                return {
                    "status": False,
                    "message": f"Tipo de documento no válido: {operation_type}",
                    "data": None,
                }
            logger.info(message)
            # Procesar datos del cliente
            self._process_customer_data(data, operation_type)
            # Procesar ítems
            self._process_items(data, operation_type)
            # Procesar pie de página
            self._process_footer(data, operation_type)
            # Procesar pagos
            self._process_payments(data, operation_type)
            # Procesar envio de datos
            return self._process_send_data(operation_type)

        except Exception as e:
            message = f"Falla durante la impresión del documento de tipo: {operation_type} [{str(e)}]"
            logger.error(message)
            return {"status": False, "message": message, "data": None}

    def _process_customer_data(self, data: Dict[str, Any], operation_type: str) -> None:
        """Procesa y envía los datos del cliente a la impresora."""
        logger.debug("Procesando datos del documento")

        customer = data.get("customer", {})
        customer_vat = self.format_text(customer.get("customer_vat", ""), "vat")
        customer_name = self.format_text(customer.get("customer_name", ""), "partner")
        customer_address = self.format_text(customer.get("customer_address", ""), "comment")
        customer_phone = self.format_text(customer.get("customer_phone", ""), "comment")
        customer_email = self.format_text(customer.get("customer_email", ""), "comment")

        document = data.get("document", {})
        document_number = normalize_number(document.get("document_number", ""))
        document_date = normalize_date(document.get("document_date", ""))
        document_name = self.format_text(document.get("document_name", ""), "comment")
        document_cashier = self.format_text(document.get("document_cashier", ""), "comment")

        commands = []
        if operation_type == "credit":
            affected_document = data.get("affected_document", {})
            affected_number = normalize_number(affected_document.get("affected_number", ""), 10)
            affected_date = normalize_date(affected_document.get("affected_date", ""))
            affected_serial = self.format_text(affected_document.get("affected_serial", ""), "comment")
            current_time = format_time(datetime.datetime.now().strftime("%H%M"))

            logger.info(
                "PFDevolucion(%s,%s,%s,%s,%s,%s)",
                customer_name,
                customer_vat,
                affected_number,
                affected_serial,
                affected_date,
                current_time,
            )
            result = self._printer.PFDevolucion(
                customer_name.encode(),
                customer_vat.encode(),
                affected_number.encode(),
                affected_serial.encode(),
                affected_date.encode(),
                current_time.encode(),
            )
            if result.decode("utf-8") != "OK":
                response = self.cancel_doc(operation_type)
                raise RuntimeError(f"Error al abrir la nota de credito || PFCancelaDoc: {response}")

        if operation_type in ("debit", "invoice"):
            logger.info("PFabrefiscal(%s,%s)", customer_name, customer_vat)
            result = self._printer.PFabrefiscal(customer_name.encode(), customer_vat.encode())
            if result.decode("utf-8") != "OK":
                response = self.cancel_doc(operation_type)
                raise RuntimeError(f"Error al abrir la factura || PFCancelaDoc: {response}")

        if operation_type in ("credit", "debit", "invoice"):
            include_line = {
                "include_partner_address": PNPcmd.PARTNER_ADDRESS.format(customer_address).encode(),
                "include_partner_phone": PNPcmd.PARTNER_PHONE.format(customer_phone).encode(),
                "include_partner_email": PNPcmd.PARTNER_EMAIL.format(customer_email).encode(),
                "include_document_number": PNPcmd.DOCUMENT_NUMBER.format(document_number).encode(),
                "include_document_date": PNPcmd.DOCUMENT_DATE.format(document_date).encode(),
                "include_document_name": PNPcmd.DOCUMENT_NAME.format(document_name).encode(),
                "include_document_cashier": PNPcmd.DOCUMENT_CASHIER.format(document_cashier).encode(),
            }

            format_config = self.template_config.get("format", {})
            lines_add = [value for key, value in include_line.items() if format_config.get(key, False)]

            if lines_add:
                for command in lines_add[:3]:
                    logger.info("PFTfiscal(%s)", command)
                    self._printer.PFTfiscal(command)
                logger.info("PFTfiscal(%s)", PNPcmd.INTER_LINE)
                self._printer.PFTfiscal(PNPcmd.INTER_LINE.encode())

        if operation_type == "note":
            name_note = self.template_config.get("fiscal", {}).get("name_note", "Nota").encode()

            result = self._printer.PFAbreNF()
            logger.info("PFAbreNF()")
            if result.decode("utf-8") != "OK":
                raise RuntimeError("Error al abrir documento NO fiscal")

            commands = [
                name_note,
                PNPcmd.INTER_LINE.encode(),
                PNPcmd.PARTNER_VAT.format(customer_vat).encode(),
                PNPcmd.PARTNER_NAME.format(customer_name).encode(),
                PNPcmd.PARTNER_ADDRESS.format(customer_address).encode(),
                PNPcmd.PARTNER_PHONE.format(customer_phone).encode(),
                PNPcmd.PARTNER_EMAIL.format(customer_email).encode(),
                PNPcmd.DOCUMENT_NUMBER.format(document_number).encode(),
                PNPcmd.DOCUMENT_DATE.format(document_date).encode(),
                PNPcmd.DOCUMENT_NAME.format(document_name).encode(),
                PNPcmd.DOCUMENT_CASHIER.format(document_cashier).encode(),
                PNPcmd.INTER_LINE.encode(),
            ]

            for command in commands:
                self._printer.PFLineaNF(command)
                logger.info("PFLineaNF(%s)", command.decode("utf-8"))

    def _process_items(self, data: Dict[str, Any], operation_type: str) -> None:
        """Procesa y envía los ítems del documento a la impresora."""
        logger.debug("Procesando items")

        for item in data.get("items", []):
            item_comment = self.format_text(item.get("item_comment", ""), "comment")
            if self.template_config.get("format", {}).get("include_item_reference", False):
                item_code = item.get("item_ref", "")
                item_product = item.get("item_name", "")
                item_name = self.format_text(f"[{item_code}] {item_product}", "product")
            else:
                item_name = self.format_text(item.get("item_name", ""), "product")

            item_quantity = self.format_number(item.get("item_quantity", 0), "quantity")
            item_price = self.format_number(item.get("item_price", 0), "price")
            item_tax = item.get("item_tax", "0")

            if operation_type == "note":
                item_line = f"{item_name} x{item_quantity} x{item_price} Iva:{item_tax}"

                result = self._printer.PFLineaNF(item_line.encode())
                logger.info("PFLineaNF(%s)", item_line)
                if result.decode("utf-8") != "OK":
                    response = self.cancel_doc(operation_type)
                    raise RuntimeError(f"Error al procesar ítem || PFCancelaDoc: {response}")

                if self.template_config.get("format", {}).get("include_item_comment", False) and item_comment:
                    self._printer.PFLineaNF(item_comment.encode())
                    logger.info("PFLineaNF(%s)", item_comment)
            else:
                tax_value = str(int(float(item_tax) * 100)).zfill(4)

                logger.info("PFrenglon(%s,%s,%s,%s)", item_name, item_quantity, item_price, tax_value)
                result = self._printer.PFrenglon(
                    item_name.encode(), item_quantity.encode(), item_price.encode(), tax_value.encode()
                )
                if result.decode("utf-8") != "OK":
                    response = self.cancel_doc(operation_type)
                    raise RuntimeError(f"Error al procesar ítem || PFCancelaDoc: {response}")

                if self.template_config.get("format", {}).get("include_item_comment", False) and item_comment:
                    logger.info("PFTfiscal(%s)", item_comment)
                    result = self._printer.PFTfiscal(item_comment.encode())
                    if result.decode("utf-8") != "OK":
                        raise RuntimeError(f"Error al procesar comentario: {item_comment}")

    def _process_footer(self, data: Dict[str, Any], operation_type: str) -> None:
        """Procesa el pie de página."""
        logger.debug("Procesando pie de página")

        delivery_comments = data.get("delivery", {}).get("delivery_comments", [])
        delivery_barcode = data.get("delivery", {}).get("delivery_barcode", "")

        if delivery_comments and self.template_config.get("format", {}).get("include_delivery_comments", False):
            if operation_type == "note":
                logger.info("PFLineaNF(%s)", PNPcmd.INTER_LINE)
                self._printer.PFLineaNF(PNPcmd.INTER_LINE.encode())
            else:
                logger.info("PFTfiscal(%s)", PNPcmd.INTER_LINE)
                self._printer.PFTfiscal(PNPcmd.INTER_LINE.encode())

            for comment in delivery_comments:
                line_comment = self.format_text(comment, "comment")
                if operation_type == "note":
                    self._printer.PFLineaNF(line_comment.encode())
                    logger.info("PFLineaNF(%s)", line_comment)
                else:
                    logger.info("PFTfiscal(%s)", line_comment)
                    result = self._printer.PFTfiscal(line_comment.encode())
                    if result.decode("utf-8") != "OK":
                        raise RuntimeError(f"Error al procesar delivery comments: {line_comment}")

        if delivery_barcode and self.template_config.get("format", {}).get("include_delivery_barcode", False):
            if operation_type == "note":
                self._printer.PFLineaNF(delivery_barcode.encode())
                logger.info("PFLineaNF(%s)", delivery_barcode)
            else:
                logger.info("PFBarra(%s)", delivery_barcode)  # Se usa PFTfiscal por error en el simulador
                result = self._printer.PFTfiscal(delivery_barcode.encode())  # Pendiente por probar funcion PFBarra
                if result.decode("utf-8") != "OK":
                    raise RuntimeError(f"Error al procesar código de barras: {delivery_barcode}")

    def _process_payments(self, data: Dict[str, Any], operation_type: str) -> None:
        """Procesa los métodos de pago del documento."""
        logger.debug("Procesando pagos")

        payments = data.get("payments", [])
        total_amount = sum(float(payment.get("payment_amount", 0)) for payment in payments)

        if operation_type == "note":
            self._printer.PFLineaNF(f"Monto Total: {total_amount}".encode())
            result = self._printer.PFCierraNF()
            logger.info("PFCierraNF(Monto Total %s)", total_amount)
            if result.decode("utf-8") != "OK":
                raise RuntimeError("Error al cerrar documento NO fiscal")
        else:
            if payments:
                mount_base = 0
                mount_igtf = 0
                sorted_payments = sorted(payments, key=lambda x: x["payment_method"], reverse=True)
                for payment in sorted_payments:
                    code = payment["payment_method"]
                    mount_base += payment["payment_amount"] if 1 <= int(code) <= 19 else 0
                    mount_igtf += payment["payment_amount"] if 20 <= int(code) <= 24 else 0

                if mount_igtf > 0:
                    formatted_igtf = self.format_number(mount_igtf, "payment").replace(".", "")
                    if not self.send_command(PNPcmd.CLOSE_PARTIAL_IGTF.format(formatted_igtf)):
                        raise RuntimeError("Error en pago con IGTF")

            time.sleep(1)
            result = self._printer.PFtotal()
            logger.info("PFtotal(%s)", total_amount)
            if result.decode("utf-8") != "OK":
                raise RuntimeError("Error al cerrar documento fiscal")

        response = self._printer.PFultimo().decode("utf-8").split(",")
        if operation_type == "note":
            self._last_document = response[2]
        if operation_type in ("debit", "invoice"):
            self._last_document = response[3]
        if operation_type == "credit":
            self._last_document = response[4]

    def _process_send_data(self, operation_type: str) -> Dict[str, Any]:
        """Obtiene los datos finales después de la impresión."""
        logger.debug("Obteniendo datos de los contadores finales")
        print(operation_type)
        try:
            machine_number = "EOO9000001"
            machine_report = "00000001"
            document_date = "2025-02-16"

            return {
                "status": True,
                "message": "Impresión finalizada exitosamente",
                "data": {
                    "document_date": document_date,
                    "document_number": self._last_document,
                    "machine_serial": machine_number,
                    "machine_report": machine_report,
                },
            }

        except Exception as e:
            logger.error("Error al obtener datos fiscales: %s", str(e))
            raise RuntimeError(f"Error al obtener datos fiscales: {str(e)}") from e
