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

from handy.tools import get_base_path

# Constantes
VALID_SERVER_MODES = {"SPOOLER", "PROXY"}
VALID_FISCAL_PRINTERS = {"TFHKA", "PNP"}
VALID_BARCODE_TYPES = {"QR", "BARCODE", "CODE128", "EAN13", "ITF", "CODE39", "PDF417"}

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
                    },
                    "required": ["fiscal_enabled", "fiscal_name", "fiscal_port"],
                },
            },
            "required": ["fiscal"],
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
    },
    "required": ["server", "proxy", "printers", "logging", "security"],
}

logger = logging.getLogger(__name__)


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
