#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright © 2024, Iron Graterol
Licensed under the GNU Affero General Public License, version 3 or later.

Test run proxy
"""

import json
import os

import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import configure_logging


def load_proxy_config():
    """Carga la configuración para el servidor proxy"""
    # Cargar configuración base
    config_path = os.path.join(os.path.dirname(__file__), "..", "config", "config.json")
    with open(config_path, "r", encoding="utf-8") as f:
        proxy_config = json.load(f)

    # Modificar para modo proxy
    proxy_config["server"]["server_port"] = 5052  # Puerto diferente al SPOOLER
    proxy_config["server"]["server_mode"] = "PROXY"
    proxy_config["proxy"]["proxy_enabled"] = True
    proxy_config["proxy"]["proxy_target"] = "http://localhost:5051/api/printers"  # URL del SPOOLER

    return proxy_config


if __name__ == "__main__":
    # Cargar configuración proxy
    config = load_proxy_config()

    # Configurar logging
    configure_logging(config.get("logging", {}))

    # Crear y ejecutar aplicación
    from server.server_api import create_app

    app = create_app(config)
    app.run(
        host=config["server"]["server_host"],
        port=config["server"]["server_port"],
        debug=config["server"]["server_debug"],
    )
