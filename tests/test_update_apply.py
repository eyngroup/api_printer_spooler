"""
Copyright © 2024, Iron Graterol
Licensed under the GNU Affero General Public License, version 3 or later.

Pruebas de `handy/update_apply.py` y del arranque `--apply-update` de `main.py`. Nunca lanzan procesos reales: el
arranque y la espera del proceso se inyectan.
"""

import shutil
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from handy import update_apply
from handy.update_apply import apply_update, launch_apply


def write(base: Path, relative: str, content: str) -> None:
    """Crea un archivo con contenido (y sus carpetas)."""
    path = base / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


@pytest.fixture
def env(tmp_path):
    """Instalación vieja (con datos del cliente) y versión nueva preparada."""
    install = tmp_path / "install"
    write(install, "ApiPS.exe", "OLD-EXE")
    write(install, "lib/a.pyd", "OLD-A")
    write(install, "lib/gone.pyd", "OLD-GONE")
    write(install, "config/defaults/config.json", "OLD-DEFAULT")
    write(install, "config/config.json", "CLIENT-CONFIG")
    write(install, "templates/template_ticket_simple.json", "CLIENT-TEMPLATE")
    write(install, "data/print_jobs.db", "CLIENT-DB")
    write(install, "logs/app.log", "CLIENT-LOG")
    write(install, "backups/old.db", "CLIENT-BACKUP")
    staged = install / "updates" / "ApiPS-2.12.0"
    write(staged, "ApiPS.exe", "NEW-EXE")
    write(staged, "lib/a.pyd", "NEW-A")
    write(staged, "lib/new.pyd", "NEW-NEW")
    write(staged, "config/defaults/config.json", "NEW-DEFAULT")
    return install, staged


class Launcher:
    """Registra los arranques de la aplicación instalada y lee el exe en ese momento."""

    def __init__(self):
        self.calls = []

    def __call__(self, install_dir):
        self.calls.append((Path(install_dir), (Path(install_dir) / "ApiPS.exe").read_text()))


def run(install, staged, **kwargs):
    launcher = kwargs.pop("launch", None) or Launcher()
    kwargs.setdefault("wait_process", lambda pid, timeout: True)
    code = apply_update(staged, install, 1234, launch=launcher, **kwargs)
    return code, launcher


def client_snapshot(install):
    return {
        rel: (install / rel).read_text()
        for rel in (
            "config/config.json",
            "templates/template_ticket_simple.json",
            "data/print_jobs.db",
            "logs/app.log",
            "backups/old.db",
        )
    }


def test_happy_path(env):
    install, staged = env
    before = client_snapshot(install)
    code, launcher = run(
        install, staged, old_version="2.11.0", now=lambda: datetime(2026, 1, 2, 3, 4, 5, tzinfo=timezone.utc)
    )
    assert code == 0
    assert (install / "ApiPS.exe").read_text() == "NEW-EXE"
    assert (install / "lib/a.pyd").read_text() == "NEW-A"
    assert (install / "lib/new.pyd").read_text() == "NEW-NEW"
    assert (install / "config/defaults/config.json").read_text() == "NEW-DEFAULT"
    assert client_snapshot(install) == before
    backup = install / "backups" / "app-2.11.0-20260102_030405"
    assert (backup / "ApiPS.exe").read_text() == "OLD-EXE"
    assert (backup / "lib/gone.pyd").exists()
    assert not (backup / "config/config.json").exists() and not (backup / "data").exists()
    assert launcher.calls == [(install, "NEW-EXE")]
    log = (install / "logs" / "update.log").read_text(encoding="utf-8")
    assert "Actualización aplicada correctamente" in log


def test_pid_wait_timeout_touches_nothing(env):
    install, staged = env
    code, launcher = run(install, staged, wait_process=lambda pid, timeout: False)
    assert code == 2 and launcher.calls == []
    assert (install / "ApiPS.exe").read_text() == "OLD-EXE"
    assert not any((install / "backups").glob("app-*"))
    assert "no terminó" in (install / "logs" / "update.log").read_text(encoding="utf-8")


def test_copy_failure_rolls_back(env, monkeypatch):
    install, staged = env
    before = client_snapshot(install)
    real_copy2 = shutil.copy2
    state = {"n": 0}

    def flaky(src, dst, *args, **kwargs):
        if Path(src).is_relative_to(staged):
            state["n"] += 1
            if state["n"] == 3:
                raise OSError("disco lleno")
        return real_copy2(src, dst, *args, **kwargs)

    monkeypatch.setattr(update_apply.shutil, "copy2", flaky)
    code, launcher = run(install, staged)
    assert code == 1
    assert (install / "ApiPS.exe").read_text() == "OLD-EXE"
    assert (install / "lib/a.pyd").read_text() == "OLD-A"
    assert (install / "lib/gone.pyd").read_text() == "OLD-GONE"
    assert (install / "config/defaults/config.json").read_text() == "OLD-DEFAULT"
    assert not (install / "lib/new.pyd").exists()
    assert client_snapshot(install) == before
    assert launcher.calls == [(install, "OLD-EXE")]
    assert "Falló la actualización" in (install / "logs" / "update.log").read_text(encoding="utf-8")


def test_launch_failure_rolls_back_and_relaunches_old(env):
    install, staged = env
    calls = []

    def launch(install_dir):
        calls.append((install_dir / "ApiPS.exe").read_text())
        if len(calls) == 1:
            raise OSError("no arranca")

    code, _ = run(install, staged, launch=launch)
    assert code == 1 and calls == ["NEW-EXE", "OLD-EXE"]
    assert (install / "ApiPS.exe").read_text() == "OLD-EXE"


def test_staged_runtime_file_is_never_written(env):
    install, staged = env
    write(staged, "config/config.json", "MALICIOSO")
    # _program_files ya excluye rutas de cliente: el archivo se ignora y el del cliente queda intacto
    code, _ = run(install, staged)
    assert code == 0 and (install / "config/config.json").read_text() == "CLIENT-CONFIG"


def test_backup_retention_keeps_three(env):
    install, staged = env
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    for i in range(5):
        write(install, "ApiPS.exe", f"OLD-EXE-{i}")
        code, _ = run(install, staged, now=lambda i=i: start + timedelta(days=i))
        assert code == 0
    backups = sorted(p.name for p in (install / "backups").glob("app-*"))
    assert len(backups) == 3
    assert (install / "backups" / "old.db").exists()


def test_apply_without_console(env, monkeypatch):
    install, staged = env
    monkeypatch.setattr(sys, "stdout", None)
    monkeypatch.setattr(sys, "stderr", None)
    code, _ = run(install, staged)
    assert code == 0 and (install / "logs" / "update.log").exists()


def test_launch_apply_command_and_cwd(tmp_path):
    captured = {}

    def fake_popen(command, **kwargs):
        captured["command"], captured["kwargs"] = command, kwargs
        return "proc"

    staged = tmp_path / "u" / "ApiPS-2.12.0"
    assert launch_apply(staged, tmp_path, pid=99, popen=fake_popen) == "proc"
    command = captured["command"]
    assert command[0] == str(staged / "ApiPS.exe")
    assert command[1:7] == ["--apply-update", "--install-dir", str(tmp_path), "--pid", "99", "--old-version"]
    assert captured["kwargs"]["cwd"] == str(staged) and captured["kwargs"]["close_fds"] is True
    assert captured["kwargs"]["start_new_session"] is True  # rama no Windows


def test_launch_apply_windows_flags(tmp_path, monkeypatch):
    captured = {}
    monkeypatch.setattr(update_apply.sys, "platform", "win32")
    monkeypatch.setattr(update_apply.subprocess, "DETACHED_PROCESS", 8, raising=False)
    monkeypatch.setattr(update_apply.subprocess, "CREATE_NEW_PROCESS_GROUP", 512, raising=False)
    launch_apply(tmp_path, tmp_path, pid=1, popen=lambda c, **kw: captured.update(kw))
    assert captured["creationflags"] == 8 | 512


def test_wait_process_exit_posix_dead_pid():
    import subprocess

    proc = subprocess.Popen([sys.executable, "-c", "pass"])
    proc.wait()
    assert update_apply.wait_process_exit(proc.pid, 2) is True


# ---------------------------------------------------------------- main.py


def test_main_apply_update_mode(tmp_path, monkeypatch):
    import main
    from handy import update_apply as module
    from server.config_loader import ConfigManager

    seen = {}

    def fake_apply(staged, install, pid, **kwargs):
        seen.update(staged=staged, install=install, pid=pid, kwargs=kwargs)
        return 7

    def boom(*args, **kwargs):
        raise AssertionError("no debe iniciarse la aplicación en modo --apply-update")

    monkeypatch.setattr(module, "apply_update", fake_apply)
    monkeypatch.setattr(main, "ensure_runtime_files", boom)
    monkeypatch.setattr(main, "create_app", boom)
    monkeypatch.setattr(main, "MainWindow", boom)
    monkeypatch.setattr(ConfigManager, "get_config", boom)
    monkeypatch.setattr(
        sys,
        "argv",
        ["ApiPS.exe", "--apply-update", "--install-dir", str(tmp_path), "--pid", "42", "--old-version", "2.11.0"],
    )
    with pytest.raises(SystemExit) as exit_info:
        main.main()
    assert exit_info.value.code == 7
    assert seen["install"] == tmp_path and seen["pid"] == 42 and seen["staged"] == Path(sys.executable).parent
    assert seen["kwargs"] == {"old_version": "2.11.0"}


def test_main_normal_path_does_not_apply_update(monkeypatch):
    import main

    class Stop(Exception):
        pass

    def stop(*args, **kwargs):
        raise Stop

    monkeypatch.setattr(main, "ensure_runtime_files", stop)
    monkeypatch.setattr(sys, "argv", ["ApiPS.exe"])
    with pytest.raises(Stop):
        main.main()


def test_backup_failure_relaunches_installed_app(env, monkeypatch):
    """Si no se puede respaldar, no se toca nada pero se vuelve a iniciar la app (la vieja ya terminó)."""
    install, staged = env
    before = client_snapshot(install)

    def broken_backup(*args, **kwargs):
        raise OSError("disco lleno")

    monkeypatch.setattr(update_apply, "_backup", broken_backup)
    code, launcher = run(install, staged)
    assert code == 2
    assert [path for path, _exe in launcher.calls] == [install]  # se inicia la versión instalada, sin cambios
    assert client_snapshot(install) == before
