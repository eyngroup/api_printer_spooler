"""
Configuración común de pytest.

Red de seguridad: ningún test puede abrir un puerto serial real. Las impresoras fiscales conectadas a la
máquina de desarrollo son equipos fiscalizados en producción; un test que llegue al hardware podría
enviarles comandos reales.
"""

import pytest
import serial

from handy.runtime_files import ensure_runtime_files

# Los tests no dependen de los archivos de runtime locales del desarrollador: se crean desde los defaults si faltan.
ensure_runtime_files()


@pytest.fixture(autouse=True)
def forbid_real_serial_ports(monkeypatch: pytest.MonkeyPatch):
    """Hace fallar cualquier intento de abrir un puerto serial real durante los tests."""

    def _forbidden(*args, **kwargs):
        raise serial.SerialException("Acceso a puertos seriales reales prohibido en los tests")

    monkeypatch.setattr(serial, "Serial", _forbidden)
