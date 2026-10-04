#!/usr/bin/env python
"""
Copyright © 2024, Iron Graterol
Licensed under the GNU Affero General Public License, version 3 or later.

Punto de entrada principal del servidor.
"""

import json
import logging
import os
import re
from datetime import datetime

from flask import Blueprint, Flask, current_app, jsonify, render_template, request, send_file
from flask_cors import CORS

from handy.tools import get_base_path

from .handlers.document_handler import handle_documents, handle_fiscal_commands, handle_reports
from .handlers.job_store import init_db
from .handlers.proxy_handler import ProxyHandler

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
    app = Flask(__name__, template_folder=template_folder, static_folder=static_folder, instance_relative_config=True)

    # Configuración de Orígenes Permitidos (CORS)
    server_config = config.get("server", {})
    allowed_origins_list = server_config.get("allowed_origins", [])

    allowed_origins = []
    if allowed_origins_list:
        try:
            allowed_origins = [re.compile(pattern) for pattern in allowed_origins_list]
        except re.error as e:
            logger.error(f"Error compilando regex en allowed_origins: {e}")

    if not allowed_origins:
        allowed_origins = [
            # Localhost con cualquier puerto (IPv4)
            re.compile(r"^http://localhost(:\d+)?$"),
            re.compile(r"^http://127\.0\.0\.1(:\d+)?$"),
            # Localhost con cualquier puerto (IPv6)
            re.compile(r"^http://\[::1\](:\d+)?$"),
            # Rango 192.168.x.x con cualquier puerto
            re.compile(r"^http://192\.168\.\d{1,3}\.\d{1,3}(:\d+)?$"),
            # Rango 10.x.x.x con cualquier puerto
            re.compile(r"^http://10\.\d{1,3}\.\d{1,3}\.\d{1,3}(:\d+)?$"),
            # Subdominios de odoo.com (solo https)
            re.compile(r"^https://.*\.odoo\.com$"),
        ]

    CORS(app, origins=allowed_origins, supports_credentials=True)

    app.config.update(config)
    app.register_blueprint(api, url_prefix="/api")

    init_db()

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

    @app.route("/block")
    def block():
        memorial_path = os.path.join(get_base_path(), "resources", "block.svg")
        return send_file(memorial_path, mimetype="image/svg+xml")

    return app


def get_uptime():
    """Calcula el tiempo que lleva corriendo el servidor"""
    uptime = datetime.now() - server_state.server_start_time
    return int(uptime.total_seconds())


@api.route("/ping", methods=["GET"])
def ping():
    """Ruta para verificar que el servidor está funcionando y retorna el serial fiscal"""
    logger.info("Recibida solicitud de conexión")
    try:
        template_path = os.path.join(get_base_path(), "templates", "template_fiscal_printer.json")
        with open(template_path, encoding="utf-8") as f:
            template_data = json.load(f)
        serial = template_data.get("fiscal", {}).get("serial", "unknown")
        return jsonify({"status": "success", "message": serial})
    except Exception as e:
        logger.error("Error al leer serial fiscal: %s", str(e))
        return jsonify({"status": "success", "message": "unknown"})


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


@api.route("/command", methods=["POST"])
def fiscal_command():
    """Ruta para enviar comandos directos a la impresora fiscal"""
    return handle_fiscal_commands()


