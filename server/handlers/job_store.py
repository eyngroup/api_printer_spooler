#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from handy.tools import get_base_path

logger = logging.getLogger(__name__)

_DB_PATH = Path(get_base_path()) / "data" / "print_jobs.db"

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
    UNIQUE (document_id, operation_type)
)
"""

_CREATE_INDEX = "CREATE INDEX IF NOT EXISTS idx_doc_op ON print_jobs (document_id, operation_type)"


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(str(_DB_PATH), timeout=5.0)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=3000")
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create the jobs table and index if they do not exist."""
    _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with _connect() as conn:
        conn.execute(_CREATE_TABLE)
        conn.execute(_CREATE_INDEX)
    logger.info("Job store inicializado: %s", _DB_PATH)


def acquire_job(document_id: str, operation_type: str) -> Tuple[str, Optional[Dict[str, Any]]]:
    """
    Atomically claim a print job slot.

    Returns a (result, payload) tuple:
        ('new',       None)           — first request, proceed
        ('retry',     None)           — previous attempt failed, proceed
        ('duplicate', cached_dict)    — already completed, return cached
        ('in_progress', None)         — currently processing, return 409
    """
    now = datetime.now().isoformat(timespec="seconds")

    with _lock:
        with _connect() as conn:
            row = conn.execute(
                "SELECT status, response FROM print_jobs WHERE document_id=? AND operation_type=?",
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
                return "duplicate", cached

            if existing["status"] == "processing":
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


def complete_job(document_id: str, operation_type: str, response: Dict[str, Any]) -> None:
    """Mark a job as successfully completed and persist the response."""
    now = datetime.now().isoformat(timespec="seconds")
    with _connect() as conn:
        conn.execute(
            "UPDATE print_jobs SET status='completed', response=?, updated_at=?"
            " WHERE document_id=? AND operation_type=?",
            (json.dumps(response), now, document_id, operation_type),
        )
    logger.debug("Job store: completado %s/%s", document_id, operation_type)


def fail_job(document_id: str, operation_type: str, error_message: str) -> None:
    """Mark a job as failed. The next request for the same document will be retried."""
    now = datetime.now().isoformat(timespec="seconds")
    with _connect() as conn:
        conn.execute(
            "UPDATE print_jobs SET status='failed', error_message=?, updated_at=?"
            " WHERE document_id=? AND operation_type=?",
            (error_message, now, document_id, operation_type),
        )
    logger.debug("Job store: fallido %s/%s — %s", document_id, operation_type, error_message)
