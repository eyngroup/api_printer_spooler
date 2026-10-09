#!/usr/bin/env python
"""
Copyright © 2024, Iron Graterol
Licensed under the GNU Affero General Public License, version 3 or later.

Monitor fiscal de solo lectura: lee la máquina HKA (S1, S3, S4, S5, SV y U0X), interpreta las respuestas
con el orden de campos verificado en una HKA80 (flag 63 = 00) y entrega una "foto" (snapshot) con caché,
sin imprimir nada y sin tocar la máquina mientras haya una impresión en curso.
"""

import copy
import logging
import threading
import time
from datetime import datetime
from typing import Any

from server.config_loader import get_payment_labels

from . import job_store
from .printer_manager import PrinterManager

logger = logging.getLogger(__name__)

CACHE_SECONDS = 60  # Vigencia de la lectura: dentro de este lapso no se vuelve a leer la máquina
MIN_REFRESH_SECONDS = 10  # Aun forzando, no se lee más seguido que esto

# Cantidad de campos de U0X con flag 63 = 00 (si llegan más, se ignoran los extra)
_U0X_FIELDS = 30
# Los acumuladores de pago desde este código son en divisa
_DIVISA_FROM_CODE = 20


def _amount(raw: str, decimals: int = 2) -> float:
    """
    Convierte un campo numérico de la máquina (dígitos con decimales implícitos) a float.
    Args:
        raw: Texto de dígitos, p. ej. "0000119844450" (11 enteros + 2 decimales)
        decimals: Cantidad de decimales implícitos
    Returns:
        float: Monto con 2 decimales
    """
    return round(int(raw.strip()) / (10**decimals), 2)


def _date(raw: str) -> str:
    """
    Convierte una fecha AAMMDD de la máquina a AAAA-MM-DD.
    Args:
        raw: Fecha en formato AAMMDD (YYMMDD)
    Returns:
        str: Fecha ISO, o cadena vacía si el campo no es una fecha válida
    """
    try:
        return datetime.strptime(raw.strip(), "%y%m%d").strftime("%Y-%m-%d")  # noqa: DTZ007 - fecha local de la máquina
    except ValueError:
        return ""


def _time(raw: str) -> str:
    """
    Convierte una hora HHMM de la máquina a HH:MM.
    Args:
        raw: Hora en formato HHMM
    Returns:
        str: Hora "HH:MM", o cadena vacía si el campo no es válido
    """
    raw = raw.strip()
    return f"{raw[:2]}:{raw[2:4]}" if len(raw) >= 4 and raw[:4].isdigit() else ""


def _lines(source: str, command: str | None = None) -> list[str]:
    """
    Separa el texto de una respuesta en líneas no vacías, quitando el eco del comando al inicio.
    Args:
        source: Texto crudo de la respuesta
        command: Comando cuyo eco se elimina de la primera línea (S4, S5, ...)
    Returns:
        list[str]: Líneas con contenido (sin strip de ceros: solo espacios de los extremos)
    """
    lines = []
    for i, line in enumerate(source.split("\n")):
        clean = line.strip()
        if i == 0 and command and clean.startswith(command):
            clean = clean[len(command) :]
        if clean:
            lines.append(clean)
    return lines


def _tax_block(fields: list[str]) -> dict[str, Any]:
    """
    Interpreta 7 montos de U0X: exento y (base, impuesto) de las alícuotas 1 a 3.
    Args:
        fields: 7 campos de 13 dígitos (11 enteros + 2 decimales)
    Returns:
        dict: {"exento", "rates": [{"rate_index", "base", "tax"}], "total"}
    """
    values = [_amount(f) for f in fields]
    exento = values[0]
    rates = [{"rate_index": n, "base": values[2 * n - 1], "tax": values[2 * n]} for n in (1, 2, 3)]
    total = round(exento + sum(r["base"] + r["tax"] for r in rates), 2)
    return {"exento": exento, "rates": rates, "total": total}


def parse_x_report(text: str) -> dict[str, Any]:
    """
    Interpreta la respuesta de U0X (acumulados del día antes del cierre Z) con el orden verificado.
    Orden: próximo Z, fecha y hora del último Z, última factura (número, fecha, hora), última nota de
    débito, última nota de crédito, último documento no fiscal y 21 montos (ventas, débito, crédito;
    cada bloque: exento, base1, imp1, base2, imp2, base3, imp3). Campos adicionales se ignoran.
    Args:
        text: Texto crudo de U0X
    Returns:
        dict: Contadores y acumulados interpretados
    Raises:
        ValueError: Si llegan menos de 30 campos
    """
    f = _lines(text)
    if len(f) < _U0X_FIELDS:
        raise ValueError(f"U0X incompleto: {len(f)} campos (se esperaban {_U0X_FIELDS})")
    return {
        "next_z": f[0],
        "last_z_date": _date(f[1]),
        "last_z_time": _time(f[2]),
        "last_invoice": {"number": f[3], "date": _date(f[4]), "time": _time(f[5])},
        "last_debit_note": f[6],
        "last_credit_note": f[7],
        "last_non_fiscal": f[8],
        "sales": _tax_block(f[9:16]),
        "debit": _tax_block(f[16:23]),
        "credit": _tax_block(f[23:30]),
    }


def parse_s4(source: str | dict[str, str]) -> list[dict[str, Any]]:
    """
    Interpreta los 24 acumuladores de formas de pago de S4 (los códigos 20 a 24 son en divisa).
    Args:
        source: Texto crudo de S4 o el diccionario {"01": "...", ...} del controlador
    Returns:
        list[dict]: [{"code": "01", "amount": float, "divisa": bool}, ...]
    """
    values = list(source.values()) if isinstance(source, dict) else _lines(source, "S4")
    return [
        {"code": f"{i:02d}", "amount": _amount(raw), "divisa": i >= _DIVISA_FROM_CODE}
        for i, raw in enumerate(values[:24], start=1)
    ]


def apply_payment_labels(snapshot: dict[str, Any], labels: dict[str, str]) -> dict[str, Any]:
    """
    Agrega "label" a cada pago del snapshot (cadena vacía si el código no tiene etiqueta). Modifica el snapshot.
    Args:
        snapshot: Snapshot con la lista "payments"
        labels: Etiquetas por código ("01".."24")
    Returns:
        dict: El mismo snapshot
    """
    for payment in snapshot.get("payments") or []:
        payment["label"] = labels.get(payment.get("code", ""), "")
    return snapshot


def parse_s5(source: str | dict[str, str]) -> dict[str, Any]:
    """
    Interpreta S5 (memoria de auditoría y datos de la máquina).
    Args:
        source: Texto crudo de S5 o el diccionario del controlador (get_s5)
    Returns:
        dict: rif, serial, audit_memory_number, capacity_mb, free_mb, documents
    """
    v = list(source.values()) if isinstance(source, dict) else _lines(source, "S5")
    v = [str(x).strip() for x in v] + [""] * 6
    return {
        "rif": v[0],
        "serial": v[1],
        "audit_memory_number": v[2],
        "capacity_mb": int(v[3]) if v[3].isdigit() else None,
        "free_mb": int(v[4]) if v[4].isdigit() else None,
        "documents": int(v[5]) if v[5].isdigit() else None,
    }


# Etiquetas que usa controllers/pfhka.py get_s3 para cada código de tipo de tasa (según la Tabla 19 del manual)
CONTROLLER_RATE_LABEL_TO_CODE = {"Percibido": "0", "Excluido": "1", "Incluido": "2"}


def parse_s3(source: str | dict[str, str]) -> dict[str, Any]:
    """
    Interpreta S3: alícuotas (tipo y porcentaje) y los flags distintos de cero.
    Args:
        source: Texto crudo de S3 o el diccionario de get_s3 (con flag_N para los flags leídos)
    Returns:
        dict: {"rates": [{"name", "type", "percent"}], "flags": {"21": "01", ...}} (solo flags != "00")
    """
    # El manual se contradice (Tabla 19: 1=excluida, 2=incluida; Tabla 55 de S3: 1=incluido, 2=excluido).
    # Verificado en HKA80 (tasas tipo 2): precio 1,00 al 31 % -> base 1,00 e impuesto 0,31, es decir, el IVA se
    # suma al precio: tipo 2 = Excluido. El controlador (get_s3) etiqueta según la Tabla 19; aquí se usa lo real.
    types = {"0": "Percibido", "1": "Incluido", "2": "Excluido"}
    names = ["General", "Reducido", "Adicional", "IGTF"]
    rates: list[dict[str, Any]] = []
    flags: dict[str, str] = {}
    if isinstance(source, dict):
        for key, value in source.items():
            if key.startswith("flag_"):
                if value != "00":
                    flags[key[5:]] = value
            elif "[" in key:
                name, _, kind = key.partition(" [")
                # Etiqueta del controlador (Tabla 19) -> código original -> tipo verificado en la máquina
                code = CONTROLLER_RATE_LABEL_TO_CODE.get(kind.rstrip("]"), "")
                rates.append({"name": name, "type": types.get(code, "Desconocido"), "percent": float(value)})
        return {"rates": rates, "flags": flags}
    lines = _lines(source, "S3")
    for i, line in enumerate(lines[:-1][:4]):
        rates.append(
            {"name": names[i], "type": types.get(line[0], "Desconocido"), "percent": _amount(line[1:5], decimals=2)}
        )
    chain = lines[-1] if len(lines) > 1 else ""
    for n in range(len(chain) // 2):
        if chain[2 * n : 2 * n + 2] != "00":
            flags[str(n)] = chain[2 * n : 2 * n + 2]
    return {"rates": rates, "flags": flags}


def machine_datetime(s1: dict[str, str]) -> datetime | None:
    """
    Arma la fecha y hora de la máquina a partir de S1 (fecha DDMMAA, hora HHMMSS).
    Args:
        s1: Diccionario de get_s1
    Returns:
        datetime | None: Fecha y hora local de la máquina, o None si no son interpretables
    """
    try:
        return datetime.strptime(f"{s1['fecha_impresora'].strip()}{s1['hora_impresora'].strip()}", "%d%m%y%H%M%S")  # noqa: DTZ007 - hora local de la máquina
    except (KeyError, ValueError):
        return None


def build_snapshot(
    raw: dict[str, Any], now: datetime | None = None, payment_labels: dict[str, str] | None = None
) -> dict[str, Any]:
    """
    Construye el snapshot a partir de las lecturas crudas de la máquina y calcula los campos derivados:
    venta neta (ventas - notas de crédito + notas de débito), total de pagos locales, total en divisa y
    desfase de hora (hora de la máquina - hora del servidor, en segundos).
    Args:
        raw: Lecturas crudas: s1, s3, s4, s5, sv (diccionarios del controlador) y u0x (texto)
        now: Hora local del servidor (solo para pruebas)
        payment_labels: Etiquetas de los medios de pago por código (si es None, quedan sin etiqueta)
    Returns:
        dict: Snapshot con machine, counters, pre_z, payments, payments_total y divisa_total
    """
    now = now or datetime.now()  # noqa: DTZ005 - hora local, comparable con la de la máquina
    s1 = raw.get("s1") or {}
    x = parse_x_report(raw["u0x"])
    s3 = parse_s3(raw.get("s3") or {})
    s5 = parse_s5(raw.get("s5") or {})
    payments = parse_s4(raw.get("s4") or {})

    machine_dt = machine_datetime(s1)
    drift = round((machine_dt - now).total_seconds()) if machine_dt else None
    sv = raw.get("sv") or {}
    net = round(x["sales"]["total"] - x["credit"]["total"] + x["debit"]["total"], 2)

    snapshot = {
        "available": True,
        "read_at": now.isoformat(timespec="seconds"),
        "stale": False,
        "machine": {
            "model": sv.get("modelo", ""),
            "country": sv.get("pais", ""),
            "serial": s5["serial"],
            "rif": s5["rif"],
            "audit_memory": {
                "number": s5["audit_memory_number"],
                "capacity_mb": s5["capacity_mb"],
                "free_mb": s5["free_mb"],
                "documents": s5["documents"],
            },
            "datetime": machine_dt.isoformat(timespec="seconds") if machine_dt else "",
            "time_drift_seconds": drift,
            "flags": s3["flags"],
            "rates": s3["rates"],
        },
        "counters": {
            "next_z": x["next_z"],
            "last_z_date": x["last_z_date"],
            "last_z_time": x["last_z_time"],
            "last_invoice": x["last_invoice"],
            "last_debit_note": x["last_debit_note"],
            "last_credit_note": x["last_credit_note"],
            "last_non_fiscal": x["last_non_fiscal"],
            "today": {
                "invoices": s1.get("facturas_dia", ""),
                "debit_notes": s1.get("notas_debito_dia", ""),
                "credit_notes": s1.get("notas_credito_dia", ""),
                "non_fiscal": s1.get("docs_no_fiscales_dia", ""),
            },
            "z_closures": s1.get("contador_cierres_z", ""),
            "memory_reports": s1.get("contador_reportes_memoria", ""),
        },
        "pre_z": {"sales": x["sales"], "debit": x["debit"], "credit": x["credit"], "net_sales": net},
        "payments": payments,
        "payments_total": round(sum(p["amount"] for p in payments if not p["divisa"]), 2),
        "divisa_total": round(sum(p["amount"] for p in payments if p["divisa"]), 2),
    }
    return apply_payment_labels(snapshot, payment_labels or {})


class FiscalMonitor:
    """Servicio con caché de clase que entrega el snapshot fiscal sin leer la máquina más de lo necesario."""

    _lock = threading.Lock()
    _snapshot: dict[str, Any] | None = None
    _read_ts: float = 0.0  # Marca monotónica de la última lectura exitosa

    @classmethod
    def reset(cls) -> None:
        """Vacía la caché (uso en pruebas)."""
        with cls._lock:
            cls._snapshot = None
            cls._read_ts = 0.0

    @classmethod
    def _stale_copy(cls, error: str | None = None) -> dict[str, Any] | None:
        """
        Copia de la última lectura buena marcada como obsoleta.
        Args:
            error: Mensaje opcional a incluir en la copia
        Returns:
            dict | None: Copia con stale=True, o None si nunca hubo una lectura buena
        """
        if cls._snapshot is None:
            return None
        snap = copy.deepcopy(cls._snapshot)
        snap["stale"] = True
        if error:
            snap["error"] = error
        return snap

    @classmethod
    def get_snapshot(cls, printers_config: dict[str, Any], force: bool = False) -> dict[str, Any]:
        """
        Devuelve el snapshot fiscal con las etiquetas de pago vigentes de la configuración (se aplican en cada
        respuesta, así un cambio de etiquetas se ve sin esperar a que venza la caché). Nunca lanza excepciones.
        Args:
            printers_config: Sección "printers" de la configuración
            force: True para pedir una lectura nueva (sujeta al mínimo entre lecturas)
        Returns:
            dict: Snapshot, o {"available": False, "reason": ...}
        """
        snapshot = cls._get_snapshot(printers_config, force)
        if snapshot.get("available"):
            apply_payment_labels(snapshot, get_payment_labels({"printers": printers_config or {}}))
        return snapshot

    @classmethod
    def _get_snapshot(cls, printers_config: dict[str, Any], force: bool = False) -> dict[str, Any]:
        """
        Devuelve el snapshot fiscal, leyendo la máquina solo si la caché venció (60 s) o si se fuerza
        (nunca más de una vez cada 10 s). Nunca lee durante una impresión. Nunca lanza excepciones.
        Args:
            printers_config: Sección "printers" de la configuración
            force: True para pedir una lectura nueva (sujeta al mínimo entre lecturas)
        Returns:
            dict: Snapshot, o {"available": False, "reason": ...}
        """
        try:
            fiscal = (printers_config or {}).get("fiscal", {}) or {}
            name = str(fiscal.get("fiscal_name", "")).strip().lower()
            if not fiscal.get("fiscal_enabled", False) or name != "tfhka":
                return {"available": False, "reason": "Monitor fiscal disponible solo para impresoras TFHKA"}

            with cls._lock:
                age = time.monotonic() - cls._read_ts
                if cls._snapshot is not None and age < (MIN_REFRESH_SECONDS if force else CACHE_SECONDS):
                    return copy.deepcopy(cls._snapshot)

                if job_store.has_processing_jobs():
                    return cls._stale_copy() or {"available": False, "reason": "Impresión en curso"}

                raw = PrinterManager.read_monitor_data("tfhka", fiscal, job_store.has_processing_jobs)
                if raw and raw.get("busy"):
                    return cls._stale_copy() or {"available": False, "reason": "Impresión en curso"}
                if not raw:
                    message = "No se pudo leer la máquina fiscal"
                    return cls._stale_copy(message) or {"available": False, "reason": message}

                cls._snapshot = build_snapshot(raw, payment_labels=get_payment_labels({"printers": printers_config}))
                cls._read_ts = time.monotonic()
                return copy.deepcopy(cls._snapshot)
        except Exception as e:  # noqa: BLE001 - nunca debe lanzar: el monitor es informativo
            logger.warning("Error en el monitor fiscal: %s", e)
            message = f"Error leyendo el monitor fiscal: {e}"
            return cls._stale_copy(message) or {"available": False, "reason": message}
