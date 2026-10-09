#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright © 2024, Iron Graterol
Licensed under the GNU Affero General Public License, version 3 or later.

setup cxFreeze
"""

import sys
import os
from cx_Freeze import setup, Executable
from handy.runtime_files import collect_include_files
from handy.version import __version__

# Obtener la ruta base del proyecto
base_path = os.path.abspath(os.path.dirname(__file__))

# Directorios que necesitan ser incluidos
include_dirs = ["config", "docs", "templates", "views", "resources"]

# Construir la lista de archivos a incluir
include_files = [
    ("LICENSE", "LICENSE"),
    ("README.md", "README.md"),
    ("resources/block.svg", "resources/block.svg"),
    ("resources/logo.bmp", "resources/logo.bmp"),
    ("resources/printer_fiscal.ico", "resources/printer_fiscal.ico"),
]

# Se excluyen los archivos de runtime (config.json y templates con contadores): se crean en el primer
# arranque a partir de config/defaults y templates/defaults.
include_files.extend(collect_include_files(base_path, include_dirs))

# Configuración del ejecutable
build_options = {
    "build_exe": os.path.join("build", "ApiPrinterSpooler"),
    "packages": [
        "flask",
        "flask_cors",
        "werkzeug",
        "jinja2",
        "win32print",
        "logging",
        "json",
        "serial",
        "jsonschema",
        "watchdog",
        "http",
        "http.client",
        "urllib",
        "urllib3",
        "decimal",
        "pathlib",
        "typing",
        "unicodedata",
        "datetime",
        "json",
        "os",
        "sys",
        "time",
        "threading",
        "re",
        "PIL",
        "printers",
        "printers.printer_pnp",
        "printers.printer_hka",
        "pystray",
        "tkinter",
        "ttkbootstrap",
        "sqlite3",
        "server",
        "controllers",
        "models",
        "handy",
    ],
    "include_files": include_files,
    "include_msvcr": True,
    "excludes": ["email", "xml", "pydoc", "unittest"],
    "optimize": 2,
}

base = None
if sys.platform == "win32":
    base = "gui"  # Cambiado de "Console" a "gui" para ocultar la consola


executables_exe = [
    Executable(
        "main.py",
        base=base,
        target_name="ApiPS.exe",
        icon="resources/printer_fiscal.ico",
        copyright="Copyright © 2024, Iron Graterol.",
    )
]

setup(
    name="ApiPrinterServer",
    version=__version__,
    description="API y Spooler de Impresión",
    options={"build_exe": build_options},
    executables=executables_exe,
)
