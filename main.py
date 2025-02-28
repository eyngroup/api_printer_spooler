#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
API Printer Server
Copyright © 2024, Iron Graterol.
Creado en memoria de mi amado hijo Ian
"""

import glob
import logging
import os
import webbrowser
from datetime import datetime, timedelta
from logging.config import dictConfig
from logging.handlers import TimedRotatingFileHandler
from utils.version import __version__

from utils.tools import get_base_path
from server.config_loader import ConfigManager
from server.server_api import create_app

print(f"Versión actual: {__version__}")


def main():
    """Función principal que inicializa el servidor API REST."""
    config = ConfigManager.get_config()  # Cargar configuración
    ConfigManager.start_watcher()

    configure_logging(config.get("logging", {}))  # Configurar logging

    logger = logging.getLogger(__name__)  # Log inicial
    logger.info("=" * 120)
    logger.info("Iniciando Servidor API REST")

    app = create_app(config)  # Crear y configurar flask

    server_host = config.get("server", {}).get("server_host", "0.0.0.0")
    server_port = config.get("server", {}).get("server_port", 5000)
    server_debug = config.get("server", {}).get("server_debug", False)

    if config.get("server", {}).get("auto_browser", False):  # Iniciar el navegador
        webbrowser.open(f"http://{server_host}:{server_port}")

    app.run(
        host=server_host,
        port=server_port,
        debug=server_debug,
    )  # Iniciar el servidor


def cleanup_old_logs(log_dir: str, max_days: int) -> None:
    """
    Elimina los archivos de log más antiguos que max_days.
    Args:
        log_dir: Directorio donde se encuentran los logs
        max_days: Número máximo de días a mantener
    """
    try:
        current_date = datetime.now()
        cutoff_date = current_date - timedelta(days=max_days)

        log_pattern = os.path.join(log_dir, "printer_service_*.log*")
        for log_file in glob.glob(log_pattern):
            try:
                file_date_str = os.path.basename(log_file).split("_")[2][:8]  # Obtiene YYYYMMDD
                file_date = datetime.strptime(file_date_str, "%Y%m%d")

                if file_date < cutoff_date:  # Si el archivo es más antiguo que cutoff_date, eliminarlo
                    os.remove(log_file)
                    # print(f"Archivo de log antiguo eliminado: {log_file}")
            except (ValueError, IndexError):
                continue
    except Exception as e:
        print(f"Error al limpiar logs antiguos: {e}")


class CustomTimedRotatingFileHandler(TimedRotatingFileHandler):
    """Handler personalizado para rotación de logs con limpieza automática."""

    def __init__(
        self,
        filename,
        when="D",
        interval=1,
        backupCount=0,
        encoding=None,
        delay=False,
        utc=False,
        atTime=None,
    ):
        super().__init__(filename, when, interval, backupCount, encoding, delay, utc, atTime)
        self.max_days = backupCount
        self.log_dir = os.path.dirname(filename)

    def doRollover(self):
        """Sobrescribe el método de rotación para incluir limpieza de logs antiguos."""
        super().doRollover()
        cleanup_old_logs(self.log_dir, self.max_days)


def configure_logging(log_config: dict) -> None:
    """
    Configura el sistema de logging con rotación de archivos y limpieza automática.
    Args:
        log_config: Diccionario con la configuración de logging
    """
    base_path = get_base_path()
    log_dir = os.path.join(base_path, "logs")
    os.makedirs(log_dir, exist_ok=True)

    log_days = log_config.get("log_days", 7)
    log_file = log_config.get("log_file", "printer_service")
    log_format = log_config.get("log_format", "%(asctime)s | %(levelname)s | %(message)s")
    log_level = getattr(logging, log_config.get("log_level", "INFO").upper(), logging.INFO)

    current_date = datetime.now().strftime("%Y%m%d")
    log_filename = f"{log_file}-{current_date}.log"

    cleanup_old_logs(log_dir, log_days)

    class ColorFormatter(logging.Formatter):
        """Formatter con colores según el nivel del log"""

        COLORS = {
            "DEBUG": "\033[34m",  # Azul
            "INFO": "\033[32m",  # Verde
            "WARNING": "\033[33m",  # Amarillo
            "ERROR": "\033[31m",  # Rojo
            "CRITICAL": "\033[41m",  # Fondo rojo
        }
        RESET = "\033[0m"

        def format(self, record):
            if record.levelname in self.COLORS:
                record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.RESET}"

            record.threadName = getattr(record, "threadName", "-")
            record.filename = getattr(record, "filename", "-")
            record.funcName = getattr(record, "funcName", "-")

            return super().format(record)

    handlers = ["file"]
    if log_config.get("log_output", True):  # Validar si se muestran logs en consola
        handlers.append("console")

    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "detailed": {
                    "()": ColorFormatter,
                    "format": log_format,
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                }
            },
            "handlers": {
                "file": {
                    "()": CustomTimedRotatingFileHandler,
                    "filename": os.path.join(log_dir, log_filename),
                    "when": "midnight",
                    "interval": 1,
                    "backupCount": log_days,
                    "formatter": "detailed",
                    "encoding": "utf-8",
                },
                "console": {
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                    "formatter": "detailed",
                },
            },
            "root": {"level": log_level, "handlers": handlers},
            "loggers": {"werkzeug": {"level": "INFO", "handlers": handlers, "propagate": False}},
        }
    )


if __name__ == "__main__":
    main()
