#!/usr/bin/env python
"""
Copyright © 2024, Iron Graterol
Licensed under the GNU Affero General Public License, version 3 or later.

Document Handler Module, responsable de la gestión de las operaciones relacionadas con los documentos.
"""

import logging
from typing import Any

from flask import Response, current_app, jsonify, request
from jsonschema import ValidationError

from models.model_invoice import Invoice
from server.document_schema import validate_document
from server.handlers.job_store import acquire_job, complete_job, fail_job
from server.handlers.printer_manager import PrinterManager

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


def find_value(dictionary: dict[str, Any], key: str) -> Any | None:
    """
    Busca recursivamente un valor en un diccionario anidado.
    Args:
        dictionary: Diccionario en el que buscar.
        key: Clave a buscar.
    Returns:
        Any | None: Valor encontrado o None si no existe.
    """
    if key in dictionary:
        return dictionary[key]

    for value in dictionary.values():
        if isinstance(value, dict):
            result = find_value(value, key)
            if result is not None:
                return result
    return None


def error_response(message: str, status_code: int = HTTP_BAD_REQUEST, data: Any = None) -> tuple[Response, int]:
    """
    Crea una respuesta de error estandarizada.
    Args:
        message: Mensaje de error.
        status_code: Código HTTP de error.
        data: Datos adicionales opcionales.
    Returns:
        tuple[Response, int]: Respuesta JSON y código de estado.
    """
    if data:
        logger.error("%s - %s", message, data)
    else:
        logger.error("%s", message)
    return jsonify({"status": False, "message": message, "data": data}), status_code


def printer_instance(
    printer_config: dict[str, Any],
) -> tuple[Any | None, dict[str, Any] | None]:
    """
    Crea una instancia de la impresora según la configuración.
    Args:
        printer_config: Configuración de impresoras.
    Returns:
        tuple[Any | None, dict[str, Any] | None]:
            - Instancia de la impresora o None si no hay impresora disponible
            - Diccionario con información del error si ocurrió uno, None si no hay error
    """
    try:
        printer_fiscal_enabled = find_value(printer_config, "fiscal_enabled")
        printer_matrix_enabled = find_value(printer_config, "matrix_enabled")
        printer_ticket_enabled = find_value(printer_config, "ticket_enabled")

        if printer_fiscal_enabled:
            printer_fiscal_name = find_value(printer_config, "fiscal_name").strip().lower()
            fiscal_config = printer_config.get("fiscal", {})
            try:
                printer = PrinterManager.get_printer(printer_fiscal_name, fiscal_config)
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


def _complete_job_safely(document_id: str, operation_type: str, response: dict[str, Any]) -> bool:
    """
    Registra un trabajo como completado, con un reintento si falla el registro.

    Si ambos intentos fallan, el trabajo queda deliberadamente en 'processing': el documento ya
    fue emitido y marcarlo como fallido permitiría reimprimirlo (doble documento fiscal).
    Args:
        document_id: Clave de idempotencia del documento
        operation_type: Tipo de operación
        response: Respuesta enviada a Odoo, que se guarda como caché
    Returns:
        bool: True si el trabajo quedó registrado como completado
    """
    for attempt in (1, 2):
        try:
            complete_job(document_id, operation_type, response)
            return True
        except Exception as e:  # noqa: BLE001 - red de seguridad: cualquier error de la base de trabajos
            logger.error(
                "Intento %s: no se pudo registrar el trabajo %s/%s: %s", attempt, document_id, operation_type, e
            )
    logger.critical(
        "Documento %s/%s IMPRESO pero no registrado como completado; queda en 'processing' para evitar "
        "una reimpresión. Respuesta: %s",
        document_id,
        operation_type,
        response,
    )
    return False


def _fail_job_safely(document_id: str, operation_type: str, error_message: str) -> None:
    """
    Registra un trabajo como fallido sin propagar errores de la base de trabajos.
    Args:
        document_id: Clave de idempotencia del documento
        operation_type: Tipo de operación
        error_message: Motivo de la falla
    """
    try:
        fail_job(document_id, operation_type, error_message)
    except Exception as e:  # noqa: BLE001 - red de seguridad: cualquier error de la base de trabajos
        logger.critical("No se pudo registrar como fallido el trabajo %s/%s: %s", document_id, operation_type, e)


def handle_documents(proxy_handler: Any | None = None) -> tuple[Response, int]:
    """
    Maneja la solicitud de impresión de documentos.
    Esta función procesa la solicitud de impresión, valida los datos recibidos,
    verifica reglas de negocio, aplica idempotencia y envía el documento a la impresora correspondiente.
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

        # Idempotency check — must happen before touching the serial port
        acquire_result, cached_response = acquire_job(invoice.document_number, invoice.operation_type)

        if acquire_result == "duplicate":
            return jsonify(cached_response)

        if acquire_result == "in_progress":
            return (
                jsonify({"status": False, "message": "Solicitud en curso, intente nuevamente en unos segundos"}),
                409,
            )

        # acquire_result is 'new' or 'retry' — proceed
        # Desde aquí el trabajo está en 'processing': toda salida debe dejarlo en un estado final,
        # o Odoo recibiría 409 indefinidamente para este documento.
        try:
            printers_config = current_app.config.get("printers", {})  # Obtener configuración de impresoras
            printer, error_data = printer_instance(printers_config)
            if not printer:
                if error_data:
                    if "state" in error_data and "error" in error_data:
                        message = (
                            f"Impresora no disponible - Estado: {error_data['state']}, Error: {error_data['error']}"
                        )
                    else:
                        message = error_data.get("message", "Error desconocido al obtener la impresora")
                    fail_job(invoice.document_number, invoice.operation_type, message)
                    return error_response(message, data=error_data)
                fail_job(invoice.document_number, invoice.operation_type, "No hay impresoras habilitadas")
                return error_response("No hay impresoras habilitadas para procesar el documento")

            result = printer.print_document(data)  # Procesar el documento
            logger.debug("Documento result= %s", result)
        except Exception as e:  # Cualquier falla debe liberar el trabajo
            # Falla antes o durante la impresión: misma semántica que un error devuelto por el driver,
            # que cancela el documento abierto en la máquina. Se libera el trabajo para permitir el reintento.
            error_msg = f"Error interno durante la impresión: {e!s}"
            logger.exception("Documento %s: %s", invoice.document_number, error_msg)
            _fail_job_safely(invoice.document_number, invoice.operation_type, error_msg)
            return error_response(error_msg, HTTP_INTERNAL_ERROR)

        if result.get("status", False):
            response_payload = {
                "status": True,
                "message": result.get("message", "Documento procesado correctamente"),
                "data": result.get("data", {}),
            }
            # El documento ya fue emitido: aunque no se pueda registrar, se responde con éxito para que
            # Odoo guarde el número fiscal. Nunca se marca como fallido (evita una doble impresión).
            _complete_job_safely(invoice.document_number, invoice.operation_type, response_payload)
            logger.info("Documento Origen: %s, impreso correctamente", invoice.document_number)
            return jsonify(response_payload)

        error_msg = result.get("message", "Error desconocido al imprimir")
        _fail_job_safely(invoice.document_number, invoice.operation_type, error_msg)
        return error_response(error_msg, data=result.get("data"))

    except Exception as e:
        return error_response(f"Error interno del servidor: {str(e)}", HTTP_INTERNAL_ERROR)


def handle_reports(report_type: str) -> tuple[Response, int]:
    """
    Maneja la solicitud de impresión de reportes fiscales.
    Args:
        report_type: Tipo de reporte ('X' o 'Z')
    Returns:
        tuple[Response, int]: Respuesta JSON y código de estado HTTP
    """
    try:
        logger.info("Recibida solicitud de reporte %s", report_type)

        printers_config = current_app.config.get("printers", {})
        fiscal_config = printers_config.get("fiscal", {})

        if not fiscal_config or not fiscal_config.get("fiscal_enabled", False):
            return error_response("Impresora fiscal no está habilitada")

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


def handle_report_x() -> tuple[Response, int]:
    """Maneja la impresión del reporte X"""
    return handle_reports("X")


def handle_report_z() -> tuple[Response, int]:
    """Maneja la impresión del reporte Z"""
    return handle_reports("Z")


def handle_fiscal_commands() -> tuple[Response, int]:
    """
    Maneja el envío de comandos directos a la impresora fiscal.
    Esperar payload: {"commands": ["CMD1", "CMD2"]}
    """
    try:
        data = request.get_json(silent=True) or {}
        commands = data.get("commands")

        if not isinstance(commands, list) or not commands:
            return error_response("'commands' debe ser una lista no vacía")

        logger.info("Recibida solicitud de comandos directos: %s", commands)

        printers_config = current_app.config.get("printers", {})
        fiscal_config = printers_config.get("fiscal", {})

        if not fiscal_config or not fiscal_config.get("fiscal_enabled", False):
            return error_response("Impresora fiscal no está habilitada")

        printer, error_data = printer_instance(printers_config)
        if not printer:
            message = (
                error_data.get("message", "Error fiscal desconocido")
                if error_data
                else "No se pudo obtener la impresora fiscal"
            )
            return error_response(message, data=error_data)

        if not printer.check_status():
            fiscal_name = printers_config.get("fiscal", {}).get("fiscal_name", "").strip().lower()
            PrinterManager.remove_printer(fiscal_name)
            printer, error_data = printer_instance(printers_config)
            if not printer:
                message = (
                    error_data.get("message", "Error al reconectar con la impresora")
                    if error_data
                    else "No se pudo reconectar con la impresora fiscal"
                )
                return error_response(message, data=error_data)
            if not printer.check_status():
                return error_response("La impresora fiscal no está lista")

        results = []
        for cmd in commands:
            success = printer.send_command(cmd)
            results.append({"command": cmd, "success": success})

        return jsonify({"status": True, "message": "Comandos procesados", "data": results}), 200

    except Exception as e:
        return error_response(f"Error procesando comandos: {str(e)}", HTTP_INTERNAL_ERROR)
