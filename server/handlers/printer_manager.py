#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright © 2024, Iron Graterol
Licensed under the GNU Affero General Public License, version 3 or later.

Clase Singleton para manejar las instancias de impresoras.
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class PrinterManager:
    """
    Clase Singleton para manejar las instancias de impresoras.
    Asegura que solo exista una instancia de cada tipo de impresora.
    """

    _instances: Dict[str, Any] = {}
    _FISCAL_PRINTERS = {"tfhka", "pnp"}  # Tipos de impresoras fiscales

    @classmethod
    def get_printer(cls, printer_type: str, printer_config: Dict[str, Any]) -> Optional[Any]:
        """
        Obtiene una instancia de impresora del tipo especificado.
        Args:
            printer_type: Tipo de impresora.
            printer_config: Configuración de la impresora.
        Returns:
            Optional[Any]: Instancia de impresora o None si no se pudo crear.
        """
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
                    msg_status = f"Impresora NO operativa - Estado: {status['status_description']}, "
                    msg_error = f"Error: {status['error_description']}"
                    logger.error("%s %s", msg_status, msg_error)
                    cls.remove_printer(printer_type)
                    raise ValueError(f"{msg_status} {msg_error}")

            return cls._instances[printer_type]

        except Exception as e:
            if printer_type in cls._instances:
                cls.remove_printer(printer_type)
            raise ValueError(str(e)) from e

    @classmethod
    def remove_printer(cls, printer_type: str) -> None:
        """
        Elimina una instancia de impresora del registro.
        Útil cuando necesitamos recrear una instancia o limpiar recursos.
        Args:
            printer_type: Tipo de impresora a eliminar
        """
        if printer_type in cls._instances:
            if printer_type in cls._FISCAL_PRINTERS:
                try:
                    cls._instances[printer_type].disconnect()
                except Exception as e:
                    logger.warning("Error al desconectar impresora %s : %s", printer_type, str(e))

            del cls._instances[printer_type]
            logger.info("Instancia de impresora %s eliminada", printer_type)
