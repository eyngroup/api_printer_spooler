"""
Tests del contador emulado de las impresoras no fiscales guardado en SQLite.
"""

import json
import sqlite3
import threading
from contextlib import closing
from pathlib import Path

import pytest

from printers.printer_counter import FiscalCounter
from server.handlers import job_store

COUNTER_JSON = {
    "document_date": "2020-01-01",
    "document_invoice": "00000010",
    "document_credit": "00000002",
    "document_debit": "00000003",
    "document_note": "00000004",
    "machine_report": "0007",
    "machine_serial": "Z1B0000001",
}


def make_template(path: Path, counter: dict | None = None) -> Path:
    """Escribe un template mínimo (con o sin sección counter) y devuelve su ruta."""
    data = {"header": {"name": "X"}}
    if counter is not None:
        data["counter"] = counter
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


@pytest.fixture
def template(tmp_path: Path) -> Path:
    """Template con contador previo (origen de la migración)."""
    return make_template(tmp_path / "template.json", dict(COUNTER_JSON))


def stored(key: str = "matrix") -> dict[str, str]:
    """Contador vigente en SQLite para una impresora."""
    return job_store._read_counters()[key]


def test_first_use_migrates_counter_from_template_json(template: Path):
    """Sin fila en SQLite, el contador se siembra desde la sección counter del template."""
    counter = FiscalCounter(str(template), "matrix")
    reserved = counter.reserve_counter("invoice")

    assert reserved["document_number"] == "00000011"
    assert reserved["machine_serial"] == "Z1B0000001"
    assert stored()["document_invoice"] == "00000010"  # la reserva no avanza el contador
    assert stored()["machine_report"] == "0007"


def test_template_without_counter_seeds_from_defaults(tmp_path: Path):
    """Sin sección counter la siembra usa ceros y NO se escribe el template."""
    template = make_template(tmp_path / "t.json")
    before = template.read_text(encoding="utf-8")

    reserved = FiscalCounter(str(template), "ticket").reserve_counter("invoice")

    assert reserved["document_number"] == "00000001"
    assert stored("ticket")["document_credit"] == "00000000"
    assert template.read_text(encoding="utf-8") == before


def test_missing_or_broken_template_seeds_from_defaults(tmp_path: Path):
    """Un template ausente o con JSON inválido no impide sembrar el contador."""
    broken = tmp_path / "broken.json"
    broken.write_text("{no es json", encoding="utf-8")

    assert FiscalCounter(str(broken), "matrix").reserve_counter()["document_number"] == "00000001"
    assert FiscalCounter(str(tmp_path / "nope.json"), "ticket").reserve_counter()["document_number"] == "00000001"


def test_reserve_commit_persists_in_sqlite_and_leaves_json_untouched(template: Path):
    """Confirmar avanza el contador en SQLite y el template JSON no se modifica."""
    before = template.read_text(encoding="utf-8")
    counter = FiscalCounter(str(template), "matrix")

    reserved = counter.reserve_counter("credit")
    counter.commit_counter("credit", reserved)

    row = stored()
    assert row["document_credit"] == "00000003"
    assert row["document_invoice"] == "00000010"
    assert row["machine_report"] == reserved["machine_report"] == "0008"  # cambió el día respecto de 2020-01-01
    assert row["document_date"] == reserved["document_date"]
    assert template.read_text(encoding="utf-8") == before
    assert FiscalCounter(str(template), "matrix").reserve_counter("credit")["document_number"] == "00000004"


def test_printers_have_independent_counters(template: Path):
    """Matriz y ticket tienen filas separadas."""
    matrix = FiscalCounter(str(template), "matrix")
    matrix.commit_counter("invoice", matrix.reserve_counter("invoice"))

    assert stored("matrix")["document_invoice"] == "00000011"
    assert FiscalCounter(str(template), "ticket").reserve_counter("invoice")["document_number"] == "00000011"
    assert stored("ticket")["document_invoice"] == "00000010"


def test_commit_never_decreases_or_repeats(template: Path, caplog):
    """Confirmar un número menor o igual al guardado se rechaza, se registra CRITICAL y no cambia nada."""
    counter = FiscalCounter(str(template), "matrix")
    reserved = counter.reserve_counter("invoice")
    counter.commit_counter("invoice", reserved)

    with pytest.raises(job_store.CounterRegressionError):
        counter.commit_counter("invoice", reserved)  # repetido
    with pytest.raises(job_store.CounterRegressionError):
        counter.commit_counter("invoice", {**reserved, "document_number": "00000005"})  # menor

    assert stored()["document_invoice"] == "00000011"
    assert "nunca debe repetirse" in caplog.text


def test_concurrent_requests_get_distinct_consecutive_numbers(template: Path):
    """Varios hilos que reservan, 'imprimen' y confirman bajo el cerrojo reciben números distintos y consecutivos."""
    numbers: list[str] = []

    def worker():
        with FiscalCounter.LOCK:
            counter = FiscalCounter(str(template), "matrix")
            reserved = counter.reserve_counter("invoice")
            counter.commit_counter("invoice", reserved)
            numbers.append(reserved["document_number"])

    threads = [threading.Thread(target=worker) for _ in range(8)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert sorted(numbers) == [f"{n:08d}" for n in range(11, 19)]
    assert stored()["document_invoice"] == "00000018"


def test_gui_saving_template_without_counter_does_not_change_next_number(template: Path):
    """Si la GUI guarda el template sin la sección counter (o con ceros), el siguiente número no cambia."""
    counter = FiscalCounter(str(template), "matrix")
    counter.commit_counter("invoice", counter.reserve_counter("invoice"))

    make_template(template)  # simula el guardado de la GUI que pierde counter
    assert FiscalCounter(str(template), "matrix").reserve_counter("invoice")["document_number"] == "00000012"
    template.write_text("{}", encoding="utf-8")  # y un JSON vacío tras un error de lectura
    assert FiscalCounter(str(template), "matrix").reserve_counter("invoice")["document_number"] == "00000012"


def test_restore_older_backup_keeps_max_counters(template: Path, tmp_path: Path):
    """Restaurar un respaldo antiguo no retrocede números, reporte ni fecha; reinserta filas ausentes."""
    counter = FiscalCounter(str(template), "matrix")
    counter.commit_counter("invoice", counter.reserve_counter("invoice"))  # 11
    backup = job_store.backup_db(tmp_path / "old.db")

    counter.commit_counter("invoice", counter.reserve_counter("invoice"))  # 12
    counter.commit_counter("note", counter.reserve_counter("note"))  # nota 5
    other = FiscalCounter(str(template), "ticket")
    other.commit_counter("invoice", other.reserve_counter("invoice"))  # solo existe en el estado vigente

    # El respaldo antiguo simula una base sin la fila del ticket y con valores menores
    with closing(sqlite3.connect(str(backup))) as conn, conn:
        conn.execute("DELETE FROM counters WHERE printer_key='ticket'")
        conn.execute("UPDATE counters SET document_date='2019-01-01', machine_report='0001'")

    job_store.restore_db(backup)

    assert stored()["document_invoice"] == "00000012"
    assert stored()["document_note"] == "00000005"
    assert stored()["machine_report"] == "0008"
    assert stored()["document_date"] >= "2020-01-01"
    assert stored("ticket")["document_invoice"] == "00000011"


def test_restore_backup_without_counters_table_keeps_current(template: Path, tmp_path: Path):
    """Un respaldo anterior a la tabla counters no borra los contadores vigentes."""
    counter = FiscalCounter(str(template), "matrix")
    counter.commit_counter("invoice", counter.reserve_counter("invoice"))
    legacy = tmp_path / "legacy.db"
    with closing(sqlite3.connect(str(legacy))) as conn, conn:
        conn.execute("CREATE TABLE print_jobs (id INTEGER PRIMARY KEY, document_id TEXT, operation_type TEXT)")

    job_store.restore_db(legacy)

    assert stored()["document_invoice"] == "00000011"
