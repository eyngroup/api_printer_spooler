#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Document Handler Module, responsable de la gestión de las operaciones relacionadas con los documentos."""

import logging
from typing import Dict, Any, Optional, Tuple

from flask import jsonify, request, current_app, Response
from jsonschema import ValidationError

from models.model_invoice import Invoice
from .printer_manager import PrinterManager
from ..document_schema import validate_document

HTTP_BAD_REQUEST = 400
HTTP_INTERNAL_ERROR = 500
PRINTER_TYPE_FISCAL = "fiscal"
PRINTER_TYPE_MATRIX = "matrix"
PRINTER_TYPE_TICKET = "ticket"

PRINTER_FISCAL_TYPES = {
    "tfhka": "printers.printer_hka.TfhkaPrinter",
    "pnp": "printers.printer_pnp.PnpPrinter",
}

logger = logging.getLogger(__name__)


def find_value(dictionary: Dict[str, Any], key: str) -> Optional[Any]:
    """
    Busca recursivamente un valor en un diccionario anidado.
    Args:
        dictionary: Diccionario en el que buscar.
        key: Clave a buscar.
    Returns:
        Optional[Any]: Valor encontrado o None si no existe.
    """
    if key in dictionary:
        return dictionary[key]

    for value in dictionary.values():
        if isinstance(value, dict):
            result = find_value(value, key)
            if result is not None:
                return result
    return None


def error_response(message: str, status_code: int = HTTP_BAD_REQUEST, data: Any = None) -> Tuple[Response, int]:
    """
    Crea una respuesta de error estandarizada.
    Args:
        message: Mensaje de error.
        status_code: Código HTTP de error.
        data: Datos adicionales opcionales.
    Returns:
        Tuple[Response, int]: Respuesta JSON y código de estado.
    """
    if data:
        logger.error("%s - %s", message, data)
    else:
        logger.error("%s", message)
    return jsonify({"status": False, "message": message, "data": data}), status_code


def printer_instance(
    printer_config: Dict[str, Any],
) -> Tuple[Optional[Any], Optional[Dict[str, Any]]]:
    """
    Crea una instancia de la impresora según la configuración.
    Args:
        printer_config: Configuración de impresoras.
    Returns:
        Tuple[Optional[Any], Optional[Dict[str, Any]]]:
            - Instancia de la impresora o None si no hay impresora disponible
            - Diccionario con información del error si ocurrió uno, None si no hay error
    """
    try:
        printer_fiscal_enabled = find_value(printer_config, "fiscal_enabled")
        printer_matrix_enabled = find_value(printer_config, "matrix_enabled")
        printer_ticket_enabled = find_value(printer_config, "ticket_enabled")

        if printer_fiscal_enabled:
            printer_fiscal_name = find_value(printer_config, "fiscal_name").strip().lower()
            try:
                printer = PrinterManager.get_printer(
                    printer_fiscal_name, find_value(printer_config, PRINTER_TYPE_FISCAL)
                )
                return printer, None
            except ValueError as e:
                error_msg = str(e)
                if "Estado:" in error_msg and "Error:" in error_msg:
                    state = error_msg.split("Estado:")[1].split(",")[0].strip()
                    error = error_msg.split("Error:")[1].strip()
                    return None, {
                        "printer_type": printer_fiscal_name,
                        "state": state,
                        "error": error,
                        "message": error_msg,
                    }
                return None, {"printer_type": printer_fiscal_name, "message": error_msg}

        if printer_matrix_enabled:
            from printers.printer_dotmatrix import MatrixPrinter

            return MatrixPrinter(find_value(printer_config, PRINTER_TYPE_MATRIX)), None

        if printer_ticket_enabled:
            from printers.printer_ticket import TicketPrinter

            return TicketPrinter(find_value(printer_config, PRINTER_TYPE_TICKET)), None

        return None, {"message": "No hay impresoras configuradas"}

    except Exception as e:
        return None, {"message": str(e)}


def handle_documents(proxy_handler: Optional[Any] = None) -> Tuple[Response, int]:
    """
    Maneja la solicitud de impresión de documentos.
    Esta función procesa la solicitud de impresión, valida los datos recibidos,
    selecciona la impresora apropiada y ejecuta la impresión del documento.
    Args:
        proxy_handler: Manejador de proxy opcional para reenviar la solicitud.
    Returns:
        Tuple[Response, int]: Respuesta JSON y código de estado HTTP.
    """
    if proxy_handler:
        return proxy_handler.handle_request()

    try:
        data = request.get_json()
        logger.info("Recibida solicitud de impresión")
        logger.debug("Datos recibidos en handle_print_document: %s", data)

        if not data:
            return error_response("No se recibieron datos en la solicitud")

        try:
            validate_document(data)
        except ValidationError as e:
            return error_response(f"Error de validación en el formato del documento: {str(e)}")

        try:  # Validar reglas de negocio del documento
            invoice = Invoice(data)
            if validation_error := invoice.validate():
                return error_response(f"Error de validación de negocio: {validation_error}")

            logger.info(
                "Documento validado: %s - Tipo: %s",
                invoice.document_number,
                invoice.operation_type,
            )
        except Exception as e:
            return error_response(f"Error al validar reglas de negocio del documento: {str(e)}")

        printers_config = current_app.config.get("printers", {})  # Obtener configuración de impresoras
        printer, error_data = printer_instance(printers_config)
        if not printer:
            if error_data:
                if "state" in error_data and "error" in error_data:
                    message = f"Impresora no disponible - Estado: {error_data['state']}, Error: {error_data['error']}"
                else:
                    message = error_data.get("message", "Error desconocido al obtener la impresora")
                return error_response(message, data=error_data)
            return error_response("No hay impresoras habilitadas para procesar el documento")

        result = printer.print_document(data)  # Procesar el documento
        logger.debug("Documento result= %s", result)

        if result.get("status", False):
            logger.info("Documento %s impreso correctamente", invoice.document_number)
            return jsonify(
                {
                    "status": True,
                    "message": result.get("message", "Documento procesado correctamente"),
                    "data": result.get("data", {}),
                }
            )

        return error_response(
            result.get("message", "Error desconocido al imprimir"),
            data=result.get("data"),
        )

    except Exception as e:
        return error_response(f"Error interno del servidor: {str(e)}", HTTP_INTERNAL_ERROR)


def handle_reports(report_type: str) -> Tuple[Response, int]:
    """
    Maneja la solicitud de impresión de reportes fiscales.
    Args:
        report_type: Tipo de reporte ('X' o 'Z')
    Returns:
        Tuple[Response, int]: Respuesta JSON y código de estado HTTP
    """
    try:
        logger.info("Recibida solicitud de reporte %s", report_type)

        printers_config = current_app.config.get("printers", {})
        fiscal_config = printers_config.get("fiscal", {})

        if not fiscal_config or not fiscal_config.get("fiscal_enabled", False):
            return error_response("Impresora fiscal no está habilitada")

        # Obtener instancia de la impresora usando PrinterManager
        # printer_name = fiscal_config.get("fiscal_name", "").lower()  # pylint: disable=W0612
        printer, error_data = printer_instance(printers_config)

        if not printer:
            if error_data:
                return error_response(error_data["message"], data=error_data)
            return error_response("No se pudo obtener la impresora fiscal")

        if not printer.check_status():  # Verificar que la impresora está lista
            return error_response("La impresora fiscal no está lista")

        method = f"report_{report_type.lower()}"  # Imprimir reporte
        if not hasattr(printer, method):
            return error_response(f"Esta impresora no soporta reportes {report_type}")

        logger.info("Imprimiendo reporte %s", report_type)
        result = getattr(printer, method)()

        if result:
            return (
                jsonify(
                    {
                        "status": True,
                        "message": f"Reporte {report_type} impreso correctamente",
                    }
                ),
                200,
            )
        return error_response(f"Error al imprimir reporte {report_type}")

    except Exception as e:
        return error_response(f"Error al imprimir reporte {report_type}: {str(e)}", HTTP_INTERNAL_ERROR)


def handle_report_x() -> Tuple[Response, int]:
    """Maneja la impresión del reporte X"""
    return handle_reports("X")


def handle_report_z() -> Tuple[Response, int]:
    """Maneja la impresión del reporte Z"""
    return handle_reports("Z")
