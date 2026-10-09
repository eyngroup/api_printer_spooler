"""Tests del bootstrap de archivos de runtime y de la exclusión de los mismos en el build."""

import json
import os
import shutil
from pathlib import Path

import pytest
from jsonschema import validate

from handy import runtime_files
from handy.runtime_files import RUNTIME_FILES, collect_include_files, default_path_for, ensure_runtime_files
from handy.tools import get_base_path
from server.config_loader import CONFIG_SCHEMA

REPO = Path(get_base_path())


@pytest.fixture
def base(tmp_path: Path) -> Path:
    """Directorio base temporal que contiene solo los valores por defecto del repositorio."""
    for relative in RUNTIME_FILES:
        default = default_path_for(relative)
        target = tmp_path / default
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(REPO / default, target)
    return tmp_path


def test_creates_missing_files_from_defaults(base: Path):
    """Un arranque sin archivos de runtime los crea idénticos a sus defaults."""
    created = ensure_runtime_files(str(base))
    assert sorted(created) == sorted(RUNTIME_FILES)
    for relative in RUNTIME_FILES:
        assert (base / relative).read_bytes() == (base / default_path_for(relative)).read_bytes()


def test_never_overwrites_existing_file(base: Path):
    """Un archivo de runtime existente conserva su contenido y no se reporta como creado."""
    existing = base / "config" / "config.json"
    existing.write_text('{"custom": true}', encoding="utf-8")
    created = ensure_runtime_files(str(base))
    assert "config/config.json" not in created
    assert existing.read_text(encoding="utf-8") == '{"custom": true}'
    assert (base / "templates" / "template_ticket_simple.json").exists()


def test_uses_get_base_path_by_default(base: Path, monkeypatch: pytest.MonkeyPatch):
    """Sin argumento usa get_base_path() (carpeta del exe cuando está congelado)."""
    monkeypatch.setattr(runtime_files, "get_base_path", lambda: str(base))
    assert len(ensure_runtime_files()) == len(RUNTIME_FILES)


def test_default_config_is_valid_and_clean():
    """El config por defecto cumple el esquema y no trae puertos ni código de seguridad del desarrollador."""
    data = json.loads((REPO / "config" / "defaults" / "config.json").read_text(encoding="utf-8"))
    validate(data, CONFIG_SCHEMA)
    assert data["printers"]["fiscal"]["fiscal_port"] == ""
    assert data["printers"]["matrix"]["matrix_port"] == ""
    assert data["printers"]["ticket"]["ticket_port"] == ""
    assert data["security"]["security_code"] == ""


def test_default_templates_have_expected_keys():
    """Los templates por defecto traen sus secciones y contadores en el valor inicial."""
    fiscal = json.loads((REPO / "templates" / "defaults" / "template_fiscal_printer.json").read_text("utf-8"))
    assert {"fiscal", "format"} <= fiscal.keys()
    for name in ("template_matriz_carta.json", "template_ticket_simple.json"):
        data = json.loads((REPO / "templates" / "defaults" / name).read_text("utf-8"))
        assert {"header", "footer", "format", "counter"} <= data.keys()
        for key in ("document_invoice", "document_credit", "document_debit", "document_note"):
            assert data["counter"][key] == "00000000"


def test_build_excludes_runtime_files_but_keeps_defaults():
    """El build incluye defaults y estáticos, nunca los archivos de runtime."""
    files = collect_include_files(str(REPO), ["config", "templates"])
    dests = {os.path.normpath(dest) for _src, dest in files}
    for relative in RUNTIME_FILES:
        assert os.path.normpath(relative) not in dests
        assert os.path.normpath(default_path_for(relative)) in dests
    assert os.path.normpath("config/hka_max_char.json") in dests
