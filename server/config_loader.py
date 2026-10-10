#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright © 2024, Iron Graterol
Licensed under the GNU Affero General Public License, version 3 or later.

Carga y valida  el archivo de configuración del sistema.
"""

import json
import logging
import os
from pathlib import Path
from typing import Dict, Any

from jsonschema import validate
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from handy.runtime_files import default_path_for, ensure_runtime_files
from handy.tools import get_base_path

# Constantes
VALID_SERVER_MODES = {"SPOOLER", "PROXY"}
VALID_FISCAL_PRINTERS = {"TFHKA", "PNP"}
VALID_MATRIX_PAPER_TYPES = {"CARTA", "MEDIA_CARTA"}
VALID_BARCODE_TYPES = {"QR", "BARCODE", "CODE128", "EAN13", "ITF", "CODE39", "PDF417"}

# Etiquetas de respaldo de los medios de pago 01..24 (HKA80). La fuente de verdad es config/defaults/config.json;
# esta constante solo se usa si ese archivo no se puede leer.
FALLBACK_PAYMENT_LABELS = {
    "01": "Efectivo",
    "02": "EfectivoBs",
    "03": "EfectivoOtros",
    "04": "Contado",
    "05": "Credito",
    "06": "OtrasCxC",
    "07": "PuntoDeVenta",
    "08": "Transferencia",
    "09": "TarjetaDebito",
    "10": "TarjetaCredito",
    "11": "PagoMovil",
    "12": "BioPago",
    "13": "CestaTicket",
    "14": "Cashea",
    "15": "CasheaCxC",
    "16": "CasheaPunto",
    "17": "CasheaPagoMovil",
    "18": "CasheaBs",
    "19": "Dif.IG..",
    "20": "Divisa",
    "21": "DivisaUSD",
    "22": "DivisaEUR",
    "23": "DivisaOtros",
    "24": "DivisaCashea",
}
PAYMENT_CODES = tuple(f"{n:02d}" for n in range(1, 25))

CONFIG_SCHEMA = {
    "type": "object",
    "properties": {
        "server": {
            "type": "object",
            "properties": {
                "auto_browser": {"type": "boolean"},
                "server_debug": {"type": "boolean"},
                "scan_serial_port": {"type": "boolean"},
                "server_host": {"type": "string"},
                "server_mode": {"type": "string", "enum": list(VALID_SERVER_MODES)},
                "server_port": {"type": "integer", "minimum": 1, "maximum": 65535},
            },
            "required": ["server_mode", "server_host", "server_port", "server_debug"],
        },
        "proxy": {
            "type": "object",
            "properties": {
                "proxy_enabled": {"type": "boolean"},
                "proxy_target": {"type": "string", "format": "uri"},
            },
            "required": ["proxy_enabled", "proxy_target"],
        },
        "printers": {
            "type": "object",
            "properties": {
                "fiscal": {
                    "type": "object",
                    "properties": {
                        "fiscal_enabled": {"type": "boolean"},
                        "fiscal_name": {"type": "string", "enum": list(VALID_FISCAL_PRINTERS)},
                        "fiscal_port": {"type": "string"},
                        "fiscal_baudrate": {"type": "integer"},
                        "fiscal_timeout": {"type": "integer"},
                        "fiscal_barcode_type": {"type": "string", "enum": list(VALID_BARCODE_TYPES)},
                        # Opcional: nombre de cada medio de pago 01..24 (cadena vacía = sin etiqueta)
                        "payment_labels": {
                            "type": "object",
                            "patternProperties": {r"^(0[1-9]|1[0-9]|2[0-4])$": {"type": "string"}},
                            "additionalProperties": False,
                        },
                    },
                    "required": ["fiscal_enabled", "fiscal_name", "fiscal_port"],
                },
                "matrix": {
                    "type": "object",
                    "properties": {
                        "matrix_enabled": {"type": "boolean"},
                        "matrix_name": {"type": "string"},
                        "matrix_port": {"type": "string"},
                        "matrix_paper": {"type": "string", "enum": list(VALID_MATRIX_PAPER_TYPES)},
                        "matrix_template": {"type": "string"},
                        "matrix_file": {"type": "string"},
                        "matrix_direct": {"type": "boolean"},
                        "matrix_use_escp": {"type": "boolean"},
                    },
                    "required": ["matrix_enabled", "matrix_name", "matrix_port", "matrix_template"],
                },
                "ticket": {
                    "type": "object",
                    "properties": {
                        "ticket_enabled": {"type": "boolean"},
                        "ticket_name": {"type": "string"},
                        "ticket_port": {"type": "string"},
                        "ticket_paper": {"type": "string"},
                        "ticket_template": {"type": "string"},
                        "ticket_file": {"type": "string"},
                        "ticket_direct": {"type": "boolean"},
                        "ticket_use_escpos": {"type": "boolean"},
                        "logo_enabled": {"type": "boolean"},
                        "logo_width": {"type": "integer"},
                        "logo_height": {"type": "integer"},
                        "barcode_enabled": {"type": "boolean"},
                        "barcode_type": {"type": "string", "enum": list(VALID_BARCODE_TYPES)},
                    },
                    "required": ["ticket_enabled", "ticket_name", "ticket_port", "ticket_template"],
                },
            },
            "required": ["fiscal", "matrix", "ticket"],
        },
        "logging": {
            "type": "object",
            "properties": {
                "log_output": {"type": "boolean"},
                "log_file": {"type": "string"},
                "log_level": {
                    "type": "string",
                    "enum": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                },
                "log_format": {"type": "string"},
                "log_days": {"type": "integer", "minimum": 1},
            },
            "required": ["log_output", "log_file", "log_level", "log_format", "log_days"],
        },
        "security": {
            "type": "object",
            "properties": {"security_code": {"type": "string"}},
            "required": ["security_code"],
        },
        # Opcional: envío periódico de lecturas del monitor fiscal a Odoo (push). Ausente = deshabilitado.
        "monitor_push": {
            "type": "object",
            "properties": {
                "enabled": {"type": "boolean"},
                "url": {"type": "string"},
                "token": {"type": "string"},
                "interval_minutes": {"type": "integer", "minimum": 1},
                "branch_code": {"type": "string"},
            },
        },
    },
    "required": ["server", "proxy", "printers", "logging", "security"],
}

logger = logging.getLogger(__name__)


def _load_default_payment_labels() -> dict[str, str]:
    """
    Lee las etiquetas por defecto de los medios de pago desde config/defaults/config.json.
    Returns:
        dict[str, str]: Etiquetas por código; las de respaldo si el archivo no se puede leer o no es válido
    """
    try:
        path = os.path.join(get_base_path(), *default_path_for("config/config.json").split("/"))
        with open(path, encoding="utf-8") as f:
            labels = json.load(f)["printers"]["fiscal"]["payment_labels"]
        return {str(k): str(v) for k, v in labels.items() if k in PAYMENT_CODES}
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as e:
        logger.warning("No se pudieron leer las etiquetas de pago por defecto, se usan las de respaldo: %s", e)
        return dict(FALLBACK_PAYMENT_LABELS)


def get_payment_labels(config: dict[str, Any] | None) -> dict[str, str]:
    """
    Etiquetas de los medios de pago 01..24: los valores por defecto combinados con los de la instalación.
    La configuración de runtime tiene prioridad por código; una cadena vacía significa "sin etiqueta".
    Nunca lanza excepciones.
    Args:
        config: Configuración completa (o None); se lee `printers.fiscal.payment_labels`
    Returns:
        dict[str, str]: Etiqueta por código ("01".."24")
    """
    try:
        labels = _load_default_payment_labels()
        overrides = ((config or {}).get("printers", {}).get("fiscal", {}) or {}).get("payment_labels") or {}
        if isinstance(overrides, dict):
            for code, label in overrides.items():
                if code in PAYMENT_CODES and isinstance(label, str):
                    labels[code] = label
        return labels
    except Exception as e:  # noqa: BLE001 - las etiquetas son informativas: nunca deben romper al llamador
        logger.warning("Error combinando las etiquetas de pago: %s", e)
        return dict(FALLBACK_PAYMENT_LABELS)


MONITOR_PUSH_MIN_INTERVAL = 15
MONITOR_PUSH_DEFAULTS = {
    "enabled": False,
    "url": "",
    "token": "",
    "interval_minutes": 60,
    "branch_code": "",
}


def get_monitor_push_config(config: dict[str, Any] | None) -> dict[str, Any]:
    """
    Ajustes del envío del monitor a Odoo: la sección `monitor_push` combinada con los valores por defecto.
    Una instalación sin la sección queda deshabilitada. El intervalo nunca baja de 15 minutos (y un valor
    no numérico vuelve a 60). Nunca lanza excepciones.
    Args:
        config: Configuración completa (o None)
    Returns:
        dict[str, Any]: enabled, url, token, interval_minutes, branch_code ya normalizados
    """
    merged = dict(MONITOR_PUSH_DEFAULTS)
    section = (config or {}).get("monitor_push") if isinstance(config, dict) else None
    if isinstance(section, dict):
        for key in merged:
            if key in section and section[key] is not None:
                merged[key] = section[key]
    merged["enabled"] = merged["enabled"] is True
    for key in ("url", "token", "branch_code"):
        merged[key] = str(merged[key]).strip()
    try:
        interval = int(merged["interval_minutes"])
    except (TypeError, ValueError):
        interval = MONITOR_PUSH_DEFAULTS["interval_minutes"]
    merged["interval_minutes"] = max(MONITOR_PUSH_MIN_INTERVAL, interval)
    return merged


def get_security_code() -> str:
    """Obtiene el security code: env var > config.json > fallback."""
    if code := os.environ.get("PRINTER_SECURITY_CODE"):
        return code
    config_code = ConfigManager.get_config().get("security", {}).get("security_code", "")
    return config_code if config_code else "0205"


class ConfigReloader(FileSystemEventHandler):  # pylint: disable=R0903
    """Maneja la recarga automática del archivo de configuración"""

    def __init__(self, callback: callable):
        self.callback = callback

    def on_modified(self, event):
        """Maneja el evento de modificación del archivo"""
        if event.src_path.endswith("config.json"):
            logger.info("Detectado cambio en config.json. Recargando...")
            self.callback()


class ConfigManager:
    """Gestor centralizado de configuración con validación de esquema"""

    _instance = None
    _config = None
    _config_path = Path(os.path.join(get_base_path(), "config", "config.json"))
    _observer = Observer()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get_config(cls) -> Dict[str, Any]:
        """Obtiene la configuración cargada (singleton)"""
        if cls._config is None:
            cls.reload_config()
        return cls._config

    @classmethod
    def reload_config(cls) -> None:
        """Recarga la configuración desde disco con validación"""
        try:
            # Defensivo: si falta config.json (primer arranque) se crea desde config/defaults
            ensure_runtime_files()
            with open(cls._config_path, "r", encoding="utf-8") as f:
                new_config = json.load(f)

            validate(new_config, CONFIG_SCHEMA)
            cls._config = new_config
            logger.info("Configuración recargada exitosamente")

        except Exception as e:
            logger.error("Error recargando configuración: %s", str(e))
            if cls._config is None:
                raise RuntimeError("No hay configuración válida cargada") from e

    @classmethod
    def start_watcher(cls) -> None:
        """Inicia el observador de cambios en el archivo"""
        event_handler = ConfigReloader(cls.reload_config)
        cls._observer.schedule(event_handler, path=str(cls._config_path.parent), recursive=False)
        cls._observer.start()
        logger.info("Observador de configuración iniciado")

    @classmethod
    def stop_watcher(cls) -> None:
        """Detiene el observador de cambios"""
        cls._observer.stop()
        cls._observer.join()
        logger.info("Observador de configuración detenido")

    @staticmethod
    def save_config(new_config):
        """Guarda la nueva configuración en el archivo"""
        with open(ConfigManager._config_path, "w", encoding="utf-8") as f:
            json.dump(new_config, f, indent=4, ensure_ascii=False)
