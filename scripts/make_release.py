#!/usr/bin/env python
"""
Copyright © 2024, Iron Graterol
Licensed under the GNU Affero General Public License, version 3 or later.

Empaqueta la carpeta compilada (`build/ApiPS`, generada por `run.bat`) para publicarla en un Release de GitHub:
crea `dist/ApiPS-<versión>.zip` (con la carpeta `ApiPS/` en la raíz) y `dist/ApiPS-<versión>.zip.sha256`.

Antes de comprimir verifica que la compilación esté limpia: si alguien ejecutó `ApiPS.exe` dentro de `build/ApiPS`,
se habrán creado archivos del cliente (configuración en uso, base de datos, logs) que nunca deben publicarse.

Uso (desde la raíz del repositorio; en Windows lo llama `release.bat`):
    uv run python scripts/make_release.py
"""

import argparse
import hashlib
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from handy.runtime_files import RUNTIME_FILES
from handy.version import __version__

APP_NAME = "ApiPS"
EXE_NAME = "ApiPS.exe"

# Carpetas que crea la aplicación al ejecutarse (datos del cliente): nunca van en un release
RUNTIME_DIRS = ("data", "logs", "backups")


class ReleaseError(Exception):
    """Error que impide generar el release (compilación ausente, sucia o archivo ya existente)."""


def find_runtime_leftovers(build_dir: Path) -> list[str]:
    """
    Busca en la compilación archivos o carpetas que solo crea la aplicación al ejecutarse.
    Args:
        build_dir: Carpeta compilada (build/ApiPS)
    Returns:
        list[str]: Rutas relativas encontradas (vacía si la compilación está limpia)
    """
    leftovers = [relative for relative in RUNTIME_FILES if (build_dir / relative).exists()]
    leftovers += [f"{name}/" for name in RUNTIME_DIRS if (build_dir / name).exists()]
    return leftovers


def sha256_of(path: Path) -> str:
    """
    Calcula el SHA256 de un archivo leyéndolo por bloques.
    Args:
        path: Archivo a resumir
    Returns:
        str: Hash en hexadecimal (minúsculas)
    """
    digest = hashlib.sha256()
    with open(path, "rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def make_release(build_dir: Path, out_dir: Path, version: str, force: bool = False) -> tuple[Path, Path]:
    """
    Comprime la compilación y escribe su SHA256.
    Args:
        build_dir: Carpeta compilada (debe contener ApiPS.exe)
        out_dir: Carpeta de salida (se crea si no existe)
        version: Versión a publicar (p. ej. "2.12.0")
        force: True para reemplazar un zip de la misma versión ya generado
    Returns:
        tuple[Path, Path]: Rutas del zip y del archivo .sha256
    Raises:
        ReleaseError: Si falta la compilación, está sucia o el zip ya existe (sin force)
    """
    if not (build_dir / EXE_NAME).is_file():
        raise ReleaseError(f"No existe {build_dir / EXE_NAME}: ejecute primero run.bat")

    leftovers = find_runtime_leftovers(build_dir)
    if leftovers:
        raise ReleaseError(
            "La compilación contiene archivos del cliente (¿se ejecutó ApiPS.exe dentro de build?): "
            + ", ".join(leftovers)
            + ". Vuelva a ejecutar run.bat y no abra la aplicación desde la carpeta build."
        )

    out_dir.mkdir(parents=True, exist_ok=True)
    zip_path = out_dir / f"{APP_NAME}-{version}.zip"
    sha_path = out_dir / f"{zip_path.name}.sha256"
    if zip_path.exists() and not force:
        raise ReleaseError(f"Ya existe {zip_path}: suba la versión en handy/version.py o use --force")

    # Rutas con "/" y la carpeta ApiPS/ en la raíz: al descomprimir queda la misma carpeta que se entrega al cliente
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(build_dir.rglob("*")):
            if path.is_file():
                archive.write(path, f"{APP_NAME}/{path.relative_to(build_dir).as_posix()}")

    # Formato de sha256sum ("<hash>  <archivo>"): se puede verificar con sha256sum -c o comparar a mano
    sha_path.write_text(f"{sha256_of(zip_path)}  {zip_path.name}\n", encoding="utf-8")
    return zip_path, sha_path


def main(argv: list[str] | None = None) -> int:
    """
    Punto de entrada de línea de comandos.
    Args:
        argv: Argumentos (None usa los de sys.argv)
    Returns:
        int: Código de salida (0 éxito, 1 error)
    """
    parser = argparse.ArgumentParser(description="Empaqueta build/ApiPS para un Release de GitHub")
    parser.add_argument("--build-dir", type=Path, default=ROOT / "build" / APP_NAME, help="Carpeta compilada")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "dist", help="Carpeta de salida")
    parser.add_argument("--force", action="store_true", help="Reemplazar un zip de la misma versión")
    args = parser.parse_args(argv)

    try:
        zip_path, sha_path = make_release(args.build_dir, args.out_dir, __version__, args.force)
    except ReleaseError as e:
        print(f"Error: {e}")
        return 1

    print(f"Versión {__version__} lista para publicar:")
    print(f"  {zip_path}")
    print(f"  {sha_path}")
    print(f"Cree en GitHub el Release con la etiqueta v{__version__} y adjunte ambos archivos.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
