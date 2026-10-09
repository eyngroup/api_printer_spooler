#!/usr/bin/env python
"""
Copyright © 2024, Iron Graterol
Licensed under the GNU Affero General Public License, version 3 or later.

Clase Singleton para manejar las instancias de impresoras.
"""

import logging
import threading
from typing import Any

logger = logging.getLogger(__name__)


class PrinterManager:
    """
    Clase Singleton para manejar las instancias de impresoras.
    Asegura que solo exista una instancia de cada tipo de impresora.
    """

    _instances: dict[str, Any] = {}
    _FISCAL_PRINTERS = {"tfhka", "pnp"}  # Tipos de impresoras fiscales
    # Serializa la creación/eliminación de instancias y el acceso al puerto serial durante la creación
    # (Flask atiende cada solicitud en un hilo distinto). Reentrante: get_printer llama a remove_printer.
    _lock = threading.RLock()

    @classmethod
    def get_printer(cls, printer_type: str, printer_config: dict[str, Any]) -> Any | None:
        """
        Obtiene una instancia de impresora del tipo especificado.
        Args:
            printer_type: Tipo de impresora.
            printer_config: Configuración de la impresora.
        Returns:
            Optional[Any]: Instancia de impresora o None si no se pudo crear.
        """
        with cls._lock:
            try:
                printer_type = printer_type.lower()
                printer_types = {
                    "tfhka": "printers.printer_hka.TfhkaPrinter",
                    "pnp": "printers.printer_pnp.PnpPrinter",
                }

                if printer_type not in printer_types:
                    raise ValueError(f"Tipo de impresora no válido: {(printer_type).upper()}")

                if printer_type in cls._instances:
                    logger.debug("Retornando instancia existente de impresora %s", printer_type.upper())
                    return cls._instances[printer_type]

                logger.info("Creando nueva instancia: Impresora %s", printer_type.upper())

                module_path = printer_types[printer_type].split(".")  # Importar dinámicamente la clase de impresora
                module = __import__(".".join(module_path[:-1]), fromlist=[module_path[-1]])
                printer_class = getattr(module, module_path[-1])

                cls._instances[printer_type] = printer_class(printer_config)  # Crear la instancia

                if printer_type in cls._FISCAL_PRINTERS:  # Para impresoras fiscales, verificar el estado
                    status = cls._instances[printer_type].get_printer_status()

                    is_error = False
                    if printer_type == "tfhka":
                        is_error = status["error_code"] != 64 or status["status_code"] != 96
                    elif printer_type == "pnp":
                        is_error = status["status_code"] != "0080" or status["error_code"] != "0600"

                    if is_error:
                        status_msg, error_msg = cls._instances[printer_type].format_status_message(status)
                        msg_status = f"Impresora NO operativa - Estado: {status_msg}, "
                        msg_error = f"Error: {error_msg}"
                        logger.error("%s %s", msg_status, msg_error)
                        cls.remove_printer(printer_type)
                        raise ValueError(f"{msg_status} {msg_error}")

                return cls._instances[printer_type]

            except Exception as e:
                if printer_type in cls._instances:
                    cls.remove_printer(printer_type)
                message = str(e)
                if "Estado:" not in message and printer_type in cls._FISCAL_PRINTERS:
                    # La creación falló sin informar el estado (p. ej. tapa abierta): se intenta leerlo
                    # para que Odoo reciba el motivo real y no solo un error genérico de conexión.
                    status = cls.read_status(printer_type, printer_config)
                    if status:
                        message = f"{message} - Estado: {status['status']}, Error: {status['error']}"
                raise ValueError(message) from e

    @classmethod
    def remove_printer(cls, printer_type: str) -> None:
        """
        Elimina una instancia de impresora del registro.
        Útil cuando necesitamos recrear una instancia o limpiar recursos.
        Args:
            printer_type: Tipo de impresora a eliminar
        """
        with cls._lock:
            if printer_type in cls._instances:
                if printer_type in cls._FISCAL_PRINTERS:
                    try:
                        cls._instances[printer_type].disconnect()
                    except Exception as e:
                        logger.warning("Error al desconectar impresora %s : %s", printer_type, str(e))

                del cls._instances[printer_type]
                logger.info("Instancia de impresora %s eliminada", printer_type)

    @classmethod
    def read_status(cls, printer_type: str, printer_config: dict[str, Any]) -> dict[str, Any] | None:
        """
        Lee el estado de una impresora fiscal con un controlador temporal, sin crear una instancia.
        Se usa cuando la creación de la instancia falló, para informar el motivo real (tapa abierta,
        sin papel, cable desconectado). No lee nada si ya existe una instancia (evita acceso concurrente
        al puerto serial). Nunca lanza excepciones.
        Args:
            printer_type: Tipo de impresora fiscal ("tfhka" o "pnp").
            printer_config: Configuración de la impresora (fiscal_port, fiscal_baudrate, fiscal_timeout).
        Returns:
            dict | None: Diccionario con status_code, error_code, status y error (textos legibles),
            o None si no se pudo leer el estado.
        """
        controller = None
        try:
            printer_type = printer_type.lower()
            if printer_type not in cls._FISCAL_PRINTERS:
                return None

            with cls._lock:
                if printer_type in cls._instances:
                    return None

                port = printer_config.get("fiscal_port")
                baudrate = printer_config.get("fiscal_baudrate", 9600)
                timeout = printer_config.get("fiscal_timeout", 2)

                if printer_type == "tfhka":
                    from controllers.pfhka import FiscalPrinterHka

                    controller = FiscalPrinterHka(port, baudrate, timeout)
                else:
                    from controllers.pfpnp import FiscalPrinterPnp

                    controller = FiscalPrinterPnp(port, baudrate, timeout)

                if not controller.open_port():
                    logger.warning("No se pudo abrir el puerto %s para leer el estado de %s", port, printer_type)
                    return None

                raw = controller.get_status()
                if not raw:
                    return None

                if printer_type == "tfhka":
                    return {
                        "status_code": raw.get("status_code"),
                        "error_code": raw.get("error_code"),
                        "status": raw.get("status", "unknown"),
                        "error": raw.get("error", "none"),
                    }
                return {
                    "status_code": raw.get("status_code"),
                    "error_code": raw.get("error_code"),
                    "status": raw.get("status", "unknown"),
                    "error": raw.get("status_detallado", "none"),
                }
        except Exception as e:  # noqa: BLE001 - nunca debe lanzar: cualquier fallo devuelve None
            logger.warning("No se pudo leer el estado de la impresora %s: %s", printer_type, e)
            return None
        finally:
            if controller is not None:
                try:
                    controller.close_port()
                except Exception as e:  # noqa: BLE001 - fallo al cerrar el puerto no debe propagarse
                    logger.warning("Error al cerrar el puerto tras leer el estado: %s", e)

    @classmethod
    def read_serial(cls, printer_type: str, printer_config: dict[str, Any]) -> str | None:
        """
        Obtiene el serial (registro de máquina) de la impresora fiscal sin crear una instancia.

        Prioridad: 1) serial de la instancia conectada (no toca el puerto, seguro durante una impresión);
        2) lectura única de solo lectura con un controlador temporal (HKA: S5, PNP: versión). Nunca envía
        CANCEL ni crea la instancia: crear la instancia de HKA cancela un documento abierto y consume un
        número fiscal, algo que un simple ping no debe provocar. Nunca lanza excepciones.
        Args:
            printer_type: Tipo de impresora fiscal ("tfhka" o "pnp").
            printer_config: Configuración de la impresora (fiscal_port, fiscal_baudrate, fiscal_timeout).
        Returns:
            str | None: Serial de la máquina, o None si no se pudo obtener.
        """
        controller = None
        try:
            printer_type = printer_type.lower()
            if printer_type not in cls._FISCAL_PRINTERS:
                return None

            with cls._lock:
                instance = cls._instances.get(printer_type)
                if instance is not None:
                    return getattr(instance, "_serial", None) or None

                port = printer_config.get("fiscal_port")
                baudrate = printer_config.get("fiscal_baudrate", 9600)
                timeout = printer_config.get("fiscal_timeout", 2)

                if printer_type == "tfhka":
                    from controllers.pfhka import FiscalPrinterHka

                    controller = FiscalPrinterHka(port, baudrate, timeout)
                else:
                    from controllers.pfpnp import FiscalPrinterPnp

                    controller = FiscalPrinterPnp(port, baudrate, timeout)

                if not controller.open_port():
                    logger.warning("No se pudo abrir el puerto %s para leer el serial de %s", port, printer_type)
                    return None

                info = controller.get_s5() if printer_type == "tfhka" else controller.get_version()
                serial = (info or {}).get("serial", "").strip()
                return serial or None
        except Exception as e:  # noqa: BLE001 - nunca debe lanzar: cualquier fallo devuelve None
            logger.warning("No se pudo leer el serial de la impresora %s: %s", printer_type, e)
            return None
        finally:
            if controller is not None:
                try:
                    controller.close_port()
                except Exception as e:  # noqa: BLE001 - fallo al cerrar el puerto no debe propagarse
                    logger.warning("Error al cerrar el puerto tras leer el serial: %s", e)
