"""
Unit tests for the SQLite job store (idempotency engine).
"""

import sqlite3
import threading
from contextlib import closing
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from server.handlers import job_store


@pytest.fixture(autouse=True)
def temp_job_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Use an isolated SQLite database for each test run."""
    db_file = tmp_path / "test_jobs.db"
    monkeypatch.setattr(job_store, "_DB_PATH", db_file)
    job_store.init_db()
    yield db_file


def test_init_db_creates_table(temp_job_db: Path):
    """Verify that init_db creates the database and table."""
    assert temp_job_db.exists()
    with job_store._connect() as conn:
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='print_jobs'")
        assert cursor.fetchone() is not None


def test_acquire_new_job():
    """First acquisition of a job should return 'new'."""
    result, cached = job_store.acquire_job("INV-001", "invoice")
    assert result == "new"
    assert cached is None


def test_acquire_in_progress_job():
    """Acquiring a job currently marked as 'processing' returns 'in_progress'."""
    result1, _ = job_store.acquire_job("INV-002", "invoice")
    assert result1 == "new"

    result2, cached2 = job_store.acquire_job("INV-002", "invoice")
    assert result2 == "in_progress"
    assert cached2 is None


def test_complete_and_duplicate_job():
    """Completed job should return 'duplicate' with cached response on subsequent calls."""
    doc_id = "INV-003"
    op_type = "invoice"
    payload = {"status": True, "message": "Documento impreso", "data": {"fiscal_number": "000123"}}

    res, _ = job_store.acquire_job(doc_id, op_type)
    assert res == "new"

    job_store.complete_job(doc_id, op_type, payload)

    res_dup, cached_payload = job_store.acquire_job(doc_id, op_type)
    assert res_dup == "duplicate"
    assert cached_payload == payload


def test_fail_and_retry_job():
    """Failed job should allow subsequent acquisition with status 'retry'."""
    doc_id = "INV-004"
    op_type = "credit"

    res, _ = job_store.acquire_job(doc_id, op_type)
    assert res == "new"

    job_store.fail_job(doc_id, op_type, "Paper out")

    res_retry, cached = job_store.acquire_job(doc_id, op_type)
    assert res_retry == "retry"
    assert cached is None


def test_backup_and_restore_db(tmp_path: Path):
    """Verify backup creates a valid copy and restore reinstates data."""
    # 1. Populate DB with a job
    job_store.acquire_job("INV-BACKUP-01", "invoice")
    job_store.complete_job("INV-BACKUP-01", "invoice", {"status": True})

    # 2. Perform backup
    backup_file = tmp_path / "backup_test.db"
    generated_path = job_store.backup_db(backup_file)
    assert generated_path.exists()

    # 3. Simulate data loss / corruption in live db
    with job_store._connect() as conn:
        conn.execute("DELETE FROM print_jobs")

    res_after_wipe, _ = job_store.acquire_job("INV-BACKUP-01", "invoice")
    assert res_after_wipe == "new"  # Was wiped, treated as new

    # 4. Restore from backup
    job_store.restore_db(backup_file)

    # 5. Check restored state
    res_restored, cached = job_store.acquire_job("INV-BACKUP-01", "invoice")
    assert res_restored == "duplicate"
    assert cached == {"status": True}


def test_restore_corrupt_file_rejected(tmp_path: Path):
    """Restoring from a corrupt non-sqlite file should raise ValueError."""
    fake_file = tmp_path / "corrupt.db"
    fake_file.write_text("corrupted content not a sqlite db")

    with pytest.raises(Exception):
        job_store.restore_db(fake_file)


@pytest.fixture
def tracked_connections(monkeypatch: pytest.MonkeyPatch) -> list[sqlite3.Connection]:
    """Record every SQLite connection opened by the job store."""
    opened: list[sqlite3.Connection] = []
    real_connect = sqlite3.connect

    def _tracking_connect(*args, **kwargs):
        conn = real_connect(*args, **kwargs)
        opened.append(conn)
        return conn

    monkeypatch.setattr(job_store.sqlite3, "connect", _tracking_connect)
    return opened


def _is_closed(conn: sqlite3.Connection) -> bool:
    """Return True when the connection has been closed."""
    try:
        conn.execute("SELECT 1")
    except sqlite3.ProgrammingError:
        return True
    return False


def test_connections_are_closed(tmp_path: Path, tracked_connections: list[sqlite3.Connection]):
    """Every connection opened by the store must be closed (avoids file locks on Windows)."""
    job_store.acquire_job("INV-CLOSE-01", "invoice")
    job_store.complete_job("INV-CLOSE-01", "invoice", {"status": True})
    job_store.acquire_job("INV-CLOSE-02", "invoice")
    job_store.fail_job("INV-CLOSE-02", "invoice", "error")
    backup_file = job_store.backup_db(tmp_path / "close_backup.db")
    job_store.restore_db(backup_file)

    assert tracked_connections
    assert all(_is_closed(conn) for conn in tracked_connections)


@pytest.mark.parametrize("operation", ["complete", "fail"])
def test_job_updates_wait_for_lock(operation: str):
    """complete_job and fail_job must serialize through the process-level lock."""
    job_store.acquire_job("INV-LOCK-01", "invoice")
    if operation == "complete":
        worker = threading.Thread(target=job_store.complete_job, args=("INV-LOCK-01", "invoice", {"status": True}))
    else:
        worker = threading.Thread(target=job_store.fail_job, args=("INV-LOCK-01", "invoice", "error"))

    with job_store._lock:
        worker.start()
        worker.join(timeout=0.3)
        assert worker.is_alive(), "La actualización no esperó al lock"

    worker.join(timeout=2)
    assert not worker.is_alive()


def _set_times(document_id: str, *, created: str | None = None, updated: str | None = None, op: str = "invoice"):
    """Fija marcas de tiempo de un trabajo para simular antigüedad."""
    with job_store._connect() as conn:
        if created:
            conn.execute(
                "UPDATE print_jobs SET created_at=? WHERE document_id=? AND operation_type=?",
                (created, document_id, op),
            )
        if updated:
            conn.execute(
                "UPDATE print_jobs SET updated_at=? WHERE document_id=? AND operation_type=?",
                (updated, document_id, op),
            )


def test_init_db_migrates_old_schema(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """A DB created with the old schema gets counter_before without losing rows."""
    old_db = tmp_path / "old_jobs.db"
    with sqlite3.connect(str(old_db)) as conn:
        conn.execute(
            "CREATE TABLE print_jobs (id INTEGER PRIMARY KEY AUTOINCREMENT, document_id TEXT NOT NULL,"
            " operation_type TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'processing', response TEXT,"
            " error_message TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL,"
            " UNIQUE (document_id, operation_type))"
        )
        conn.execute(
            "INSERT INTO print_jobs (document_id, operation_type, status, created_at, updated_at)"
            " VALUES ('OLD-1', 'invoice', 'failed', '2024-01-01T00:00:00', '2024-01-01T00:00:00')"
        )
    conn.close()
    monkeypatch.setattr(job_store, "_DB_PATH", old_db)

    job_store.init_db()
    job_store.init_db()  # idempotente

    job = job_store.get_job("OLD-1", "invoice")
    assert job is not None
    assert job["status"] == "failed"
    assert job["counter_before"] is None
    job_store.set_counter_before("OLD-1", "invoice", "00000010")
    assert job_store.get_job("OLD-1", "invoice")["counter_before"] == "00000010"


def test_restore_old_backup_is_migrated(tmp_path: Path):
    """Restoring a backup made with the old schema keeps the store usable."""
    backup = tmp_path / "old_backup.db"
    with closing(sqlite3.connect(str(backup))) as conn, conn:
        conn.execute(
            "CREATE TABLE print_jobs (id INTEGER PRIMARY KEY AUTOINCREMENT, document_id TEXT NOT NULL,"
            " operation_type TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'processing', response TEXT,"
            " error_message TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL,"
            " UNIQUE (document_id, operation_type))"
        )
    job_store.restore_db(backup)
    assert job_store.acquire_job("NEW-1", "invoice")[0] == "new"
    job_store.set_counter_before("NEW-1", "invoice", "00000001")


def test_stale_processing_becomes_unknown_and_persists():
    """A 'processing' job older than STALE_PROCESSING_SECONDS is an orphan -> 'unknown', and stays so."""
    job_store.acquire_job("INV-OLD", "invoice")
    old = (datetime.now() - timedelta(seconds=job_store.STALE_PROCESSING_SECONDS + 5)).isoformat(timespec="seconds")
    _set_times("INV-OLD", updated=old)

    assert job_store.acquire_job("INV-OLD", "invoice") == ("unknown", None)
    job = job_store.get_job("INV-OLD", "invoice")
    assert job["status"] == "unknown"
    assert "huérfano" in job["error_message"]
    assert job_store.acquire_job("INV-OLD", "invoice") == ("unknown", None)


def test_fresh_processing_stays_in_progress():
    """A recent 'processing' job is still in progress (409)."""
    job_store.acquire_job("INV-NEW", "invoice")
    recent = (datetime.now() - timedelta(seconds=30)).isoformat(timespec="seconds")
    _set_times("INV-NEW", updated=recent)
    assert job_store.acquire_job("INV-NEW", "invoice") == ("in_progress", None)


def test_mark_unknown_and_restart_job():
    """mark_unknown keeps the state across acquires; restart_job reopens it only from 'unknown'."""
    job_store.acquire_job("INV-U", "invoice")
    assert job_store.restart_job("INV-U", "invoice") is False  # processing: no es 'unknown'
    job_store.mark_unknown("INV-U", "invoice", "sin respuesta")
    assert job_store.acquire_job("INV-U", "invoice") == ("unknown", None)
    assert job_store.restart_job("INV-U", "invoice") is True
    job = job_store.get_job("INV-U", "invoice")
    assert job["status"] == "processing"
    assert job["error_message"] is None
    assert job_store.get_job("NOPE", "invoice") is None


def test_get_job_decodes_response():
    """get_job returns the decoded response of a completed job."""
    job_store.acquire_job("INV-R", "invoice")
    job_store.complete_job("INV-R", "invoice", {"status": True})
    job = job_store.get_job("INV-R", "invoice")
    assert job["response"] == {"status": True}
    assert job["created_at"] and job["updated_at"]


def test_completed_since_counts_matching_jobs():
    """completed_since counts completed jobs of the same type since a date, excluding one document."""
    for doc, op in (("A", "invoice"), ("B", "invoice"), ("C", "credit"), ("D", "invoice")):
        job_store.acquire_job(doc, op)
        job_store.complete_job(doc, op, {"status": True})
    job_store.acquire_job("E", "invoice")  # processing: no cuenta
    _set_times("D", updated="2000-01-01T00:00:00")  # anterior a la fecha de corte

    since = "2020-01-01T00:00:00"
    assert job_store.completed_since("invoice", since, "X") == 2  # A y B
    assert job_store.completed_since("invoice", since, "A") == 1  # excluye A
    assert job_store.completed_since("credit", since, "X") == 1
