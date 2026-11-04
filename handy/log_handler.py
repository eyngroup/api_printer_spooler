#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright © 2024, Iron Graterol
Licensed under the GNU Affero General Public License, version 3 or later.

Handler de logging diario que nunca renombra ni elimina el archivo vigente.

El archivo del día se llama ``<base_name>-YYYYMMDD.log``. Al cambiar la fecha local se abre el archivo
del nuevo día (sin rotación por renombrado, que en Windows puede fallar y dejar el log mudo).
"""

import logging
import os
import sys
from collections.abc import Callable
from datetime import datetime

ERROR_FILE_NAME = "logging_error.txt"


def current_log_path(log_dir: str, base_name: str, now: datetime | None = None) -> str:
    """Devuelve la ruta del log del día: ``<log_dir>/<base_name>-YYYYMMDD.log``."""
    now = now or datetime.now()  # noqa: DTZ005 - hora local, igual que el resto de la aplicación
    return os.path.join(log_dir, f"{base_name}-{now.strftime('%Y%m%d')}.log")


class DailyFileHandler(logging.Handler):
    """Escribe en el log del día en modo append y cambia de archivo al cambiar la fecha, sin renombrar."""

    def __init__(
        self,
        log_dir: str,
        base_name: str,
        encoding: str = "utf-8",
        on_rollover: Callable[[], None] | None = None,
    ) -> None:
        """Crea el handler; el archivo se abre de forma perezosa en el primer registro."""
        super().__init__()
        self.log_dir = log_dir
        self.base_name = base_name
        self.encoding = encoding
        self.on_rollover = on_rollover
        self.stream = None
        self._stream_day: str | None = None

    @staticmethod
    def _today() -> str:
        """Fecha local actual como ``YYYYMMDD`` (punto único de reloj, reemplazable en pruebas)."""
        return datetime.now().strftime("%Y%m%d")  # noqa: DTZ005 - fecha local del equipo

    def _path_for(self, day: str) -> str:
        """Ruta del archivo de log para el día indicado (``YYYYMMDD``)."""
        return os.path.join(self.log_dir, f"{self.base_name}-{day}.log")

    def _close_stream(self) -> None:
        """Cierra el stream actual ignorando cualquier error."""
        stream, self.stream = self.stream, None
        if stream is not None:
            try:
                stream.close()
            except Exception:  # noqa: BLE001, S110 - cerrar el stream jamás debe fallar hacia afuera
                pass

    def _ensure_stream(self) -> None:
        """Abre (o cambia) el archivo del día; si falla, el stream queda cerrado para reintentar en el próximo registro."""
        today = self._today()
        if self.stream is not None and self._stream_day == today and os.path.exists(self._path_for(today)):
            return
        changed_day = self._stream_day is not None and self._stream_day != today
        self._close_stream()
        os.makedirs(self.log_dir, exist_ok=True)
        self.stream = open(self._path_for(today), "a", encoding=self.encoding)  # noqa: SIM115 - stream de larga vida
        self._stream_day = today
        if changed_day and self.on_rollover is not None:
            try:
                self.on_rollover()
            except Exception:  # noqa: BLE001, S110 - la limpieza no debe afectar al logging
                pass

    def emit(self, record: logging.LogRecord) -> None:
        """Escribe el registro y hace flush; ante cualquier fallo delega en ``handleError``."""
        try:
            self._ensure_stream()
            self.stream.write(self.format(record) + "\n")
            self.stream.flush()
        except Exception:  # noqa: BLE001 - se anota en logging_error.txt y se reintenta en el próximo registro
            self._close_stream()
            self.handleError(record)

    def handleError(self, record: logging.LogRecord) -> None:
        """Anota el error en ``logging_error.txt`` (la GUI no tiene stderr) sin propagar ninguna excepción."""
        try:
            exc_type, exc, _ = sys.exc_info()
            stamp = datetime.now().isoformat(timespec="seconds")  # noqa: DTZ005 - hora local
            line = f"{stamp} | {exc_type.__name__ if exc_type else '-'}: {exc}\n"
            os.makedirs(self.log_dir, exist_ok=True)
            with open(os.path.join(self.log_dir, ERROR_FILE_NAME), "a", encoding="utf-8") as f:
                f.write(line)
        except Exception:  # noqa: BLE001, S110 - último recurso: no hay dónde más informar
            pass
        try:
            if sys.stderr is not None:
                super().handleError(record)
        except Exception:  # noqa: BLE001, S110 - stderr puede no existir en el build GUI
            pass

    def close(self) -> None:
        """Cierra el stream y el handler."""
        self.acquire()
        try:
            self._close_stream()
        finally:
            self.release()
        super().close()
