#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright © 2024, Iron Graterol
Licensed under the GNU Affero General Public License, version 3 or later.

Creado en memoria de mi amado hijo Ian
"""

import glob
import logging
import os
import threading
import webbrowser
from datetime import datetime, timedelta
from logging.config import dictConfig
from logging.handlers import TimedRotatingFileHandler

from handy.runtime_files import ensure_runtime_files
from handy.serial_scan import find_fiscal_port
from handy.tools import get_base_path
from handy.tray_system import TrayManager
from handy.version import __version__
from server.config_loader import ConfigManager
from server.server_api import create_app
from views.main_window import MainWindow


def autodetect_serial_port(config: dict) -> None:
    """
    Escanea y actualiza el puerto serial fiscal si la configuración lo indica.
    """
    server_config = config.get("server", {})
    if not server_config.get("scan_serial_port", False):
        return

    logger = logging.getLogger(__name__)
    logger.info("Iniciando auto-detección de puerto serial fiscal...")

    # Estrategia de selección: se confirma cada candidato (puerto configurado, VID:PID conocidos y otros USB)
    # con una consulta de estado de solo lectura; nunca se persiste un puerto sin confirmar.
    # (Antes: 1. buscar "Prolific" o "USB Serial" en la descripción; 2. si no, tomar el primer puerto disponible.
    # Fallaba en Windows en español y podía elegir un COM de Bluetooth.)
    fiscal_config = config.get("printers", {}).get("fiscal", {})
    current_port = fiscal_config.get("fiscal_port")
    fiscal_name = str(fiscal_config.get("fiscal_name", "")).strip().lower()
    if fiscal_name not in ("tfhka", "pnp"):
        logger.warning("Auto-detección omitida: impresora fiscal '%s' no soportada.", fiscal_name)
        return

    candidate_port = find_fiscal_port(
        fiscal_name,
        current_port,
        int(fiscal_config.get("fiscal_baudrate", 9600)),
        fiscal_config.get("fiscal_timeout", 1.0),
    )

    if not candidate_port:
        logger.warning("No se confirmó un puerto fiscal; se mantiene la configuración actual (%s).", current_port)
        return

    if candidate_port != current_port:
        logger.info(f"Actualizando puerto fiscal: {current_port} -> {candidate_port}")

        # Actualizar estructura de configuración en memoria
        config["printers"]["fiscal"]["fiscal_port"] = candidate_port

        # Guardar cambios a disco
        try:
            ConfigManager.save_config(config)
            logger.info("Configuración actualizada y guardada.")
        except Exception as e:
            logger.error(f"Error guardando configuración detectada: {e}")
    else:
        logger.info(f"El puerto actual ({current_port}) ya es el correcto.")


def main():
    """Función principal que inicializa el servidor API REST."""
    # Primer arranque: crea config.json y los templates de runtime desde sus valores por defecto (sin sobrescribir)
    ensure_runtime_files()
    config = ConfigManager.get_config()  # Cargar configuración

    base_path = get_base_path()
    configure_logging(config.get("logging", {}))  # Configurar logging

    logger = logging.getLogger(__name__)  # Log inicial
    logger.info("=" * 60)
    logger.info("Versión actual: %s-Ian", __version__)

    # Auto-detección de puerto (Pre-Flight Check)
    autodetect_serial_port(config)

    ConfigManager.start_watcher()

    app = create_app(config)  # Crear y configurar flask

    # Ventana principal (Consola/Logs, Servidor, Fiscal, Ticket, Matriz).
    # Vive en el hilo principal: Tkinter/ttkbootstrap requiere su mainloop() ahí.
    window = MainWindow(flask_app=app)

    # Iniciar el system tray (corre en su propio hilo daemon)
    tray = TrayManager(app, base_path, main_window=window)
    tray.run()

    server_host = config.get("server", {}).get("server_host", "0.0.0.0")
    server_port = config.get("server", {}).get("server_port", 5000)
    server_debug = config.get("server", {}).get("server_debug", False)

    logger.info("Iniciando Servidor API REST en http://%s:%s", server_host, server_port)
    logger.info("=" * 60)

    if config.get("server", {}).get("auto_browser", False):  # Iniciar el navegador
        webbrowser.open(f"http://{server_host}:{server_port}")

    def run_flask() -> None:
        app.run(
            host=server_host, port=server_port, debug=server_debug, passthrough_errors=True, use_reloader=False
        )

    # Flask pasa a un hilo daemon: el hilo principal queda libre para el mainloop de la GUI.
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    window.mainloop()  # Bloquea el hilo principal hasta que se solicite salir desde la bandeja


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

        log_pattern = os.path.join(log_dir, "*.log*")
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
            "loggers": {"werkzeug": {"level": "WARNING", "handlers": handlers, "propagate": False}},
        }
    )


if __name__ == "__main__":
    main()
