#!/usr/bin/env python
"""
Copyright © 2024, Iron Graterol
Licensed under the GNU Affero General Public License, version 3 or later.

Archivos de runtime (configuración y templates con contadores): se versionan solo sus valores por defecto
(`config/defaults/` y `templates/defaults/`) y la copia de trabajo se crea en el primer arranque. Este módulo
no depende de cx_Freeze ni de Flask para poder usarse desde `setup.py` y desde los tests.
"""

import json
import logging
import os
import shutil
from pathlib import Path

from handy.tools import get_base_path

logger = logging.getLogger(__name__)

# Archivos mutables en runtime (ruta relativa a la base). Cada uno tiene su valor por defecto en <dir>/defaults/.
RUNTIME_FILES = (
    "config/config.json",
    "templates/template_fiscal_printer.json",
    "templates/template_matriz_carta.json",
    "templates/template_ticket_simple.json",
)

# Carpetas de datos del cliente: nunca van en un release ni son tocadas por una actualización
RUNTIME_DIRS = ("data", "logs", "backups", "updates")


def is_runtime_path(relative: "str | Path") -> bool:
    """
    Indica si una ruta relativa a la instalación es un dato del cliente (no pertenece al programa).
    Args:
        relative: Ruta relativa a la carpeta de instalación (con "/" o "\\")
    Returns:
        bool: True si es un archivo de runtime o está dentro de data/, logs/, backups/ o updates/ (sin distinguir
        mayúsculas)
    """
    text = relative.as_posix() if isinstance(relative, Path) else str(relative)
    parts = text.strip("/").lower().split("/")
    if parts[0] in RUNTIME_DIRS:
        return True
    return "/".join(parts) in {path.lower() for path in RUNTIME_FILES}


def read_configured_fiscal_serial() -> str:
    """
    Lee el serial configurado en la pestaña Fiscal (template_fiscal_printer.json).
    En HKA el driver lo actualiza al conectar; en PNP lo configura el técnico a mano.
    Returns:
        str: Serial configurado o "unknown" si no se pudo leer.
    """
    try:
        template_path = os.path.join(get_base_path(), "templates", "template_fiscal_printer.json")
        with open(template_path, encoding="utf-8") as f:
            template_data = json.load(f)
        return template_data.get("fiscal", {}).get("serial", "unknown")
    except Exception as e:  # noqa: BLE001 - cualquier fallo de lectura se informa como serial desconocido
        logger.error("Error al leer serial fiscal: %s", str(e))
        return "unknown"


def default_path_for(relative_path: str) -> str:
    """Devuelve la ruta relativa del valor por defecto de un archivo de runtime (`dir/defaults/nombre`)."""
    directory, name = os.path.split(relative_path)
    return f"{directory}/defaults/{name}"


def ensure_runtime_files(base_path: str | None = None) -> list[str]:
    """
    Crea los archivos de runtime que no existan copiándolos desde sus valores por defecto.

    Nunca sobrescribe un archivo existente: las instalaciones actuales conservan su configuración y contadores.
    Args:
        base_path: Directorio base; por defecto `get_base_path()` (carpeta del exe si está congelado).
    Returns:
        Lista de rutas relativas de los archivos creados.
    """
    base = base_path if base_path is not None else get_base_path()
    created = []
    for relative in RUNTIME_FILES:
        target = os.path.join(base, *relative.split("/"))
        if os.path.exists(target):
            continue
        source = os.path.join(base, *default_path_for(relative).split("/"))
        if not os.path.isfile(source):
            logger.error("No se encontró el valor por defecto %s para crear %s", source, target)
            continue
        os.makedirs(os.path.dirname(target), exist_ok=True)
        shutil.copyfile(source, target)
        created.append(relative)
        logger.info("Archivo de runtime creado desde su valor por defecto: %s", relative)
    return created


def collect_include_files(base_path: str, include_dirs: list[str]) -> list[tuple[str, str]]:
    """
    Calcula la lista (origen, destino) de archivos a empaquetar en el build, excluyendo los archivos de runtime.

    Así el build nunca incluye la configuración ni los contadores del equipo de desarrollo.
    Args:
        base_path: Raíz del proyecto.
        include_dirs: Directorios (relativos a la raíz) a recorrer.
    """
    excluded = {os.path.normpath(p) for p in RUNTIME_FILES}
    result = []
    for dir_name in include_dirs:
        dir_path = os.path.join(base_path, dir_name)
        if not os.path.exists(dir_path):
            continue
        for root, _dirs, files in os.walk(dir_path):
            for file in files:
                source = os.path.join(root, file)
                dest = os.path.relpath(source, base_path)
                if os.path.normpath(dest) in excluded:
                    continue
                result.append((source, dest))
    return result
