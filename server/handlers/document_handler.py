#!/usr/bin/env python
"""
Copyright © 2024, Iron Graterol
Licensed under the GNU Affero General Public License, version 3 or later.

Document Handler Module, responsable de la gestión de las operaciones relacionadas con los documentos.
"""

import logging
import re
import time
from typing import Any

from flask import Response, current_app, jsonify, request
from jsonschema import ValidationError

from models.model_invoice import Invoice
from server.document_schema import validate_document
from server.handlers.job_store import (
    acquire_job,
    complete_job,
    completed_since,
    fail_job,
    get_job,
    mark_unknown,
    restart_job,
    set_counter_before,
)
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

# Comando directo de cierre Z (I0Z, I1Z, I2Z, I3Z): tras él se ajusta el reloj de la máquina
Z_COMMAND_PATTERN = re.compile(r"I\dZ", re.IGNORECASE)
# Espera tras un Z enviado como comando directo (el driver de reportes ya espera 3 s por su cuenta)
CLOCK_SYNC_DELAY_SECONDS = 2


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


def failure_data(state: str, error: str, /, **extra: Any) -> dict[str, Any]:
    """
    Construye el bloque de datos de una falla con el contrato que espera Odoo (Estado y Error).
    Args:
        state: Texto del estado (se envía como "Estado").
        error: Texto del error (se envía como "Error").
        **extra: Claves adicionales a conservar en el bloque.
    Returns:
        dict[str, Any]: Diccionario con "Estado", "Error" y las claves adicionales.
    """
    return {"Estado": state, "Error": error, **extra}


def _normalize_failure_data(data: Any, message: str, state: str) -> dict[str, Any]:
    """
    Garantiza que los datos de una respuesta de falla sean siempre un diccionario con Estado y Error.
    Args:
        data: Datos originales (None, lista, diccionario u otro valor).
        message: Mensaje de la falla, usado como Error cuando los datos no lo traen.
        state: Estado por defecto cuando los datos no lo traen.
    Returns:
        dict[str, Any]: Diccionario con "Estado" y "Error" siempre presentes.
    """
    if data is None:
        return failure_data(state, message)
    if isinstance(data, list):
        return failure_data(state, message, results=data)
    if isinstance(data, dict):
        if "Estado" in data and "Error" in data:
            return data
        return {**data, "Estado": data.get("Estado", state), "Error": data.get("Error", message)}
    return failure_data(state, message, results=data)


def error_response(
    message: str, status_code: int = HTTP_BAD_REQUEST, data: Any = None, state: str = "Error interno"
) -> tuple[Response, int]:
    """
    Crea una respuesta de error estandarizada.
    El campo data siempre es un diccionario con "Estado" y "Error" (Odoo los lee cuando status es false).
    Args:
        message: Mensaje de error.
        status_code: Código HTTP de error.
        data: Datos adicionales opcionales. Una lista se conserva bajo la clave "results".
        state: Estado por defecto cuando los datos no incluyen "Estado".
    Returns:
        tuple[Response, int]: Respuesta JSON y código de estado.
    """
    data = _normalize_failure_data(data, message, state)
    logger.error("%s - %s", message, data)
    return jsonify({"status": False, "message": message, "data": data}), status_code


def _fill_status_from_printer(printer: Any, data: Any) -> Any:
    """
    Completa Estado/Error de una falla de impresión con el estado actual de la impresora.
    Hace un único intento y nunca lanza excepciones: la respuesta de error no debe fallar por esto.
    Args:
        printer: Instancia de la impresora (puede ser None).
        data: Datos de la falla devueltos por el driver (puede ser None).
    Returns:
        Any: Los datos originales, o un diccionario con Estado/Error si se pudo leer el estado.
    """
    if printer is None or (isinstance(data, dict) and "Estado" in data and "Error" in data):
        return data
    try:
        status = printer.get_printer_status()
        state, error = printer.format_status_message(status)
        if not isinstance(state, str) or not isinstance(error, str):
            return data
        base = data if isinstance(data, dict) else {}
        return {**base, "Estado": state, "Error": error}
    except Exception as e:  # noqa: BLE001 - mejora opcional: cualquier fallo al leer el estado se ignora
        logger.warning("No se pudo leer el estado de la impresora tras la falla: %s", e)
        return data


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
                    state = error_msg.rsplit("Estado:", 1)[1].split(",")[0].strip()
                    error = error_msg.rsplit("Error:", 1)[1].strip()
                    return None, failure_data(
                        state,
                        error,
                        printer_type=printer_fiscal_name,
                        state=state,
                        error=error,
                        message=error_msg,
                    )
                return None, failure_data(
                    "Impresora no disponible", error_msg, printer_type=printer_fiscal_name, message=error_msg
                )

        if printer_matrix_enabled:
            from printers.printer_dotmatrix import MatrixPrinter

            return MatrixPrinter(find_value(printer_config, PRINTER_TYPE_MATRIX)), None

        if printer_ticket_enabled:
            from printers.printer_ticket import TicketPrinter

            return TicketPrinter(find_value(printer_config, PRINTER_TYPE_TICKET)), None

        return None, failure_data(
            "Impresora no disponible", "No hay impresoras configuradas", message="No hay impresoras configuradas"
        )

    except Exception as e:
        return None, failure_data("Impresora no disponible", str(e), message=str(e))


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


UNKNOWN_RESULT_MESSAGE = "No se pudo verificar si el documento se emitió; verifíquelo en la máquina antes de reintentar"


def _unknown_payload() -> dict[str, Any]:
    """
    Construye la respuesta cuando no se puede saber si la máquina emitió el documento.
    Returns:
        dict[str, Any]: Payload con status False y Estado/Error ("Resultado desconocido")
    """
    return {
        "status": False,
        "message": UNKNOWN_RESULT_MESSAGE,
        "data": failure_data("Resultado desconocido", UNKNOWN_RESULT_MESSAGE),
    }


def _issued_payload(
    printer_type: str, fiscal_config: dict[str, Any], operation_type: str, after: str
) -> dict[str, Any]:
    """
    Construye la respuesta de éxito de un documento que la máquina emitió pese a la falla de comunicación.

    Intenta obtener los datos fiscales completos de la instancia viva (`_process_send_data`, que los arma
    desde S1) y los acepta solo si su número coincide con el leído; si no, devuelve al menos el número y el
    serial de la máquina. No incluye el total: S2 se reinicia tras el cierre.
    Args:
        printer_type: Tipo de impresora fiscal
        fiscal_config: Configuración de la impresora fiscal
        operation_type: Tipo de operación
        after: Último número leído de la máquina tras la falla
    Returns:
        dict[str, Any]: Payload de éxito para Odoo
    """
    document_number = str(after).strip().zfill(8)
    data: dict[str, Any] | None = None
    try:
        instance = PrinterManager._instances.get(printer_type)
        if instance is not None:
            full = instance._process_send_data(operation_type)
            candidate = dict((full or {}).get("data") or {})
            if candidate.get("document_number") == document_number:
                candidate.pop("total", None)
                data = candidate
    except Exception as e:  # noqa: BLE001 - mejora opcional: si falla se usan los datos mínimos
        logger.warning("No se pudieron leer los datos fiscales completos tras la conciliación: %s", e)
    if data is None:
        data = {"document_number": document_number}
        # Sin instancia viva (p. ej. tras una caída): fecha, Z y serial de la misma lectura S1 de la máquina
        summary = PrinterManager.read_fiscal_summary(printer_type, fiscal_config)
        if summary:
            data.update(summary)
        else:
            serial = PrinterManager.read_serial(printer_type, fiscal_config)
            if serial:
                data["machine_serial"] = serial
    return {
        "status": True,
        "message": "Documento emitido (verificado en la máquina tras una falla de comunicación)",
        "data": data,
    }


def _reconcile(
    printer_type: str, fiscal_config: dict[str, Any], invoice: Any, job: dict[str, Any]
) -> tuple[str, dict[str, Any] | None]:
    """
    Concilia un trabajo dudoso con el contador de la máquina (única fuente de verdad).

    Compara el contador guardado antes de imprimir con el actual:
      - igual al previo + 1 y sin otros documentos del tipo completados desde entonces: "issued";
      - igual al previo: "not_issued" (la máquina no emitió nada);
      - cualquier otro caso (sin lectura, saltos, otro documento intermedio, no numérico): "unknown".
    Nunca lanza excepciones.
    Args:
        printer_type: Tipo de impresora fiscal
        fiscal_config: Configuración de la impresora fiscal
        invoice: Documento validado (document_number, operation_type)
        job: Trabajo registrado (get_job) con counter_before y created_at
    Returns:
        tuple[str, dict | None]: ("issued", payload de éxito), ("not_issued", None) o
        ("unknown", payload de resultado desconocido)
    """
    unknown = ("unknown", _unknown_payload())
    try:
        before = job.get("counter_before")
        if before is None:
            logger.warning("Documento %s: sin contador previo; no se puede conciliar", invoice.document_number)
            return unknown
        after = PrinterManager.read_last_document_number(printer_type, fiscal_config, invoice.operation_type)
        if after is None:
            logger.warning("Documento %s: no se pudo leer el contador de la máquina", invoice.document_number)
            return unknown
        try:
            before_n, after_n = int(before), int(after)
        except (TypeError, ValueError):
            return unknown
        if after_n == before_n:
            return "not_issued", None
        if (
            after_n == before_n + 1
            and completed_since(invoice.operation_type, job["created_at"], invoice.document_number) == 0
        ):
            logger.warning(
                "Documento %s: la máquina lo emitió (contador %s -> %s) pese a la falla de comunicación",
                invoice.document_number,
                before,
                after,
            )
            return "issued", _issued_payload(printer_type, fiscal_config, invoice.operation_type, str(after))
        logger.warning(
            "Documento %s: contador inconsistente (antes %s, ahora %s); resultado desconocido",
            invoice.document_number,
            before,
            after,
        )
        return unknown
    except Exception:
        logger.exception("Documento %s: error al conciliar con la máquina", invoice.document_number)
        return unknown


def _mark_unknown_safely(document_id: str, operation_type: str, error_message: str) -> None:
    """
    Marca un trabajo como de resultado desconocido sin propagar errores de la base de trabajos.
    Args:
        document_id: Clave de idempotencia del documento
        operation_type: Tipo de operación
        error_message: Motivo de la incertidumbre
    """
    try:
        mark_unknown(document_id, operation_type, error_message)
    except Exception as e:  # noqa: BLE001 - red de seguridad: cualquier error de la base de trabajos
        logger.critical("No se pudo marcar como desconocido el trabajo %s/%s: %s", document_id, operation_type, e)


def _resolve_unknown_job(printer_type: str, fiscal_config: dict[str, Any], invoice: Any) -> tuple[Response, int] | None:
    """
    Resuelve un trabajo en estado 'unknown' consultando el contador de la máquina antes de imprimir.
    Args:
        printer_type: Tipo de impresora fiscal
        fiscal_config: Configuración de la impresora fiscal
        invoice: Documento validado
    Returns:
        tuple[Response, int] | None: Respuesta final (emitido o aún desconocido), o None si se comprobó
        que NO se emitió y el trabajo quedó en 'processing' para imprimir normalmente
    """
    job = get_job(invoice.document_number, invoice.operation_type)
    if job is None:
        return error_response("Trabajo no encontrado al conciliar", HTTP_INTERNAL_ERROR)
    outcome, payload = _reconcile(printer_type, fiscal_config, invoice, job)
    if outcome == "issued":
        _complete_job_safely(invoice.document_number, invoice.operation_type, payload)
        return jsonify(payload), 200
    if outcome == "not_issued":
        if restart_job(invoice.document_number, invoice.operation_type):
            logger.info("Documento %s: no se emitió en la máquina; se reintenta la impresión", invoice.document_number)
            return None
        # Otra solicitud ya tomó el reintento
        return (
            jsonify({"status": False, "message": "Solicitud en curso, intente nuevamente en unos segundos"}),
            409,
        )
    logger.error("Documento %s: resultado aún desconocido", invoice.document_number)
    return jsonify(payload), HTTP_BAD_REQUEST


def _reconcile_failed_print(
    printer_type: str, fiscal_config: dict[str, Any], invoice: Any
) -> tuple[Response, int] | None:
    """
    Concilia con la máquina una impresión fallida cuyo contador previo se conoce.
    Args:
        printer_type: Tipo de impresora fiscal
        fiscal_config: Configuración de la impresora fiscal
        invoice: Documento validado
    Returns:
        tuple[Response, int] | None: Respuesta de éxito (emitido) o de resultado desconocido (el trabajo
        queda en 'unknown'); None si no se emitió y se debe aplicar el manejo de falla habitual
    """
    job = get_job(invoice.document_number, invoice.operation_type)
    outcome, payload = _reconcile(printer_type, fiscal_config, invoice, job) if job else ("unknown", _unknown_payload())
    if outcome == "issued":
        _complete_job_safely(invoice.document_number, invoice.operation_type, payload)
        return jsonify(payload), 200
    if outcome == "unknown":
        _mark_unknown_safely(invoice.document_number, invoice.operation_type, UNKNOWN_RESULT_MESSAGE)
        return jsonify(payload), HTTP_BAD_REQUEST
    return None


def _read_counter_before(printer: Any, invoice: Any) -> str | None:
    """
    Lee y guarda el contador de la máquina antes de imprimir (solo impresoras que lo soportan, HKA).
    Nunca lanza excepciones; sin lectura válida no se guarda nada y la falla se trata como siempre.
    Args:
        printer: Instancia de la impresora
        invoice: Documento validado
    Returns:
        str | None: Último número leído, o None si no aplica o no se pudo leer
    """
    try:
        reader = getattr(printer, "read_last_document_number", None)
        if not callable(reader):
            return None
        value = reader(invoice.operation_type)
        if not isinstance(value, str) or not value.strip():
            return None
        value = value.strip()
        set_counter_before(invoice.document_number, invoice.operation_type, value)
        return value
    except Exception as e:  # noqa: BLE001 - mejora opcional: sin contador previo se mantiene el flujo habitual
        logger.warning("No se pudo registrar el contador previo del documento %s: %s", invoice.document_number, e)
        return None


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
            return error_response("No se recibieron datos en la solicitud", state="Documento rechazado")

        try:
            validate_document(data)
        except ValidationError as e:
            return error_response(
                f"Error de validación en el formato del documento: {str(e)}", state="Documento rechazado"
            )

        try:  # Validar reglas de negocio del documento
            invoice = Invoice(data)
            if validation_error := invoice.validate():
                return error_response(
                    f"Error de validación de negocio: {validation_error}", state="Documento rechazado"
                )

            logger.info(
                "Documento validado: %s - Tipo: %s",
                invoice.document_number,
                invoice.operation_type,
            )
        except Exception as e:
            return error_response(
                f"Error al validar reglas de negocio del documento: {str(e)}", state="Documento rechazado"
            )

        # Idempotency check — must happen before touching the serial port
        acquire_result, cached_response = acquire_job(invoice.document_number, invoice.operation_type)

        if acquire_result == "duplicate":
            return jsonify(cached_response)

        if acquire_result == "in_progress":
            return (
                jsonify({"status": False, "message": "Solicitud en curso, intente nuevamente en unos segundos"}),
                409,
            )

        printers_config = current_app.config.get("printers", {})  # Obtener configuración de impresoras
        fiscal_config = printers_config.get("fiscal", {}) or {}
        fiscal_name = find_value(printers_config, "fiscal_name")
        printer_type = str(fiscal_name or "").strip().lower()

        if acquire_result == "unknown":
            # No se sabe si la máquina emitió el documento: se concilia con su contador antes de imprimir
            resolved = _resolve_unknown_job(printer_type, fiscal_config, invoice)
            if resolved is not None:
                return resolved

        # acquire_result is 'new' or 'retry' (o 'unknown' ya conciliado como no emitido) — proceed
        # Desde aquí el trabajo está en 'processing': toda salida debe dejarlo en un estado final,
        # o Odoo recibiría 409 indefinidamente para este documento.
        printer = None
        counter_before = None  # Contador de la máquina antes de imprimir (solo HKA)
        try:
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
                    return error_response(message, data=error_data, state="Impresora no disponible")
                fail_job(invoice.document_number, invoice.operation_type, "No hay impresoras habilitadas")
                return error_response(
                    "No hay impresoras habilitadas para procesar el documento", state="Impresora no disponible"
                )

            counter_before = _read_counter_before(printer, invoice)
            result = printer.print_document(data)  # Procesar el documento
            logger.debug("Documento result= %s", result)
        except Exception as e:  # Cualquier falla debe liberar el trabajo
            # Falla antes o durante la impresión: misma semántica que un error devuelto por el driver,
            # que cancela el documento abierto en la máquina. Se libera el trabajo para permitir el reintento.
            error_msg = f"Error interno durante la impresión: {e!s}"
            logger.exception("Documento %s: %s", invoice.document_number, error_msg)
            if counter_before is not None:
                # La máquina pudo emitir el documento antes de la falla: se verifica con su contador
                reconciled = _reconcile_failed_print(printer_type, fiscal_config, invoice)
                if reconciled is not None:
                    return reconciled
            _fail_job_safely(invoice.document_number, invoice.operation_type, error_msg)
            # Si la impresora existe, se intenta informar su estado real (una sola lectura, sin fallar).
            return error_response(error_msg, HTTP_INTERNAL_ERROR, data=_fill_status_from_printer(printer, None))

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
        if result.get("printed"):
            # El documento salió impreso pero sin número fiscal (p. ej. PNP con respuesta de cierre corta):
            # se guarda la respuesta como completada para que un reintento de Odoo nunca lo reimprima.
            failure_payload = {
                "status": False,
                "message": error_msg,
                "data": _normalize_failure_data(result.get("data"), error_msg, "Documento impreso"),
            }
            _complete_job_safely(invoice.document_number, invoice.operation_type, failure_payload)
            logger.error("Documento %s impreso sin número fiscal: %s", invoice.document_number, error_msg)
            return jsonify(failure_payload), HTTP_BAD_REQUEST

        if counter_before is not None:
            # El driver reportó falla (p. ej. USB cortado tras el cierre): se verifica en la máquina
            reconciled = _reconcile_failed_print(printer_type, fiscal_config, invoice)
            if reconciled is not None:
                return reconciled

        _fail_job_safely(invoice.document_number, invoice.operation_type, error_msg)
        return error_response(
            error_msg,
            data=_fill_status_from_printer(printer, result.get("data")),
            state="Error de impresión",
        )

    except Exception as e:
        return error_response(f"Error interno del servidor: {str(e)}", HTTP_INTERNAL_ERROR)


def _sync_clock_after_z(printers_config: dict[str, Any], wait_seconds: float = 0) -> dict[str, Any] | None:
    """
    Ajusta el reloj de la impresora HKA justo después de un reporte Z exitoso.

    Un fallo del ajuste NUNCA debe convertir en falla un Z que ya se emitió: el resultado (incluso un error)
    se devuelve para informarlo en la respuesta. Solo aplica a la impresora fiscal tfhka.
    Args:
        printers_config: Configuración de impresoras de la aplicación.
        wait_seconds: Espera previa al ajuste (para dar tiempo a que la máquina termine el cierre).
    Returns:
        dict | None: Resultado de PrinterManager.sync_clock, o None si no aplica (no es tfhka).
    """
    try:
        fiscal_config = printers_config.get("fiscal", {})
        fiscal_name = str(fiscal_config.get("fiscal_name", "")).strip().lower()
        if fiscal_name != "tfhka":
            return None
        if wait_seconds > 0:
            time.sleep(wait_seconds)
        return PrinterManager.sync_clock(fiscal_name, fiscal_config)
    except Exception as e:  # noqa: BLE001 - el ajuste de reloj jamás debe romper la respuesta del Z
        logger.warning("No se pudo ajustar el reloj tras el Z: %s", e)
        return {"status": "error", "message": str(e)}


def handle_clock_sync() -> tuple[Response, int]:
    """
    Ajusta manualmente el reloj de la impresora fiscal con la hora del servidor.
    Body opcional: {"force": true} para ajustar aunque el desfase esté dentro del umbral.
    Returns:
        tuple[Response, int]: Resultado de sync_clock; status true si quedó en hora (adjusted/in_sync).
    """
    try:
        body = request.get_json(silent=True) or {}
        force = bool(body.get("force", False)) if isinstance(body, dict) else False

        printers_config = current_app.config.get("printers", {})
        fiscal_config = printers_config.get("fiscal", {})
        if not fiscal_config or not fiscal_config.get("fiscal_enabled", False):
            return error_response("Impresora fiscal no está habilitada", state="Impresora no disponible")

        fiscal_name = str(fiscal_config.get("fiscal_name", "")).strip().lower()
        result = PrinterManager.sync_clock(fiscal_name, fiscal_config, force=force)
        status = result.get("status")

        if status in ("adjusted", "in_sync"):
            message = "Reloj de la impresora ajustado" if status == "adjusted" else "El reloj ya está en hora"
            return jsonify({"status": True, "message": message, "data": result}), 200

        message = result.get("message") or "Esta impresora no soporta el ajuste de reloj"
        http_status = HTTP_INTERNAL_ERROR if status == "error" else HTTP_BAD_REQUEST
        return error_response(message, http_status, data=result, state="Ajuste de reloj rechazado")

    except Exception as e:  # noqa: BLE001 - la ruta siempre responde con el contrato de error
        return error_response(f"Error al ajustar el reloj: {e}", HTTP_INTERNAL_ERROR)


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
            return error_response("Impresora fiscal no está habilitada", state="Impresora no disponible")

        printer, error_data = printer_instance(printers_config)

        if not printer:
            if error_data:
                return error_response(error_data["message"], data=error_data, state="Impresora no disponible")
            return error_response("No se pudo obtener la impresora fiscal", state="Impresora no disponible")

        if not printer.check_status():  # Verificar que la impresora está lista
            return error_response("La impresora fiscal no está lista", state="Impresora no disponible")

        method = f"report_{report_type.lower()}"  # Imprimir reporte
        if not hasattr(printer, method):
            return error_response(f"Esta impresora no soporta reportes {report_type}")

        logger.info("Imprimiendo reporte %s", report_type)
        result = getattr(printer, method)()

        if result:
            response: dict[str, Any] = {"status": True, "message": f"Reporte {report_type} impreso correctamente"}
            if report_type.upper() == "Z":
                clock_sync = _sync_clock_after_z(printers_config)  # el driver ya esperó 3 s tras el Z
                if clock_sync is not None:
                    response["data"] = {"clock_sync": clock_sync}
            return jsonify(response), 200
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
            return error_response("'commands' debe ser una lista no vacía", state="Comando rechazado")

        logger.info("Recibida solicitud de comandos directos: %s", commands)

        printers_config = current_app.config.get("printers", {})
        fiscal_config = printers_config.get("fiscal", {})

        if not fiscal_config or not fiscal_config.get("fiscal_enabled", False):
            return error_response("Impresora fiscal no está habilitada", state="Impresora no disponible")

        printer, error_data = printer_instance(printers_config)
        if not printer:
            message = (
                error_data.get("message", "Error fiscal desconocido")
                if error_data
                else "No se pudo obtener la impresora fiscal"
            )
            return error_response(message, data=error_data, state="Impresora no disponible")

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
                return error_response(message, data=error_data, state="Impresora no disponible")
            if not printer.check_status():
                return error_response("La impresora fiscal no está lista", state="Impresora no disponible")

        results = []
        for cmd in commands:
            success = printer.send_command(cmd)
            results.append({"command": cmd, "success": success})

        # Un Z enviado como comando directo también deja la máquina lista para ajustar su reloj
        clock_sync = None
        if any(r["success"] and Z_COMMAND_PATTERN.match(str(r["command"]).strip()) for r in results):
            clock_sync = _sync_clock_after_z(printers_config, CLOCK_SYNC_DELAY_SECONDS)

        # El estado global refleja el resultado real: Odoo envía un comando por llamada y no debe
        # recibir un éxito si la impresora lo rechazó (el detalle por comando se mantiene en data).
        rejected = [result["command"] for result in results if not result["success"]]
        if rejected:
            return error_response(
                f"Comando(s) rechazado(s) por la impresora: {', '.join(rejected)}",
                data=results if clock_sync is None else {"results": results, "clock_sync": clock_sync},
                state="Comando rechazado",
            )

        response = {"status": True, "message": "Comandos procesados", "data": results}
        if clock_sync is not None:
            # "data" sigue siendo la lista de resultados (contrato de Odoo); el ajuste va aparte
            response["clock_sync"] = clock_sync
        return jsonify(response), 200

    except Exception as e:
        return error_response(f"Error procesando comandos: {str(e)}", HTTP_INTERNAL_ERROR)
