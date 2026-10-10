"""
Copyright © 2024, Iron Graterol
Licensed under the GNU Affero General Public License, version 3 or later.

Pruebas de `handy/updater.py`: consulta del release, verificación y preparación (staging) del paquete.
Nunca usan red real: se inyecta una sesión falsa.
"""

import hashlib
import io
import zipfile
from pathlib import Path

import pytest
import requests

from handy import updater
from handy.updater import UpdateError, UpdateInfo, check_latest, download_and_stage


class FakeResponse:
    """Respuesta HTTP mínima."""

    def __init__(self, status=200, json_data=None, content=b"", bad_json=False):
        self.status_code = status
        self._json = json_data
        self._content = content
        self._bad_json = bad_json

    def json(self):
        if self._bad_json:
            raise ValueError("no es JSON")
        return self._json

    def iter_content(self, chunk_size=1):
        for i in range(0, len(self._content), chunk_size):
            yield self._content[i : i + chunk_size]


class FakeSession:
    """Sesión que responde según la URL y registra las llamadas."""

    def __init__(self, responses=None, error=None):
        self.responses = responses or {}
        self.error = error
        self.calls = []

    def get(self, url, **kwargs):
        self.calls.append((url, kwargs))
        if self.error:
            raise self.error
        return self.responses[url]


def release_json(tag="v2.12.0", assets=True):
    """JSON de un release de GitHub con (o sin) los dos assets esperados."""
    ver = tag.lstrip("v")
    items = []
    if assets:
        items = [
            {"name": f"ApiPS-{ver}.zip", "browser_download_url": f"https://x/ApiPS-{ver}.zip"},
            {"name": f"ApiPS-{ver}.zip.sha256", "browser_download_url": f"https://x/ApiPS-{ver}.zip.sha256"},
        ]
    return {"tag_name": tag, "body": "Notas " * 1000, "assets": items}


def check(tag, current="2.11.0", assets=True):
    session = FakeSession({updater.API_URL: FakeResponse(200, release_json(tag, assets))})
    return check_latest(current, session), session


def test_check_newer_available():
    info, session = check("v2.12.0")
    assert info.available and info.latest == "2.12.0" and info.error is None
    assert info.zip_url.endswith("ApiPS-2.12.0.zip") and info.sha256_url.endswith(".zip.sha256")
    assert len(info.notes) <= updater.MAX_NOTES
    headers = session.calls[0][1]["headers"]
    assert headers["Accept"] == "application/vnd.github+json" and headers["User-Agent"].startswith("ApiPS/")
    assert session.calls[0][1]["timeout"] == 10


def test_check_same_and_older_not_available():
    for tag in ("2.11.0", "v2.11.0", "2.10.9"):
        info, _ = check(tag)
        assert not info.available and info.error is None


def test_check_numeric_not_lexicographic():
    info, _ = check("2.100.0", current="2.20.0")
    assert info.available


def test_check_404_is_not_error():
    info = check_latest("2.11.0", FakeSession({updater.API_URL: FakeResponse(404)}))
    assert not info.available and info.error is None and info.message == "No hay versiones publicadas"


def test_check_http_error():
    info = check_latest("2.11.0", FakeSession({updater.API_URL: FakeResponse(500)}))
    assert not info.available and "500" in info.error


def test_check_network_error():
    info = check_latest("2.11.0", FakeSession(error=requests.ConnectionError("sin red")))
    assert not info.available and info.error


def test_check_bad_json():
    info = check_latest("2.11.0", FakeSession({updater.API_URL: FakeResponse(200, bad_json=True)}))
    assert not info.available and info.error


def test_check_missing_assets():
    info, _ = check("v2.12.0", assets=False)
    assert not info.available and "incompleto" in info.error


def test_check_unparsable_tag():
    for tag in ("latest", "v2.12", "2.12.0-beta"):
        info, _ = check(tag)
        assert not info.available and info.error


def test_is_supported_false_when_not_frozen():
    assert updater.is_supported() is False


def test_is_supported_requires_frozen_and_windows(monkeypatch):
    monkeypatch.setattr(updater.sys, "frozen", True, raising=False)
    monkeypatch.setattr(updater.sys, "platform", "win32")
    assert updater.is_supported() is True
    monkeypatch.setattr(updater.sys, "platform", "linux")
    assert updater.is_supported() is False


# ---------------------------------------------------------------- staging


def make_zip(files: dict[str, bytes]) -> bytes:
    """Construye un zip en memoria con los nombres dados (sin normalizarlos)."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for name, data in files.items():
            archive.writestr(name, data)
    return buffer.getvalue()


GOOD = {"ApiPS/ApiPS.exe": b"EXE", "ApiPS/lib/a.pyd": b"A", "ApiPS/config/defaults/config.json": b"{}"}


def stage(tmp_path, zip_bytes, sha_name="ApiPS-2.12.0.zip", sha=None):
    """Prepara una sesión falsa con el zip y llama a download_and_stage."""
    digest = sha or hashlib.sha256(zip_bytes).hexdigest()
    session = FakeSession(
        {
            "https://x/z": FakeResponse(200, content=zip_bytes),
            "https://x/s": FakeResponse(200, content=f"{digest}  {sha_name}\n".encode()),
        }
    )
    info = UpdateInfo(available=True, latest="2.12.0", zip_url="https://x/z", sha256_url="https://x/s")
    return download_and_stage(info, tmp_path, session)


def test_stage_good_zip(tmp_path):
    staged = stage(tmp_path, make_zip(GOOD))
    assert staged == tmp_path / "updates" / "ApiPS-2.12.0"
    assert (staged / "ApiPS.exe").read_bytes() == b"EXE"
    assert (staged / "lib" / "a.pyd").read_bytes() == b"A"
    assert not (staged / "ApiPS").exists()
    assert not (tmp_path / "updates" / "ApiPS-2.12.0.partial").exists()


def test_stage_hash_mismatch(tmp_path):
    with pytest.raises(UpdateError, match="SHA256"):
        stage(tmp_path, make_zip(GOOD), sha="0" * 64)
    assert not (tmp_path / "updates" / "ApiPS-2.12.0").exists()


def test_stage_sha_file_name_mismatch(tmp_path):
    with pytest.raises(UpdateError, match="no corresponde"):
        stage(tmp_path, make_zip(GOOD), sha_name="ApiPS-9.9.9.zip")


def test_stage_invalid_sha_format(tmp_path):
    with pytest.raises(UpdateError):
        stage(tmp_path, make_zip(GOOD), sha="zz")


def test_stage_not_a_zip(tmp_path):
    with pytest.raises(UpdateError):
        stage(tmp_path, b"esto no es un zip")


@pytest.mark.parametrize(
    "extra",
    [
        {"ApiPS/../evil.txt": b"x"},
        {"ApiPS/lib/../../evil.txt": b"x"},
        {"/abs/evil.txt": b"x"},
        {"C:/evil.txt": b"x"},
        {"ApiPS\\lib\\evil.txt": b"x"},
        {"otro/evil.txt": b"x"},
        {"ApiPS/config/config.json": b"{}"},
        {"ApiPS/templates/template_ticket_simple.json": b"{}"},
        {"ApiPS/data/x.db": b"db"},
        {"ApiPS/Logs/a.log": b"log"},
        {"ApiPS/backups/x": b"x"},
        {"ApiPS/updates/x": b"x"},
    ],
)
def test_stage_malicious_zip_rejected(tmp_path, extra):
    with pytest.raises(UpdateError):
        stage(tmp_path, make_zip({**GOOD, **extra}))
    updates = tmp_path / "updates"
    assert not (updates / "ApiPS-2.12.0").exists()
    assert not (updates / "ApiPS-2.12.0.partial").exists()
    assert not (tmp_path / "evil.txt").exists()


def test_stage_missing_exe(tmp_path):
    with pytest.raises(UpdateError, match="ApiPS.exe"):
        stage(tmp_path, make_zip({"ApiPS/lib/a.pyd": b"A"}))


def test_stage_size_limit(tmp_path, monkeypatch):
    monkeypatch.setattr(updater, "MAX_UNCOMPRESSED", 3)
    with pytest.raises(UpdateError, match="tamaño"):
        stage(tmp_path, make_zip(GOOD))
    assert not (tmp_path / "updates" / "ApiPS-2.12.0").exists()


def test_stage_replaces_previous_staging(tmp_path):
    old = tmp_path / "updates" / "ApiPS-2.12.0"
    old.mkdir(parents=True)
    (old / "stale.txt").write_text("viejo")
    staged = stage(tmp_path, make_zip(GOOD))
    assert not (staged / "stale.txt").exists() and (staged / "ApiPS.exe").exists()


def test_stage_download_http_error(tmp_path):
    session = FakeSession({"https://x/z": FakeResponse(500), "https://x/s": FakeResponse(500)})
    info = UpdateInfo(available=True, latest="2.12.0", zip_url="https://x/z", sha256_url="https://x/s")
    with pytest.raises(UpdateError, match="500"):
        download_and_stage(info, tmp_path, session)


def test_stage_requires_available(tmp_path):
    with pytest.raises(UpdateError):
        download_and_stage(UpdateInfo(), Path(tmp_path), FakeSession())


def test_cleanup_updates_removes_leftovers_and_tolerates_missing_dir(tmp_path):
    """Al arrancar se borran zips y versiones preparadas; sin carpeta updates/ no pasa nada."""
    updater.cleanup_updates(tmp_path)  # sin updates/: no lanza
    staged = tmp_path / "updates" / "ApiPS-2.12.0"
    staged.mkdir(parents=True)
    (staged / "ApiPS.exe").write_text("exe", encoding="utf-8")
    (tmp_path / "updates" / "ApiPS-2.12.0.zip").write_bytes(b"zip")
    updater.cleanup_updates(tmp_path)
    assert list((tmp_path / "updates").iterdir()) == []
