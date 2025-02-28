#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" setup cxFreeze"""

import sys
import os
from cx_Freeze import setup, Executable

# Obtener la ruta base del proyecto
base_path = os.path.abspath(os.path.dirname(__file__))

# Directorios que necesitan ser incluidos
include_dirs = ["config", "docs", "library", "templates", "views"]

# Construir la lista de archivos a incluir
include_files = [
    ("LICENSE", "LICENSE"),
    ("README.md", "README.md"),
    ("resources/block.svg", "resources/block.svg"),
    ("resources/logo.bmp", "resources/logo.bmp"),
]

for dir_name in include_dirs:
    dir_path = os.path.join(base_path, dir_name)
    if os.path.exists(dir_path):
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                source = os.path.join(root, file)
                dest = os.path.relpath(source, base_path)
                include_files.append((source, dest))

# Configuración del ejecutable
build_options = {
    "packages": [
        "flask",
        "flask_cors",
        "werkzeug",
        "jinja2",
        "win32print",
        "clr",
        "logging",
        "json",
        "serial",
        "pythonnet",
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
        "ctypes",
        "PIL",
        "printers",
        "printers.printer_pnp",
        "printers.printer_hka",
    ],
    "include_files": include_files,
    "include_msvcr": True,
    "excludes": ["tkinter", "unittest", "email", "xml", "pydoc"],
    "optimize": 2,
}

base = None
if sys.platform == "win32":
    base = "Console"  # Cambiado de "Win32GUI" a "Console" para mostrar la consola


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
    version="1.1.0",
    description="API y Spooler de Impresión",
    options={"build_exe": build_options},
    executables=executables_exe,
)
