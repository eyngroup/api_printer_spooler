"""Tests del empaquetado del release (scripts/make_release.py) sobre una compilación simulada."""

import hashlib
import importlib.util
import zipfile
from pathlib import Path

import pytest

_SPEC = importlib.util.spec_from_file_location(
    "make_release", Path(__file__).resolve().parents[1] / "scripts" / "make_release.py"
)
make_release = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(make_release)


@pytest.fixture
def build_dir(tmp_path: Path) -> Path:
    """Compilación limpia simulada: ejecutable, librerías y valores por defecto (sin archivos del cliente)."""
    build = tmp_path / "build" / "ApiPS"
    (build / "lib").mkdir(parents=True)
    (build / "config" / "defaults").mkdir(parents=True)
    (build / "ApiPS.exe").write_bytes(b"MZ-ejecutable")
    (build / "python310.dll").write_bytes(b"dll")
    (build / "lib" / "library.zip").write_bytes(b"codigo")
    (build / "config" / "defaults" / "config.json").write_text("{}", encoding="utf-8")
    return build


def test_creates_zip_with_apips_root_and_sha256(build_dir: Path, tmp_path: Path):
    """El zip lleva la carpeta ApiPS/ en la raíz con todos los archivos, y el .sha256 coincide con el zip."""
    zip_path, sha_path = make_release.make_release(build_dir, tmp_path / "dist", "2.12.0")

    assert zip_path.name == "ApiPS-2.12.0.zip"
    with zipfile.ZipFile(zip_path) as archive:
        names = set(archive.namelist())
    assert names == {
        "ApiPS/ApiPS.exe",
        "ApiPS/python310.dll",
        "ApiPS/lib/library.zip",
        "ApiPS/config/defaults/config.json",
    }

    expected = hashlib.sha256(zip_path.read_bytes()).hexdigest()
    assert sha_path.name == "ApiPS-2.12.0.zip.sha256"
    assert sha_path.read_text(encoding="utf-8") == f"{expected}  ApiPS-2.12.0.zip\n"


def test_fails_without_executable(tmp_path: Path):
    """Sin ApiPS.exe (no se ejecutó run.bat) no se genera nada."""
    with pytest.raises(make_release.ReleaseError, match="run.bat"):
        make_release.make_release(tmp_path / "build" / "ApiPS", tmp_path / "dist", "2.12.0")
    assert not (tmp_path / "dist").exists()


@pytest.mark.parametrize(
    "leftover",
    [
        "config/config.json",
        "templates/template_matriz_carta.json",
        "data/print_jobs.db",
        "logs/app.log",
        "backups/x.db",
    ],
)
def test_refuses_build_with_client_files(build_dir: Path, tmp_path: Path, leftover: str):
    """Si la app se ejecutó dentro de build, sus archivos (config en uso, BD, logs) nunca se publican."""
    target = build_dir / leftover
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("dato del cliente", encoding="utf-8")

    with pytest.raises(make_release.ReleaseError, match="archivos del cliente"):
        make_release.make_release(build_dir, tmp_path / "dist", "2.12.0")
    assert not list((tmp_path / "dist").glob("*.zip"))


def test_does_not_overwrite_existing_version_unless_forced(build_dir: Path, tmp_path: Path):
    """Un zip de la misma versión no se reemplaza por accidente; con force sí."""
    out = tmp_path / "dist"
    make_release.make_release(build_dir, out, "2.12.0")
    with pytest.raises(make_release.ReleaseError, match="handy/version.py"):
        make_release.make_release(build_dir, out, "2.12.0")
    make_release.make_release(build_dir, out, "2.12.0", force=True)


def test_main_returns_error_code_on_failure(tmp_path: Path, capsys):
    """La línea de comandos devuelve 1 y explica el error (release.bat se detiene)."""
    code = make_release.main(["--build-dir", str(tmp_path / "nada"), "--out-dir", str(tmp_path / "dist")])
    assert code == 1
    assert "Error:" in capsys.readouterr().out
