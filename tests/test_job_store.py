"""
Unit tests for the SQLite job store (idempotency engine).
"""

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
