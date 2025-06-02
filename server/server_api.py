#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright © 2024, Iron Graterol
Licensed under the GNU Affero General Public License, version 3 or later.

Punto de entrada principal del servidor.
"""

import logging
from datetime import datetime
import time
import threading
import os

from flask import Flask, request, jsonify, Blueprint, current_app, render_template, make_response, send_file
from flask_cors import CORS

from utils.tools import get_base_path
from server.config_loader import ConfigManager
from .handlers.document_handler import handle_documents, handle_reports
from .handlers.proxy_handler import ProxyHandler
from .auth import require_auth, create_session, cleanup_sessions

logger = logging.getLogger(__name__)

# Blueprint para agrupar las rutas
api = Blueprint("api", __name__)


class ServerState:  # pylint: disable=R0903
    """Clase para el estado del servidor."""

    def __init__(self):
        self.request_count = 0
        self.error_count = 0
        self.last_errors = []
        self.proxy_handler = None
        self.server_start_time = datetime.now()
        self.error_log = []


# Crear una instancia global del estado del servidor
server_state = ServerState()


@api.before_request
def before_request():
    """before request"""
    if request.endpoint != "api.get_status":  # No contar las peticiones de status
        server_state.request_count += 1


@api.errorhandler(Exception)
def handle_error(error):
    """handle error"""
    server_state.error_count += 1
    error_info = {
        "timestamp": datetime.now().isoformat(),
        "message": str(error),
        "endpoint": request.endpoint,
    }
    server_state.last_errors.append(error_info)
    if len(server_state.last_errors) > 10:  # Mantener solo los últimos 10 errores
        server_state.last_errors.pop(0)
    return jsonify({"status": "error", "message": str(error)}), 500


def create_app(config):
    """Crea y configura la aplicación Flask"""
    template_folder = os.path.join(get_base_path(), "views")
    static_folder = os.path.join(get_base_path(), "views", "static")
    app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)

    CORS(app)
    app.config.update(config)
    app.register_blueprint(api, url_prefix="/api")

    if config.get("server", {}).get("server_mode") == "PROXY":
        server_state.proxy_handler = ProxyHandler(config)
        logger.info(
            "Modo PROXY configurado. Target URL: %s",
            config.get("proxy", {}).get("proxy_target"),
        )
    else:
        logger.info("Modo SPOOLER configurado")

    @app.route("/")
    def index():
        """Ruta principal que muestra el estado del servidor"""
        uptime = datetime.now() - server_state.server_start_time
        hours = int(uptime.total_seconds() // 3600)
        minutes = int((uptime.total_seconds() % 3600) // 60)

        return render_template(
            "status.html",
            server_status="running",
            uptime=f"{hours}h {minutes}m",
            version="1.0.0",
            server_mode=app.config.get("server", {}).get("server_mode"),
            printers=app.config.get("printers", {}),
            errors=server_state.error_log[-10:],  # Últimos 10 errores
        )

    @app.route("/config-editor.html")
    @require_auth
    def config_editor():
        """Ruta para el editor de configuración"""
        return render_template("config-editor.html")

    @app.route("/block")
    def block():
        memorial_path = os.path.join(get_base_path(), "resources", "block.svg")
        return send_file(memorial_path, mimetype="image/svg+xml")

    # Limpiar sesiones expiradas cada minuto
    def cleanup_task():
        while True:
            time.sleep(60)
            cleanup_sessions()

    cleanup_thread = threading.Thread(target=cleanup_task, daemon=True)
    cleanup_thread.start()

    return app


def get_uptime():
    """Calcula el tiempo que lleva corriendo el servidor"""
    uptime = datetime.now() - server_state.server_start_time
    return int(uptime.total_seconds())


@api.route("/ping", methods=["GET"])
def ping():
    """Ruta para verificar que el servidor está funcionando"""
    logger.info("Recibida solicitud PING")
    return jsonify({"status": "success", "message": "pong"})


@api.route("/status", methods=["GET"])
def get_status():
    """Obtiene el estado actual del servidor y las impresoras"""
    try:
        logger.info("Recibida solicitud de estado")

        config = current_app.config  # Obtener la configuración completa
        if not config:
            raise ValueError("No se pudo obtener la configuración del servidor")

        response = {
            "status": "running",
            "uptime": get_uptime(),
            "config": {
                "server": config.get("server", {}),
                "proxy": config.get("proxy", {}),
                "printers": config.get("printers", {}),
                "logging": config.get(
                    "logging",
                    {
                        "level": "INFO",
                        "filename": "server.log",
                        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                        "console_output": True,
                    },
                ),
                "security": config.get("security", {"z_report_code": ""}),
            },
            "stats": {
                "requests_total": server_state.request_count,
                "error_count": server_state.error_count,
                "last_errors": server_state.last_errors,
            },
        }

        return jsonify(response)

    except Exception as e:
        logger.error("Error al obtener el estado: %s", str(e))
        return (
            jsonify(
                {
                    "status": "error",
                    "message": f"Error al obtener el estado: {str(e)}",
                    "config": {},
                }
            ),
            500,
        )


@api.route("/printers", methods=["POST"])
def print_document():
    """Ruta principal para imprimir documentos"""
    return handle_documents(server_state.proxy_handler)


@api.route("/report_x", methods=["GET"])
def print_report_x():
    """Ruta para imprimir reporte X (solo impresoras fiscales)"""
    return handle_reports("X")


@api.route("/report_z", methods=["GET"])
def print_report_z():
    """Ruta para imprimir reporte Z (solo impresoras fiscales)"""
    return handle_reports("Z")


@api.route("/config", methods=["POST"])
def save_config():
    """Guarda la configuración en el archivo config.json usando ConfigManager"""
    try:
        logger.info("Recibida solicitud para guardar configuración")

        new_config = request.get_json()
        if not new_config:
            raise ValueError("No se recibió configuración para guardar")

        required_sections = ["server", "proxy", "printers", "logging", "security"]
        for section in required_sections:  # Validar la estructura básica de la configuración
            if section not in new_config:
                raise ValueError(f"Falta la sección {section} en la configuración")

        ConfigManager.save_config(new_config)  # Guardar la configuración
        ConfigManager.reload_config()  # Recargar la configuración
        current_app.config.update(new_config)  # Actualizar la configuración

        if new_config.get("server", {}).get("server_mode") == "PROXY":
            server_state.proxy_handler = ProxyHandler(new_config)
            logger.info(
                "Modo PROXY reconfigurado. Target URL: %s",
                new_config.get("proxy", {}).get("proxy_target"),
            )

        return jsonify({"status": "success", "message": "Configuración guardada correctamente"})

    except Exception as e:
        logger.error("Error al guardar la configuración: %s", str(e))
        return (
            jsonify(
                {
                    "status": "error",
                    "message": f"Error al guardar la configuración: {str(e)}",
                }
            ),
            500,
        )


@api.route("/auth/validate", methods=["POST"])
def validate_security_code():
    """Valida el código de seguridad y crea una sesión"""
    try:
        data = request.get_json()
        if not data or "security_code" not in data:
            return jsonify({"status": "error", "message": "Código no proporcionado"}), 400

        config = current_app.config
        if not config or "security" not in config:
            return jsonify({"status": "error", "message": "Error de configuración"}), 500

        if data["security_code"] == config["security"]["security_code"]:
            token = create_session()
            response = make_response(jsonify({"status": "success", "message": "Código válido"}))
            response.set_cookie("auth_token", token, httponly=True, samesite="Strict", max_age=1800)
            return response
        return jsonify({"status": "error", "message": "Código de seguridad incorrecto"}), 401

    except Exception as e:
        logger.error("Error en validación de código: %s", str(e))
        return jsonify({"status": "error", "message": f"Error en validación: {str(e)}"}), 500
