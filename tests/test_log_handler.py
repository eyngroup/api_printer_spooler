#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright © 2024, Iron Graterol
Licensed under the GNU Affero General Public License, version 3 or later.

Pruebas del handler de log diario y de la limpieza de logs antiguos.
"""

import logging
import os
import pathlib
import shutil
from datetime import datetime, timedelta

import pytest

from handy.log_handler import DailyFileHandler, current_log_path
from main import cleanup_old_logs


@pytest.fixture
def make_logger(tmp_path):
    """Crea un logger aislado (sin propagar) con un DailyFileHandler y lo limpia al terminar."""
    created = []

    def _make(**kwargs):
        handler = DailyFileHandler(str(tmp_path / "logs"), "printer_spooler", **kwargs)
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger = logging.getLogger(f"test_daily_{len(created)}_{id(handler)}")
        logger.setLevel(logging.INFO)
        logger.propagate = False
        logger.addHandler(handler)
        created.append((logger, handler))
        return logger, handler

    yield _make
    for logger, handler in created:
        logger.removeHandler(handler)
        handler.close()


def test_writes_to_todays_file(make_logger, tmp_path):
    """Un registro queda escrito en el archivo del día."""
    logger, _handler = make_logger()
    logger.info("hola")
    path = current_log_path(str(tmp_path / "logs"), "printer_spooler")
    assert pathlib.Path(path).read_text(encoding="utf-8") == "hola\n"


def test_switches_file_on_date_change(make_logger, tmp_path, monkeypatch):
    """Al cambiar la fecha se escribe en el archivo nuevo, el anterior queda intacto y se llama on_rollover."""
    calls = []
    logger, _handler = make_logger(on_rollover=lambda: calls.append(1))
    days = iter(["20260101", "20260102"])
    monkeypatch.setattr(DailyFileHandler, "_today", staticmethod(lambda: next(days)))
    logger.info("uno")
    logger.info("dos")
    log_dir = tmp_path / "logs"
    assert (log_dir / "printer_spooler-20260101.log").read_text(encoding="utf-8") == "uno\n"
    assert (log_dir / "printer_spooler-20260102.log").read_text(encoding="utf-8") == "dos\n"
    assert calls == [1]


def test_recreates_removed_directory(make_logger, tmp_path):
    """Si se borra el directorio entre registros, se recrea y se sigue escribiendo sin excepciones."""
    logger, _handler = make_logger()
    logger.info("antes")
    shutil.rmtree(tmp_path / "logs")
    logger.info("despues")
    path = current_log_path(str(tmp_path / "logs"), "printer_spooler")
    assert "despues" in pathlib.Path(path).read_text(encoding="utf-8")


def test_handle_error_appends_to_error_file(make_logger, tmp_path):
    """handleError anota el fallo en logging_error.txt."""
    _logger, handler = make_logger()
    try:
        raise OSError("disco lleno")
    except OSError:
        handler.handleError(logging.LogRecord("x", logging.ERROR, "f", 1, "m", None, None))
    content = (tmp_path / "logs" / "logging_error.txt").read_text(encoding="utf-8")
    assert "OSError" in content and "disco lleno" in content


def test_cleanup_old_logs(tmp_path):
    """Elimina el log de hace más de max_days y conserva el de hoy."""
    today = datetime.now()  # noqa: DTZ005 - fecha local, como el handler
    old = tmp_path / "printer_spooler-20260917.log"
    rotated = tmp_path / "printer_spooler-20260918.log.2026-09-18"
    recent = tmp_path / f"printer_spooler-{(today - timedelta(days=1)).strftime('%Y%m%d')}.log"
    current = tmp_path / os.path.basename(current_log_path(str(tmp_path), "printer_spooler"))
    for f in (old, rotated, recent, current):
        f.write_text("x")
    cleanup_old_logs(str(tmp_path), 5)
    assert not old.exists() and not rotated.exists()
    assert recent.exists() and current.exists()
