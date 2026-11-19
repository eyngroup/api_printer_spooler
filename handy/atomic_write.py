#!/usr/bin/env python
"""
Copyright © 2024, Iron Graterol
Licensed under the GNU Affero General Public License, version 3 or later.

Escritura atómica de archivos JSON: evita que un corte de energía a mitad de la escritura deje el archivo
truncado (la aplicación no podría volver a arrancar con una configuración corrupta).
"""

import json
import os
from typing import Any


def write_json_atomic(path: str, data: Any, indent: int = 4) -> None:
    """
    Escribe `data` como JSON en `path` de forma atómica.

    Se escribe primero en `path + ".tmp"` (mismo directorio, para que el reemplazo sea atómico), se fuerza a
    disco con flush + fsync y se reemplaza el destino con `os.replace`. Ante cualquier falla se elimina el
    temporal, el archivo original queda intacto y se relanza la excepción.
    Args:
        path: Ruta del archivo destino.
        data: Datos serializables a JSON.
        indent: Sangría del JSON escrito.
    """
    path = os.fspath(path)
    tmp_path = path + ".tmp"
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, path)
    except BaseException:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        raise
