#!/usr/bin/env python
"""
Copyright © 2024, Iron Graterol
Licensed under the GNU Affero General Public License, version 3 or later.

Aplicación de una actualización ya descargada y validada (ver `handy/updater.py`). `launch_apply` lo invoca la
aplicación instalada: lanza el ejecutable NUEVO (extraído en `updates/`) con `--apply-update` y se cierra. Ese
ejecutable corre desde su propia carpeta (sin bloqueos de archivos de Windows), espera a que el proceso viejo termine,
respalda los archivos del programa, copia los nuevos encima SIN tocar los datos del cliente y arranca la aplicación
instalada. Ante cualquier fallo restaura el respaldo y arranca la versión anterior. Sin consola (cx_Freeze base="gui"):
todo se registra en `<instalación>/logs/update.log`.
"""

import logging
import os
import shutil
import subprocess
import sys
import time
from collections.abc import Callable
from datetime import datetime
from pathlib import Path

from handy.runtime_files import is_runtime_path
from handy.version import __version__

EXE_NAME = "ApiPS.exe"
# Carpetas de datos del cliente (nunca se respaldan, se sobrescriben ni se restauran): ver
# `handy.runtime_files.RUNTIME_DIRS` / `is_runtime_path`
KEEP_BACKUPS = 3  # respaldos de programa que se conservan
DEFAULT_TIMEOUT = 120  # segundos esperando que el proceso viejo termine
UNKNOWN_VERSION = "anterior"

logger = logging.getLogger("handy.update_apply")


def _program_files(root: Path, skip: Path | None = None) -> list[Path]:
    """
    Lista los archivos del programa (todo menos los datos del cliente) bajo una carpeta.
    Args:
        root: Carpeta base (instalación, respaldo o versión preparada)
        skip: Subcarpeta a ignorar siempre (p. ej. la carpeta preparada si estuviera dentro)
    Returns:
        list[Path]: Rutas relativas a `root`
    """
    result = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if skip is not None and (path == skip or skip in path.parents):
            continue
        if not is_runtime_path(relative):
            result.append(relative)
    return result


def launch_apply(
    staged_dir: Path,
    install_dir: Path,
    pid: int | None = None,
    popen: Callable[..., subprocess.Popen] | None = None,
) -> subprocess.Popen:
    """
    Lanza, desacoplado, el ejecutable preparado con `--apply-update`. Quien llama debe cerrar la aplicación después.
    Args:
        staged_dir: Carpeta con la nueva versión extraída
        install_dir: Carpeta de instalación a actualizar
        pid: PID del proceso actual (por defecto `os.getpid()`)
        popen: Fábrica de procesos inyectable (por defecto `subprocess.Popen`)
    Returns:
        subprocess.Popen: El proceso lanzado
    """
    popen = popen or subprocess.Popen
    command = [
        str(Path(staged_dir) / EXE_NAME),
        "--apply-update",
        "--install-dir",
        str(install_dir),
        "--pid",
        str(pid if pid is not None else os.getpid()),
        "--old-version",
        __version__,
    ]
    if sys.platform == "win32":
        flags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
        return popen(command, cwd=str(staged_dir), creationflags=flags, close_fds=True)
    # Otros sistemas: solo lo usan los tests; sesión propia para que sobreviva al proceso que lo lanza
    return popen(command, cwd=str(staged_dir), start_new_session=True, close_fds=True)


ERROR_INVALID_PARAMETER = 87  # OpenProcess con un PID inexistente: el proceso ya no existe
OPEN_RETRY_SECONDS = 0.5  # pausa entre reintentos de OpenProcess cuando falla por otra causa (p. ej. acceso denegado)


def _win_open_process(pid: int) -> tuple[int | None, int]:
    """
    Abre un proceso de Windows con permiso SYNCHRONIZE (solo Windows).
    Args:
        pid: Identificador del proceso
    Returns:
        tuple[int | None, int]: (handle o None si falló, código de GetLastError cuando falló; 0 si abrió)
    """
    import ctypes

    synchronize = 0x00100000
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.OpenProcess.argtypes = [ctypes.c_uint32, ctypes.c_int, ctypes.c_uint32]
    kernel32.OpenProcess.restype = ctypes.c_void_p  # HANDLE: 64 bits seguros
    handle = kernel32.OpenProcess(synchronize, False, int(pid))
    if not handle:
        return None, ctypes.get_last_error()
    return handle, 0


def _win_wait_and_close(handle: int, timeout: float) -> bool:
    """
    Espera a que el proceso (handle abierto) termine y cierra el handle (solo Windows).
    Args:
        handle: Handle devuelto por `_win_open_process`
        timeout: Segundos máximos de espera
    Returns:
        bool: True si el proceso terminó; False si sigue vivo al agotar el tiempo
    """
    import ctypes

    wait_object_0 = 0
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.WaitForSingleObject.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
    kernel32.WaitForSingleObject.restype = ctypes.c_uint32
    kernel32.CloseHandle.argtypes = [ctypes.c_void_p]
    try:
        return kernel32.WaitForSingleObject(handle, int(max(timeout, 0) * 1000)) == wait_object_0
    finally:
        kernel32.CloseHandle(handle)


def _wait_exit_windows(
    pid: int,
    timeout: float,
    open_process: Callable[[int], tuple[int | None, int]] | None = None,
    wait_and_close: Callable[[int, float], bool] | None = None,
    sleep: Callable[[float], None] = time.sleep,
    clock: Callable[[], float] = time.monotonic,
) -> bool:
    """
    Lógica de espera en Windows con las llamadas al sistema inyectables (para probarla en cualquier sistema).
    Un handle nulo solo significa "el proceso ya no existe" si el error es ERROR_INVALID_PARAMETER (87); con cualquier
    otro (p. ej. acceso denegado) el proceso puede seguir vivo, así que se reintenta hasta agotar el tiempo y, si
    sigue fallando, se devuelve False para que quien llama aborte sin tocar nada.
    Args:
        pid: Identificador del proceso
        timeout: Segundos máximos de espera
        open_process: Abre el proceso: devuelve (handle | None, error)
        wait_and_close: Espera el handle y lo cierra
        sleep: Pausa entre reintentos
        clock: Reloj monotónico
    Returns:
        bool: True si terminó (o ya no existía); False si sigue vivo o no se pudo comprobar al agotar el tiempo
    """
    open_process = open_process or _win_open_process
    wait_and_close = wait_and_close or _win_wait_and_close
    deadline = clock() + timeout
    while True:
        handle, error = open_process(pid)
        if handle:
            return wait_and_close(handle, max(deadline - clock(), 0))
        if error == ERROR_INVALID_PARAMETER:
            return True
        if clock() >= deadline:
            logger.warning("No se pudo comprobar el proceso %s (error %s): se aborta la actualización", pid, error)
            return False
        sleep(OPEN_RETRY_SECONDS)


def wait_process_exit(pid: int, timeout: float) -> bool:
    """
    Espera a que un proceso termine.
    Args:
        pid: Identificador del proceso
        timeout: Segundos máximos de espera
    Returns:
        bool: True si terminó (o ya no existía); False si sigue vivo al agotar el tiempo
    """
    if sys.platform == "win32":
        return _wait_exit_windows(pid, timeout)
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return True
        except PermissionError:
            pass  # existe pero de otro usuario: sigue vivo
        time.sleep(0.2)
    return False


def launch_installed(install_dir: Path) -> subprocess.Popen:
    """
    Arranca la aplicación instalada, desacoplada de este proceso.
    Args:
        install_dir: Carpeta de instalación
    Returns:
        subprocess.Popen: El proceso lanzado
    """
    command = [str(Path(install_dir) / EXE_NAME)]
    if sys.platform == "win32":
        flags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
        return subprocess.Popen(command, cwd=str(install_dir), creationflags=flags, close_fds=True)
    return subprocess.Popen(command, cwd=str(install_dir), start_new_session=True, close_fds=True)


def _setup_log(install_dir: Path) -> logging.Handler | None:
    """
    Agrega un handler de archivo propio (`logs/update.log`, modo append). Sin consola: no usa stdout/stderr.
    Args:
        install_dir: Carpeta de instalación
    Returns:
        logging.Handler | None: El handler agregado, o None si no se pudo crear el archivo
    """
    try:
        log_dir = Path(install_dir) / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        handler = logging.FileHandler(log_dir / "update.log", mode="a", encoding="utf-8")
    except OSError:
        return None
    handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return handler


def _prune_backups(backups_dir: Path, keep: int) -> None:
    """Conserva solo los `keep` respaldos de programa más recientes (carpetas `app-*`)."""
    folders = sorted((p for p in backups_dir.glob("app-*") if p.is_dir()), key=lambda p: p.name)
    # El nombre termina en una marca de tiempo; se ordena por fecha de modificación para no depender de la versión
    folders.sort(key=lambda p: p.stat().st_mtime)
    for old in folders[:-keep] if keep > 0 else folders:
        shutil.rmtree(old, ignore_errors=True)


def _backup(install_dir: Path, old_version: str, now: datetime) -> Path:
    """
    Copia los archivos del programa a `backups/app-<versión>-<fecha>/`.
    Args:
        install_dir: Carpeta de instalación
        old_version: Versión instalada (o "anterior")
        now: Fecha y hora actuales
    Returns:
        Path: Carpeta del respaldo
    """
    backup_dir = install_dir / "backups" / f"app-{old_version}-{now.strftime('%Y%m%d_%H%M%S')}"
    backup_dir.mkdir(parents=True, exist_ok=True)
    for relative in _program_files(install_dir):
        target = backup_dir / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(install_dir / relative, target)
    return backup_dir


def _restore(backup_dir: Path, install_dir: Path, added: list[Path]) -> None:
    """
    Restaura el respaldo sobre la instalación y elimina los archivos que la actualización agregó.
    Args:
        backup_dir: Respaldo de programa
        install_dir: Carpeta de instalación
        added: Archivos (relativos) que la actualización creó y no existían antes
    """
    for relative in added:
        if not is_runtime_path(relative):
            (install_dir / relative).unlink(missing_ok=True)
    for relative in _program_files(backup_dir):
        target = install_dir / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(backup_dir / relative, target)


def apply_update(
    staged_dir: Path,
    install_dir: Path,
    old_pid: int | None,
    *,
    wait_process: Callable[[int, float], bool] | None = None,
    launch: Callable[[Path], object] | None = None,
    now: Callable[[], datetime] | None = None,
    timeout: float = DEFAULT_TIMEOUT,
    old_version: str = UNKNOWN_VERSION,
) -> int:
    """
    Aplica una actualización desde la versión nueva ya extraída. Nunca deja al cliente sin aplicación que arrancar.
    Args:
        staged_dir: Carpeta con la nueva versión (la del ejecutable en ejecución)
        install_dir: Carpeta de instalación a actualizar
        old_pid: PID de la aplicación vieja a esperar (None si no hay)
        wait_process: Espera inyectable `(pid, timeout) -> bool`
        launch: Arranque inyectable de la aplicación instalada `(install_dir) -> Popen`
        now: Reloj inyectable
        timeout: Segundos máximos esperando al proceso viejo
        old_version: Versión instalada antes de actualizar (para nombrar el respaldo)
    Returns:
        int: 0 si se actualizó; 1 si falló y se restauró; 2 si no se tocó nada (el proceso viejo no terminó)
    """
    staged_dir, install_dir = Path(staged_dir), Path(install_dir)
    wait_process = wait_process or wait_process_exit
    launch = launch or launch_installed
    now = now or datetime.now
    handler = _setup_log(install_dir)
    try:
        logger.info("Iniciando actualización: %s -> %s", staged_dir, install_dir)
        if old_pid is not None and not wait_process(old_pid, timeout):
            logger.error("El proceso %s no terminó en %s s: se cancela sin modificar nada", old_pid, timeout)
            return 2

        try:
            backup_dir = _backup(install_dir, old_version, now())
        except Exception:
            logger.exception("No se pudo crear el respaldo: se cancela sin modificar la instalación")
            # La aplicación vieja ya terminó: se vuelve a iniciar tal cual para no dejar al cliente sin servicio
            try:
                launch(install_dir)
            except Exception:
                logger.exception("No se pudo iniciar la versión instalada")
            return 2
        logger.info("Respaldo creado en %s", backup_dir)
        _prune_backups(install_dir / "backups", KEEP_BACKUPS)

        added: list[Path] = []
        try:
            for relative in _program_files(staged_dir):
                if is_runtime_path(relative):  # defensa extra: la validación del zip ya lo impide
                    raise RuntimeError(f"La actualización intenta escribir un archivo del cliente: {relative}")
                target = install_dir / relative
                if not target.exists():
                    added.append(relative)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(staged_dir / relative, target)
            logger.info("Archivos copiados; iniciando la aplicación actualizada")
            launch(install_dir)
        except Exception:
            logger.exception("Falló la actualización; restaurando la versión anterior")
            try:
                _restore(backup_dir, install_dir, added)
                logger.info("Respaldo restaurado; iniciando la versión anterior")
            except Exception:
                logger.exception("No se pudo restaurar el respaldo completo; revise %s", backup_dir)
            try:
                launch(install_dir)
            except Exception:
                logger.exception("No se pudo iniciar la versión anterior")
            return 1

        logger.info("Actualización aplicada correctamente")
        return 0
    finally:
        if handler is not None:
            logger.removeHandler(handler)
            handler.close()
