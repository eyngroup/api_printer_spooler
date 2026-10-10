#!/usr/bin/env python
"""
Copyright © 2024, Iron Graterol
Licensed under the GNU Affero General Public License, version 3 or later.

Actualización automática (lado cliente): consulta el último Release publicado en GitHub, descarga el zip junto con su
SHA256, lo verifica, valida su contenido y lo extrae a `<instalación>/updates/ApiPS-<versión>/`. No instala nada: la
aplicación de la actualización la hace `handy/update_apply.py` desde la copia ya extraída. Este módulo no depende de
Flask ni de Tkinter para poder usarse desde la ventana de escritorio y desde los tests.
"""

import hashlib
import logging
import re
import shutil
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

import requests

from handy.runtime_files import RUNTIME_FILES
from handy.version import __version__

logger = logging.getLogger(__name__)

REPO = "eyngroup/api_printer_spooler"
API_URL = f"https://api.github.com/repos/{REPO}/releases/latest"
APP_DIR = "ApiPS"
EXE_NAME = "ApiPS.exe"
TIMEOUT = 10  # segundos por solicitud HTTP
MAX_NOTES = 2000  # caracteres máximos de las notas del release
MAX_UNCOMPRESSED = 500 * 1024 * 1024  # tamaño máximo descomprimido del zip (500 MB)
# Carpetas de datos del cliente que nunca deben venir en un release ni ser tocadas por una actualización
RUNTIME_DIRS = ("data", "logs", "backups", "updates")
NO_RELEASES_MESSAGE = "No hay versiones publicadas"
UNSUPPORTED_REASON = (
    "Disponible solo en la aplicación compilada para Windows; con el código fuente actualice con git pull"
)

_VERSION_RE = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)$")


class UpdateError(Exception):
    """Error al descargar, verificar o preparar una actualización (el mensaje está en español)."""


@dataclass
class UpdateInfo:
    """Resultado de consultar el último release publicado."""

    available: bool = False
    current: str = ""
    latest: str = ""
    zip_url: str = ""
    sha256_url: str = ""
    notes: str = ""
    error: str | None = None
    message: str = ""


def is_supported() -> bool:
    """
    Indica si esta instalación puede autoactualizarse: solo la aplicación compilada (congelada) en Windows.
    Returns:
        bool: True si es el ejecutable compilado en Windows
    """
    return bool(getattr(sys, "frozen", False)) and sys.platform == "win32"


def parse_version(text: str) -> tuple[int, int, int] | None:
    """
    Convierte `MAJOR.MINOR.PATCH` (con "v" inicial opcional) en una tupla numérica.
    Args:
        text: Versión o etiqueta del release
    Returns:
        tuple[int, int, int] | None: La tupla, o None si no se puede interpretar
    """
    match = _VERSION_RE.match(str(text).strip())
    if not match:
        return None
    return int(match.group(1)), int(match.group(2)), int(match.group(3))


def _headers() -> dict[str, str]:
    """Cabeceras de las solicitudes a GitHub (API v3 y User-Agent con la versión actual)."""
    return {"Accept": "application/vnd.github+json", "User-Agent": f"ApiPS/{__version__}"}


def check_latest(current_version: str, session: requests.Session | None = None) -> UpdateInfo:
    """
    Consulta el último release de GitHub y lo compara con la versión actual. Nunca lanza excepciones.
    Args:
        current_version: Versión instalada (p. ej. "2.11.0")
        session: Sesión HTTP inyectable (por defecto `requests`)
    Returns:
        UpdateInfo: Resultado; `error` trae el texto en español si no se pudo determinar
    """
    info = UpdateInfo(current=current_version)
    getter = session.get if session is not None else requests.get
    try:
        response = getter(API_URL, headers=_headers(), timeout=TIMEOUT)
    except requests.RequestException as e:
        info.error = f"No se pudo consultar las actualizaciones: {e}"
        return info
    except Exception as e:  # noqa: BLE001 - la consulta nunca debe tumbar a quien la llama
        info.error = f"Error inesperado al consultar las actualizaciones: {e}"
        return info

    if response.status_code == 404:
        info.message = NO_RELEASES_MESSAGE
        return info
    if response.status_code != 200:
        info.error = f"GitHub respondió con el código HTTP {response.status_code}"
        return info

    try:
        data = response.json()
        tag = str(data["tag_name"])
        body = data.get("body") or ""
        assets = {a["name"]: a["browser_download_url"] for a in data.get("assets", [])}
    except (ValueError, KeyError, TypeError, AttributeError):
        info.error = "La respuesta de GitHub no es válida"
        return info

    latest_tuple = parse_version(tag)
    current_tuple = parse_version(current_version)
    if latest_tuple is None or current_tuple is None:
        info.error = f"No se pudo interpretar la versión ({tag!r} / {current_version!r})"
        return info

    info.latest = tag.strip().lstrip("v")
    info.notes = str(body)[:MAX_NOTES]
    if latest_tuple <= current_tuple:
        info.message = "La aplicación está actualizada"
        return info

    zip_name = f"{APP_DIR}-{info.latest}.zip"
    zip_url = assets.get(zip_name)
    sha_url = assets.get(f"{zip_name}.sha256")
    if not zip_url or not sha_url:
        info.error = f"Release incompleto: faltan {zip_name} o su .sha256"
        return info

    info.available = True
    info.zip_url = zip_url
    info.sha256_url = sha_url
    info.message = f"Nueva versión disponible: {info.latest}"
    return info


def _is_runtime_path(relative: str) -> bool:
    """
    Indica si una ruta relativa pertenece a los datos del cliente (archivos de runtime o carpetas de datos).
    Args:
        relative: Ruta relativa con "/" (sin el prefijo ApiPS/)
    Returns:
        bool: True si es una ruta de cliente protegida
    """
    normalized = relative.strip("/").lower()
    if normalized in {path.lower() for path in RUNTIME_FILES}:
        return True
    first = normalized.split("/", 1)[0]
    return first in RUNTIME_DIRS


def validate_zip(archive: zipfile.ZipFile) -> list[zipfile.ZipInfo]:
    """
    Valida el contenido de un zip ANTES de extraerlo.
    Args:
        archive: Zip abierto
    Returns:
        list[zipfile.ZipInfo]: Miembros (solo archivos) que se pueden extraer
    Raises:
        UpdateError: Si hay rutas peligrosas, archivos del cliente, falta el exe o supera el tamaño máximo
    """
    members = []
    total = 0
    for member in archive.infolist():
        name = member.filename
        if "\\" in name or ":" in name or name.startswith("/") or PurePosixPath(name).is_absolute():
            raise UpdateError(f"El paquete contiene una ruta no permitida: {name}")
        parts = name.split("/")
        if ".." in parts:
            raise UpdateError(f"El paquete contiene una ruta no permitida: {name}")
        if parts[0] != APP_DIR:
            raise UpdateError(f"El paquete contiene un archivo fuera de {APP_DIR}/: {name}")
        if member.is_dir():
            continue
        relative = "/".join(parts[1:])
        if not relative:
            raise UpdateError(f"El paquete contiene una ruta no permitida: {name}")
        if _is_runtime_path(relative):
            raise UpdateError(f"El paquete contiene archivos del cliente: {relative}")
        total += member.file_size
        if total > MAX_UNCOMPRESSED:
            raise UpdateError("El paquete descomprimido supera el tamaño máximo permitido")
        members.append(member)
    if not any(m.filename == f"{APP_DIR}/{EXE_NAME}" for m in members):
        raise UpdateError(f"El paquete no contiene {APP_DIR}/{EXE_NAME}")
    return members


def _download(url: str, target: Path, session: requests.Session | None) -> None:
    """
    Descarga una URL a un archivo por bloques.
    Args:
        url: Dirección a descargar
        target: Archivo de destino
        session: Sesión HTTP inyectable
    Raises:
        UpdateError: Si falla la red o la respuesta no es 200
    """
    getter = session.get if session is not None else requests.get
    try:
        response = getter(url, headers={"User-Agent": _headers()["User-Agent"]}, timeout=TIMEOUT, stream=True)
        if response.status_code != 200:
            raise UpdateError(f"La descarga falló con el código HTTP {response.status_code}")
        with open(target, "wb") as file:
            for block in response.iter_content(chunk_size=1024 * 1024):
                if block:
                    file.write(block)
    except requests.RequestException as e:
        raise UpdateError(f"No se pudo descargar la actualización: {e}") from e
    except OSError as e:
        raise UpdateError(f"No se pudo guardar la descarga: {e}") from e


def _sha256_of(path: Path) -> str:
    """Calcula el SHA256 (hexadecimal) de un archivo leyéndolo por bloques."""
    digest = hashlib.sha256()
    with open(path, "rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _read_expected_hash(sha_path: Path, zip_name: str) -> str:
    """
    Lee el hash esperado de un archivo en formato sha256sum (`<hash>  <archivo>`).
    Args:
        sha_path: Archivo .sha256 descargado
        zip_name: Nombre del zip al que debe corresponder
    Returns:
        str: Hash en minúsculas
    Raises:
        UpdateError: Si el formato es inválido o el nombre no coincide
    """
    parts = sha_path.read_text(encoding="utf-8", errors="replace").strip().split(None, 1)
    if len(parts) != 2 or not re.fullmatch(r"[0-9a-fA-F]{64}", parts[0]):
        raise UpdateError("El archivo .sha256 no tiene un formato válido")
    if parts[1].strip().lstrip("*") != zip_name:
        raise UpdateError("El archivo .sha256 no corresponde al paquete descargado")
    return parts[0].lower()


def download_and_stage(info: UpdateInfo, install_dir: Path, session: requests.Session | None = None) -> Path:
    """
    Descarga, verifica y extrae una actualización a `<install_dir>/updates/ApiPS-<versión>/`.
    Args:
        info: Resultado de `check_latest` con `available=True`
        install_dir: Carpeta de instalación (la del ejecutable)
        session: Sesión HTTP inyectable
    Returns:
        Path: Carpeta con la nueva versión lista para aplicar
    Raises:
        UpdateError: En cualquier fallo; no deja una extracción a medias
    """
    if not info.available or not info.zip_url or not info.sha256_url or parse_version(info.latest) is None:
        raise UpdateError("No hay una actualización disponible para descargar")

    updates_dir = Path(install_dir) / "updates"
    zip_name = f"{APP_DIR}-{info.latest}.zip"
    zip_path = updates_dir / zip_name
    sha_path = updates_dir / f"{zip_name}.sha256"
    staging = updates_dir / f"{APP_DIR}-{info.latest}"
    partial = updates_dir / f"{APP_DIR}-{info.latest}.partial"

    try:
        updates_dir.mkdir(parents=True, exist_ok=True)
        _download(info.sha256_url, sha_path, session)
        _download(info.zip_url, zip_path, session)

        expected = _read_expected_hash(sha_path, zip_name)
        if _sha256_of(zip_path) != expected:
            raise UpdateError("La verificación SHA256 falló: el archivo descargado está dañado o fue alterado")

        shutil.rmtree(partial, ignore_errors=True)
        try:
            with zipfile.ZipFile(zip_path) as archive:
                members = validate_zip(archive)
                for member in members:
                    target = partial.joinpath(*member.filename.split("/")[1:])
                    target.parent.mkdir(parents=True, exist_ok=True)
                    with archive.open(member) as source, open(target, "wb") as out:
                        shutil.copyfileobj(source, out)
        except zipfile.BadZipFile as e:
            raise UpdateError(f"El paquete descargado no es un zip válido: {e}") from e
        except OSError as e:
            raise UpdateError(f"No se pudo extraer la actualización: {e}") from e

        # Solo cuando la extracción terminó completa reemplaza una preparación previa de la misma versión
        shutil.rmtree(staging, ignore_errors=True)
        partial.rename(staging)
    except UpdateError:
        shutil.rmtree(partial, ignore_errors=True)
        raise
    except OSError as e:
        shutil.rmtree(partial, ignore_errors=True)
        raise UpdateError(f"No se pudo preparar la actualización: {e}") from e

    logger.info("Actualización %s preparada en %s", info.latest, staging)
    return staging


def cleanup_updates(install_dir: Path) -> None:
    """
    Borra al arrancar lo que quedó en `<install_dir>/updates/` (zips y versiones ya aplicadas o abandonadas).
    Ignora errores: justo después de actualizar, el ejecutable preparado puede seguir terminando y Windows bloquea
    su carpeta; lo que no se pueda borrar ahora se borra en el siguiente arranque. Nunca lanza excepciones.
    Args:
        install_dir: Carpeta de instalación
    """
    updates_dir = Path(install_dir) / "updates"
    if not updates_dir.is_dir():
        return
    for entry in updates_dir.iterdir():
        try:
            if entry.is_dir():
                shutil.rmtree(entry, ignore_errors=True)
            else:
                entry.unlink()
        except OSError as e:
            logger.warning("No se pudo borrar %s (se reintenta en el próximo arranque): %s", entry, e)
