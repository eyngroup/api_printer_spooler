#!/usr/bin/env python
"""
Copyright © 2024, Iron Graterol
Licensed under the GNU Affero General Public License, version 3 or later.

Idempotency store for print jobs backed by SQLite.
Prevents duplicate fiscal prints when Odoo sends repeated requests.
"""

import json
import logging
import sqlite3
import threading
from collections.abc import Callable, Iterator
from contextlib import closing, contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any

from handy.tools import get_base_path

logger = logging.getLogger(__name__)

_DB_PATH = Path(get_base_path()) / "data" / "print_jobs.db"

# Segundos tras los cuales un trabajo en 'processing' se considera huérfano (el proceso murió a mitad de la
# impresión). El timeout de Odoo es de 90 s y una impresión HKA toma ~10 s, por lo que 180 s no choca con
# una impresión legítima en curso.
STALE_PROCESSING_SECONDS = 180

# One process-level lock — fiscal printer is a singleton anyway
_lock = threading.Lock()

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS print_jobs (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id    TEXT    NOT NULL,
    operation_type TEXT    NOT NULL,
    status         TEXT    NOT NULL DEFAULT 'processing',
    response       TEXT,
    error_message  TEXT,
    created_at     TEXT    NOT NULL,
    updated_at     TEXT    NOT NULL,
    counter_before TEXT,
    UNIQUE (document_id, operation_type)
)
"""

# Contadores emulados de las impresoras no fiscales (una fila por impresora: "matrix", "ticket").
# Reemplazan a la sección "counter" de los templates JSON, que se podía perder al guardar la configuración.
_CREATE_COUNTERS = """
CREATE TABLE IF NOT EXISTS counters (
    printer_key      TEXT PRIMARY KEY,
    document_date    TEXT NOT NULL,
    document_invoice TEXT NOT NULL,
    document_credit  TEXT NOT NULL,
    document_debit   TEXT NOT NULL,
    document_note    TEXT NOT NULL,
    machine_report   TEXT NOT NULL,
    machine_serial   TEXT NOT NULL,
    updated_at       TEXT NOT NULL
)
"""

# Columnas de documento y de máquina de la tabla counters (sin la clave ni updated_at)
COUNTER_FIELDS = (
    "document_date",
    "document_invoice",
    "document_credit",
    "document_debit",
    "document_note",
    "machine_report",
    "machine_serial",
)
_COUNTER_NUMBER_FIELDS = ("document_invoice", "document_credit", "document_debit", "document_note")

_CREATE_INDEX = "CREATE INDEX IF NOT EXISTS idx_doc_op ON print_jobs (document_id, operation_type)"


@contextmanager
def _connect() -> Iterator[sqlite3.Connection]:
    """
    Abre una conexión a la base de trabajos como context manager.

    Hace commit al salir sin errores, rollback ante una excepción y SIEMPRE cierra
    la conexión. El `with sqlite3.connect()` nativo solo gestiona la transacción y deja
    la conexión abierta, lo que en Windows mantiene bloqueado el archivo .db.
    """
    with closing(sqlite3.connect(str(_DB_PATH), timeout=5.0)) as conn:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=3000")
        conn.row_factory = sqlite3.Row
        with conn:
            yield conn


def _ensure_schema(conn: sqlite3.Connection) -> None:
    """
    Crea la tabla y el índice si no existen y migra bases creadas con el esquema anterior.

    Las bases de producción ya existen: si falta la columna counter_before (contador de la máquina
    antes de imprimir) se agrega con ALTER TABLE, sin perder los trabajos registrados.
    Args:
        conn: Conexión abierta a la base de trabajos
    """
    conn.execute(_CREATE_TABLE)
    conn.execute(_CREATE_INDEX)
    conn.execute(_CREATE_COUNTERS)
    columns = {row["name"] for row in conn.execute("PRAGMA table_info(print_jobs)").fetchall()}
    if "counter_before" not in columns:
        conn.execute("ALTER TABLE print_jobs ADD COLUMN counter_before TEXT")
        logger.info("Job store: columna counter_before agregada a una base existente")


def init_db() -> None:
    """Create the jobs table and index if they do not exist (y migra el esquema anterior)."""
    _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with _connect() as conn:
        _ensure_schema(conn)
    logger.info("Job store inicializado: %s", _DB_PATH)


_ORPHAN_MESSAGE = "Trabajo huérfano: el proceso se interrumpió durante la impresión"


def _now_iso() -> str:
    """
    Devuelve la hora local actual (sin zona horaria, como el resto del módulo) en formato ISO a segundos.
    Returns:
        str: Marca de tiempo ISO local
    """
    return datetime.now().isoformat(timespec="seconds")  # noqa: DTZ005 - hora local, como el resto del job store


def _is_stale(updated_at: str) -> bool:
    """
    Indica si un trabajo en 'processing' lleva más de STALE_PROCESSING_SECONDS sin actualizarse.
    Args:
        updated_at: Marca de tiempo ISO local (sin zona horaria) de la última actualización
    Returns:
        bool: True si el trabajo es huérfano; False si es reciente o la fecha no es interpretable
    """
    try:
        age = (datetime.fromisoformat(_now_iso()) - datetime.fromisoformat(updated_at)).total_seconds()
    except (TypeError, ValueError):
        return False
    return age > STALE_PROCESSING_SECONDS


def acquire_job(document_id: str, operation_type: str) -> tuple[str, dict[str, Any] | None]:
    """
    Atomically claim a print job slot.

    Returns a (result, payload) tuple:
        ('new',       None)           — first request, proceed
        ('retry',     None)           — previous attempt failed, proceed
        ('duplicate', cached_dict)    — already completed, return cached
        ('in_progress', None)         — currently processing, return 409
        ('unknown',   None)           — no se sabe si el documento se emitió (hay que conciliar con la máquina)

    Un trabajo en 'unknown' no se modifica. Un trabajo en 'processing' cuyo updated_at supera
    STALE_PROCESSING_SECONDS se considera huérfano y pasa a 'unknown'.
    """
    now = datetime.now().isoformat(timespec="seconds")

    with _lock, _connect() as conn:
        row = conn.execute(
            "SELECT status, response, updated_at FROM print_jobs WHERE document_id=? AND operation_type=?",
            (document_id, operation_type),
        ).fetchone()

        if row is None:
            conn.execute(
                "INSERT INTO print_jobs (document_id, operation_type, status, created_at, updated_at)"
                " VALUES (?, ?, 'processing', ?, ?)",
                (document_id, operation_type, now, now),
            )
            logger.debug("Job store: nuevo trabajo %s/%s", document_id, operation_type)
            return "new", None

        existing = dict(row)

        if existing["status"] == "completed":
            cached = json.loads(existing["response"])
            logger.info(
                "Job store: documento %s/%s ya procesado — retornando caché",
                document_id,
                operation_type,
            )
            logger.debug("Job store: caché retornado %s/%s — %s", document_id, operation_type, cached)
            return "duplicate", cached

        if existing["status"] == "unknown":
            logger.warning("Job store: documento %s/%s con resultado desconocido", document_id, operation_type)
            return "unknown", None

        if existing["status"] == "processing":
            if _is_stale(existing["updated_at"]):
                conn.execute(
                    "UPDATE print_jobs SET status='unknown', error_message=?, updated_at=?"
                    " WHERE document_id=? AND operation_type=?",
                    (_ORPHAN_MESSAGE, now, document_id, operation_type),
                )
                logger.warning(
                    "Job store: trabajo huérfano %s/%s marcado como desconocido", document_id, operation_type
                )
                return "unknown", None
            logger.warning(
                "Job store: documento %s/%s en proceso — solicitud duplicada rechazada",
                document_id,
                operation_type,
            )
            return "in_progress", None

        # status == 'failed' — allow retry
        conn.execute(
            "UPDATE print_jobs SET status='processing', error_message=NULL, response=NULL, updated_at=?"
            " WHERE document_id=? AND operation_type=?",
            (now, document_id, operation_type),
        )
        logger.info(
            "Job store: reintento autorizado para %s/%s",
            document_id,
            operation_type,
        )
        return "retry", None


def complete_job(document_id: str, operation_type: str, response: dict[str, Any]) -> None:
    """Mark a job as successfully completed and persist the response."""
    now = datetime.now().isoformat(timespec="seconds")
    with _lock, _connect() as conn:
        conn.execute(
            "UPDATE print_jobs SET status='completed', response=?, updated_at=?"
            " WHERE document_id=? AND operation_type=?",
            (json.dumps(response), now, document_id, operation_type),
        )
    logger.debug("Job store: completado %s/%s", document_id, operation_type)


def fail_job(document_id: str, operation_type: str, error_message: str) -> None:
    """Mark a job as failed. The next request for the same document will be retried."""
    now = datetime.now().isoformat(timespec="seconds")
    with _lock, _connect() as conn:
        conn.execute(
            "UPDATE print_jobs SET status='failed', error_message=?, updated_at=?"
            " WHERE document_id=? AND operation_type=?",
            (error_message, now, document_id, operation_type),
        )
    logger.debug("Job store: fallido %s/%s — %s", document_id, operation_type, error_message)


def set_counter_before(document_id: str, operation_type: str, value: str) -> None:
    """
    Guarda el último número fiscal de la máquina leído justo antes de imprimir.
    Args:
        document_id: Clave de idempotencia del documento
        operation_type: Tipo de operación
        value: Último número del tipo de documento según la máquina (S1)
    """
    with _lock, _connect() as conn:
        conn.execute(
            "UPDATE print_jobs SET counter_before=? WHERE document_id=? AND operation_type=?",
            (value, document_id, operation_type),
        )
    logger.debug("Job store: contador previo %s para %s/%s", value, document_id, operation_type)


def mark_unknown(document_id: str, operation_type: str, error_message: str) -> None:
    """
    Marca un trabajo como 'unknown': no se pudo determinar si el documento se emitió en la máquina.
    Args:
        document_id: Clave de idempotencia del documento
        operation_type: Tipo de operación
        error_message: Motivo de la incertidumbre
    """
    now = _now_iso()
    with _lock, _connect() as conn:
        conn.execute(
            "UPDATE print_jobs SET status='unknown', error_message=?, updated_at=?"
            " WHERE document_id=? AND operation_type=?",
            (error_message, now, document_id, operation_type),
        )
    logger.warning("Job store: resultado desconocido %s/%s — %s", document_id, operation_type, error_message)


def get_job(document_id: str, operation_type: str) -> dict[str, Any] | None:
    """
    Lee un trabajo registrado.
    Args:
        document_id: Clave de idempotencia del documento
        operation_type: Tipo de operación
    Returns:
        dict | None: status, counter_before, created_at, updated_at, error_message y response
        (ya decodificada), o None si el trabajo no existe
    """
    with _lock, _connect() as conn:
        row = conn.execute(
            "SELECT status, counter_before, created_at, updated_at, error_message, response"
            " FROM print_jobs WHERE document_id=? AND operation_type=?",
            (document_id, operation_type),
        ).fetchone()
    if row is None:
        return None
    job = dict(row)
    job["response"] = json.loads(job["response"]) if job["response"] else None
    return job


def completed_since(operation_type: str, since_iso: str, exclude_document_id: str) -> int:
    """
    Cuenta los trabajos completados del mismo tipo desde una fecha, excluyendo un documento.
    Sirve para detectar que otro documento avanzó el contador de la máquina durante la incertidumbre.
    Args:
        operation_type: Tipo de operación
        since_iso: Marca de tiempo ISO local (inclusive)
        exclude_document_id: Documento que no se cuenta
    Returns:
        int: Cantidad de trabajos completados
    """
    with _lock, _connect() as conn:
        row = conn.execute(
            "SELECT COUNT(*) AS total FROM print_jobs"
            " WHERE operation_type=? AND status='completed' AND updated_at>=? AND document_id<>?",
            (operation_type, since_iso, exclude_document_id),
        ).fetchone()
    return int(row["total"])


def has_processing_jobs() -> bool:
    """
    Indica si hay alguna impresión en curso (trabajo en 'processing' no huérfano). Solo lee.
    Los trabajos huérfanos (más de STALE_PROCESSING_SECONDS sin actualizarse) no cuentan: el proceso
    murió a mitad de la impresión y bloquearían el monitor indefinidamente.
    Returns:
        bool: True si existe al menos un trabajo en curso reciente
    """
    with _lock, _connect() as conn:
        rows = conn.execute("SELECT updated_at FROM print_jobs WHERE status='processing'").fetchall()
    return any(not _is_stale(row["updated_at"]) for row in rows)


def restart_job(document_id: str, operation_type: str) -> bool:
    """
    Reabre como 'processing' un trabajo 'unknown' que se comprobó que NO se emitió (reintento seguro).
    Es atómico: solo uno de varios reintentos simultáneos obtiene True.
    Args:
        document_id: Clave de idempotencia del documento
        operation_type: Tipo de operación
    Returns:
        bool: True si el trabajo estaba en 'unknown' y quedó en 'processing'
    """
    now = _now_iso()
    with _lock, _connect() as conn:
        cursor = conn.execute(
            "UPDATE print_jobs SET status='processing', error_message=NULL, response=NULL, updated_at=?"
            " WHERE document_id=? AND operation_type=? AND status='unknown'",
            (now, document_id, operation_type),
        )
    return cursor.rowcount == 1


class CounterRegressionError(ValueError):
    """Se intentó confirmar un número de documento igual o menor al ya confirmado (nunca debe repetirse)."""


def _counter_row_to_dict(row: sqlite3.Row) -> dict[str, str]:
    """
    Convierte una fila de la tabla counters en un diccionario con los campos de COUNTER_FIELDS.
    Args:
        row: Fila leída de la tabla counters
    Returns:
        dict[str, str]: Valores del contador
    """
    return {field: row[field] for field in COUNTER_FIELDS}


def load_counter(printer_key: str, seed: Callable[[], dict[str, str]]) -> dict[str, str]:
    """
    Lee el contador emulado de una impresora no fiscal; si no tiene fila la crea (migración única).
    La siembra se hace con BEGIN IMMEDIATE para que dos procesos no inserten a la vez. Una vez creada la
    fila, el seed (p. ej. el JSON del template) deja de ser la fuente de verdad.
    Args:
        printer_key: Clave de la impresora ("matrix" o "ticket")
        seed: Función sin argumentos que devuelve los valores iniciales (campos de COUNTER_FIELDS)
    Returns:
        dict[str, str]: Valores actuales del contador
    """
    _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with _lock, _connect() as conn:
        conn.execute(_CREATE_COUNTERS)
        row = conn.execute("SELECT * FROM counters WHERE printer_key=?", (printer_key,)).fetchone()
        if row is not None:
            return _counter_row_to_dict(row)
        conn.execute("BEGIN IMMEDIATE")
        row = conn.execute("SELECT * FROM counters WHERE printer_key=?", (printer_key,)).fetchone()
        if row is not None:  # Otro proceso sembró mientras esperábamos el bloqueo
            return _counter_row_to_dict(row)
        values = {field: str(seed()[field]) for field in COUNTER_FIELDS}
        conn.execute(
            "INSERT INTO counters (printer_key, " + ", ".join(COUNTER_FIELDS) + ", updated_at)"
            " VALUES (?, " + ", ".join("?" for _ in COUNTER_FIELDS) + ", ?)",
            (printer_key, *(values[field] for field in COUNTER_FIELDS), _now_iso()),
        )
        logger.info("Job store: contador '%s' sembrado en la base de datos", printer_key)
        return values


def commit_counter_row(printer_key: str, counter_key: str, reserved: dict[str, str]) -> None:
    """
    Confirma en una sola transacción (BEGIN IMMEDIATE) los valores reservados de un contador.
    Regla: un número confirmado nunca disminuye ni se repite. Si el número guardado para counter_key es
    mayor o igual al reservado se rechaza con CounterRegressionError y no se modifica nada.
    Args:
        printer_key: Clave de la impresora ("matrix" o "ticket")
        counter_key: Campo del número de documento ("document_invoice", "document_credit", ...)
        reserved: Diccionario devuelto por reserve_counter (document_date, document_number, machine_report)
    Raises:
        CounterRegressionError: Si el número reservado no es mayor al guardado
        LookupError: Si la impresora no tiene fila de contador
    """
    with _lock, _connect() as conn:
        conn.execute("BEGIN IMMEDIATE")
        row = conn.execute("SELECT * FROM counters WHERE printer_key=?", (printer_key,)).fetchone()
        if row is None:
            raise LookupError(f"No existe contador para la impresora '{printer_key}'")
        stored = int(row[counter_key])
        new_number = int(reserved["document_number"])
        if stored >= new_number:
            logger.critical(
                "Contador %s/%s: se rechaza confirmar %s porque ya está confirmado %s (nunca debe repetirse)",
                printer_key,
                counter_key,
                reserved["document_number"],
                row[counter_key],
            )
            raise CounterRegressionError(
                f"Contador {printer_key}/{counter_key}: {reserved['document_number']} no supera al guardado {row[counter_key]}"
            )
        conn.execute(
            f"UPDATE counters SET document_date=?, machine_report=?, {counter_key}=?, updated_at=?"  # counter_key viene de COUNTER_MAPPING
            " WHERE printer_key=?",
            (
                reserved["document_date"],
                reserved["machine_report"],
                str(reserved["document_number"]).zfill(8),
                _now_iso(),
                printer_key,
            ),
        )
    logger.info("Job store: contador %s/%s confirmado: %s", printer_key, counter_key, reserved["document_number"])


def _read_counters(db_file: Path | None = None) -> dict[str, dict[str, str]]:
    """
    Lee todas las filas de counters de la base indicada (por defecto la activa). Tolera que no exista la tabla.
    Args:
        db_file: Ruta de la base a leer; None usa la base activa
    Returns:
        dict: {printer_key: valores del contador}
    """
    try:
        with closing(sqlite3.connect(str(db_file or _DB_PATH), timeout=5.0)) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT * FROM counters").fetchall()
    except sqlite3.Error:
        return {}
    return {row["printer_key"]: _counter_row_to_dict(row) for row in rows}


def _merge_counters(conn: sqlite3.Connection, current: dict[str, dict[str, str]]) -> None:
    """
    Tras una restauración, deja cada contador en el máximo entre el valor vigente antes de restaurar y el
    restaurado, para que un respaldo antiguo nunca retroceda los números (ni la fecha). Las impresoras que
    solo existían en el estado vigente se reinsertan.
    Args:
        conn: Conexión a la base ya restaurada y con el esquema al día
        current: Contadores vigentes antes de restaurar (resultado de _read_counters)
    """
    for printer_key, cur in current.items():
        row = conn.execute("SELECT * FROM counters WHERE printer_key=?", (printer_key,)).fetchone()
        if row is None:
            conn.execute(
                "INSERT INTO counters (printer_key, " + ", ".join(COUNTER_FIELDS) + ", updated_at)"
                " VALUES (?, " + ", ".join("?" for _ in COUNTER_FIELDS) + ", ?)",
                (printer_key, *(cur[field] for field in COUNTER_FIELDS), _now_iso()),
            )
            continue
        merged = _counter_row_to_dict(row)
        for field in (*_COUNTER_NUMBER_FIELDS, "machine_report"):
            merged[field] = max(merged[field], cur[field], key=int)
        # ISO YYYY-MM-DD: el orden de texto es cronológico
        merged["document_date"] = max(merged["document_date"], cur["document_date"])
        conn.execute(
            "UPDATE counters SET " + ", ".join(f"{field}=?" for field in COUNTER_FIELDS) + ", updated_at=?"
            " WHERE printer_key=?",
            (*(merged[field] for field in COUNTER_FIELDS), _now_iso(), printer_key),
        )
        logger.info("Job store: contador '%s' conservado al restaurar (máximo entre vigente y respaldo)", printer_key)


def backup_db(target_path: str | Path | None = None) -> Path:
    """
    Creates an atomic, consistent online backup of the SQLite database using SQLite's backup API.
    Does not block concurrent reads or writes in WAL mode.
    """
    if target_path is None:
        backup_dir = Path(get_base_path()) / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        target_path = backup_dir / f"print_jobs_{timestamp}.db"
    else:
        target_path = Path(target_path)
        target_path.parent.mkdir(parents=True, exist_ok=True)

    with _lock, _connect() as src_conn:
        with closing(sqlite3.connect(str(target_path))) as dst_conn:
            src_conn.backup(dst_conn)

    logger.info("Respaldo de base de datos generado: %s", target_path)
    return target_path


def restore_db(backup_path: str | Path) -> None:
    """
    Restores the database from a backup file after verifying its integrity.
    Atomically copies content into the live database.
    """
    backup_file = Path(backup_path)
    if not backup_file.exists():
        raise FileNotFoundError(f"Archivo de respaldo no encontrado: {backup_file}")

    # Integrity check of the backup file before restoring
    with closing(sqlite3.connect(str(backup_file))) as test_conn:
        test_conn.row_factory = sqlite3.Row
        check = test_conn.execute("PRAGMA integrity_check").fetchone()
        if not check or check[0] != "ok":
            raise ValueError(f"El archivo de respaldo está corrupto o no es válido: {check}")

    # Ensure target parent directory exists and perform atomic restore
    _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with _lock:
        current_counters = _read_counters()  # Los contadores no deben retroceder al restaurar un respaldo antiguo
        with closing(sqlite3.connect(str(backup_file))) as src_conn:
            with _connect() as dst_conn:
                src_conn.backup(dst_conn)
            # Un respaldo antiguo puede no tener las columnas nuevas: se migra la base ya restaurada
            with _connect() as conn:
                _ensure_schema(conn)
                _merge_counters(conn, current_counters)

    logger.info("Base de datos restaurada exitosamente desde: %s", backup_file)
