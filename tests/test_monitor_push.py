"""
Pruebas del envío (push) del monitor fiscal a Odoo: configuración, envelope, cola, remitente y planificador.
Nunca se hacen llamadas de red reales ni se lee una máquina: se usan sesiones HTTP falsas y snapshots inyectados.
"""

import json
import re
import time
from datetime import datetime, timedelta
from pathlib import Path

import pytest
import requests
from jsonschema import validate

from server.config_loader import CONFIG_SCHEMA, ConfigManager, get_monitor_push_config
from server.handlers import job_store, monitor_push
from server.handlers.fiscal_monitor import FiscalMonitor
from server.server_api import create_app

NOW = datetime(2026, 10, 9, 15, 22, 5)  # noqa: DTZ001 - hora local sin zona, como el spooler
SNAPSHOT_OK = {"available": True, "read_at": "2026-10-09T15:22:00", "machine": {"serial": "Z7C0000000"}}
SNAPSHOT_NO = {"available": False, "reason": "Impresión en curso"}


def make_config(**push) -> dict:
    """Configuración mínima con la sección monitor_push habilitada y completa (se puede sobrescribir)."""
    settings = {"enabled": True, "url": "https://odoo.example/push", "token": "tok-1", "interval_minutes": 60}
    settings.update(push)
    return {"server": {"server_mode": "SPOOLER"}, "printers": {}, "monitor_push": settings}


class FakeResponse:
    """Respuesta HTTP falsa con status y cuerpo JSON."""

    def __init__(self, status_code: int = 200, body=None):
        self.status_code = status_code
        self._body = {"status": "ok"} if body is None else body

    def json(self):
        if isinstance(self._body, Exception):
            raise self._body
        return self._body


class FakeSession:
    """Sesión falsa: devuelve (o lanza) las respuestas en orden y registra cada llamada."""

    def __init__(self, *responses):
        self.responses = list(responses)
        self.calls: list[dict] = []

    def post(self, url, json=None, headers=None, timeout=None, **kwargs):
        self.calls.append({"url": url, "json": json, "headers": headers, "timeout": timeout, **kwargs})
        item = self.responses.pop(0) if self.responses else FakeResponse()
        if isinstance(item, Exception):
            raise item
        return item


@pytest.fixture(autouse=True)
def clean_state(monkeypatch):
    """Estado del módulo limpio y serial configurado fijo (no se lee el template real)."""
    monitor_push.reset_state()
    monkeypatch.setattr("server.server_api._configured_serial", lambda: "CFG0000001")
    yield
    monitor_push.stop_scheduler()
    monitor_push.reset_state()


def enqueue(trigger="scheduled", config=None, snapshot=None, now=NOW) -> str:
    """Encola una lectura con snapshot inyectado y devuelve su reading_id."""
    return monitor_push.enqueue_reading(trigger, config or make_config(), snapshot or SNAPSHOT_OK, now)


# ------------------------------------------------------------------ configuración


def test_missing_section_is_disabled_with_defaults():
    settings = get_monitor_push_config({"server": {}})
    assert settings == {"enabled": False, "url": "", "token": "", "interval_minutes": 60, "branch_code": ""}
    assert get_monitor_push_config(None)["enabled"] is False


def test_interval_is_clamped_to_minimum():
    assert get_monitor_push_config({"monitor_push": {"interval_minutes": 5}})["interval_minutes"] == 15
    assert get_monitor_push_config({"monitor_push": {"interval_minutes": 30}})["interval_minutes"] == 30
    assert get_monitor_push_config({"monitor_push": {"interval_minutes": "abc"}})["interval_minutes"] == 60


def test_schema_accepts_config_with_and_without_section():
    defaults = json.loads(Path("config/defaults/config.json").read_text(encoding="utf-8"))
    validate(defaults, CONFIG_SCHEMA)
    assert defaults["monitor_push"]["enabled"] is False
    without = {k: v for k, v in defaults.items() if k != "monitor_push"}
    validate(without, CONFIG_SCHEMA)


def test_status_endpoint_does_not_expose_monitor_push():
    config = dict(ConfigManager.get_config())
    config["monitor_push"] = {"enabled": True, "url": "https://x", "token": "SECRET-TOKEN"}
    app = create_app(config)
    app.config["TESTING"] = True
    body = app.test_client().get("/api/status").get_data(as_text=True)
    assert "monitor_push" not in body
    assert "SECRET-TOKEN" not in body


# ------------------------------------------------------------------ envelope


def test_envelope_has_all_contract_fields():
    config = make_config(branch_code="SUC01")
    env = monitor_push.build_envelope(SNAPSHOT_OK, "before_z", config, NOW)
    assert env["contract_version"] == "1.0"
    assert re.fullmatch(r"[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}", env["reading_id"])
    assert env["trigger"] == "before_z"
    assert env["sent_at"] == "2026-10-09T15:22:05"
    assert re.fullmatch(r"[+-]\d{2}:\d{2}", env["utc_offset"])
    assert set(env["spooler"]) == {"version", "host", "mode"}
    assert env["spooler"]["mode"] == "SPOOLER"
    assert env["branch_code"] == "SUC01"
    assert env["machine_serial"] == "Z7C0000000"
    assert env["snapshot"] is SNAPSHOT_OK


def test_utc_offset_format(monkeypatch):
    class FixedOffset(datetime):
        def astimezone(self, tz=None):
            from datetime import timezone

            return self.replace(tzinfo=timezone(timedelta(hours=-4)))

    assert monitor_push._format_offset(FixedOffset(2026, 10, 9)) == "-04:00"
    assert monitor_push._format_offset(NOW) != ""


def test_machine_serial_falls_back_to_configured_when_unavailable():
    env = monitor_push.build_envelope(SNAPSHOT_NO, "scheduled", make_config(), NOW)
    assert env["machine_serial"] == "CFG0000001"
    assert env["snapshot"] == SNAPSHOT_NO


def test_sent_at_is_refreshed_on_resend_with_same_reading_id():
    reading_id = enqueue()
    session = FakeSession(FakeResponse(500), FakeResponse(200))
    monitor_push.send_due(make_config(), session, now=NOW)
    monitor_push.send_due(make_config(), session, now=NOW + timedelta(minutes=2))
    first, second = session.calls
    assert first["json"]["reading_id"] == second["json"]["reading_id"] == reading_id
    assert first["json"]["sent_at"] == "2026-10-09T15:22:05"
    assert second["json"]["sent_at"] == "2026-10-09T15:24:05"


# ------------------------------------------------------------------ cola de salida


def test_outbox_fetch_orders_oldest_first_and_honors_next_attempt():
    job_store.outbox_enqueue("b", "scheduled", {"n": 2})
    job_store.outbox_enqueue("a", "scheduled", {"n": 1})
    with job_store._connect() as conn:
        conn.execute("UPDATE monitor_outbox SET created_at='2026-10-09T10:00:00' WHERE reading_id='a'")
        conn.execute("UPDATE monitor_outbox SET created_at='2026-10-09T11:00:00' WHERE reading_id='b'")
    far = "2999-01-01T00:00:00"
    assert job_store.outbox_fetch_due(far)["reading_id"] == "a"
    job_store.outbox_mark_failed("a", "boom", "2999-12-31T00:00:00")
    item = job_store.outbox_fetch_due(far)
    assert item["reading_id"] == "b"
    assert job_store.outbox_count() == 2
    job_store.outbox_mark_sent("b")
    assert job_store.outbox_fetch_due(far) is None


def test_backoff_schedule():
    delays = [monitor_push._backoff_delay(n, 60) for n in range(1, 8)]
    assert [int(d.total_seconds() // 60) for d in delays] == [1, 2, 5, 10, 30, 60, 60]


def test_failure_increments_attempts_and_schedules_next():
    enqueue()
    monitor_push.send_due(make_config(), FakeSession(FakeResponse(503)), now=NOW)
    with job_store._connect() as conn:
        row = conn.execute("SELECT attempts, next_attempt_at, last_error FROM monitor_outbox").fetchone()
    assert row["attempts"] == 1
    assert row["next_attempt_at"] == "2026-10-09T15:23:05"
    assert "503" in row["last_error"]


def test_purge_drops_older_than_seven_days_and_beyond_500():
    for i in range(3):
        job_store.outbox_enqueue(f"old{i}", "scheduled", {})
    with job_store._connect() as conn:
        conn.execute("UPDATE monitor_outbox SET created_at='2026-10-01T00:00:00'")
    job_store.outbox_enqueue("fresh", "scheduled", {})
    with job_store._connect() as conn:
        conn.execute("UPDATE monitor_outbox SET created_at='2026-10-09T10:00:00' WHERE reading_id='fresh'")
    assert job_store.outbox_purge(NOW) == 3
    assert job_store.outbox_count() == 1

    with job_store._connect() as conn:
        for i in range(510):
            conn.execute(
                "INSERT INTO monitor_outbox (reading_id, trigger, payload, created_at, next_attempt_at)"
                " VALUES (?, 'scheduled', '{}', ?, '2026-10-09T10:00:00')",
                (f"r{i:03d}", f"2026-10-09T11:{i // 60:02d}:{i % 60:02d}"),
            )
    assert job_store.outbox_purge(NOW) == 11
    assert job_store.outbox_count() == 500
    with job_store._connect() as conn:
        ids = {r["reading_id"] for r in conn.execute("SELECT reading_id FROM monitor_outbox")}
    assert "r509" in ids and "r000" not in ids


# ------------------------------------------------------------------ remitente


def test_ok_and_duplicate_delete_the_reading():
    enqueue()
    enqueue()
    sleeps: list[float] = []
    session = FakeSession(FakeResponse(200, {"status": "ok"}), FakeResponse(200, {"status": "duplicate"}))
    status = monitor_push.send_due(make_config(), session, now=NOW, sleep=sleeps.append)
    assert status["pending"] == 0
    assert len(session.calls) == 2
    assert sleeps == [monitor_push.MIN_SECONDS_BETWEEN_REQUESTS]  # solo entre envíos, no antes del primero


def test_bearer_header_timeout_and_tls_verification_not_disabled():
    enqueue()
    session = FakeSession()
    monitor_push.send_due(make_config(token="abc"), session, now=NOW)
    call = session.calls[0]
    assert call["url"] == "https://odoo.example/push"
    assert call["headers"] == {"Authorization": "Bearer abc"}
    assert call["timeout"] == 15
    assert call.get("verify", True) is True


def test_401_pauses_and_resumes_only_after_token_change():
    enqueue()
    session = FakeSession(FakeResponse(401, {"code": "unauthorized"}))
    status = monitor_push.send_due(make_config(), session, now=NOW)
    assert status["paused"] is True
    assert status["pending"] == 1
    # Mismo token: no se envía nada
    monitor_push.send_due(make_config(), session, now=NOW + timedelta(hours=1))
    assert len(session.calls) == 1
    # Token nuevo: se reanuda
    status = monitor_push.send_due(make_config(token="tok-2"), session, now=NOW + timedelta(hours=1))
    assert len(session.calls) == 2
    assert status["paused"] is False
    assert status["pending"] == 0


def test_422_drops_reading_logs_error_and_continues(caplog):
    first = enqueue()
    enqueue()
    session = FakeSession(FakeResponse(422, {"code": "serial_mismatch", "message": "no coincide"}), FakeResponse(200))
    with caplog.at_level("ERROR"):
        status = monitor_push.send_due(make_config(), session, now=NOW, sleep=lambda s: None)
    assert len(session.calls) == 2
    assert status["pending"] == 0
    assert session.calls[0]["json"]["reading_id"] == first
    assert any("422" in r.message and r.levelname == "ERROR" for r in caplog.records)


@pytest.mark.parametrize(
    "failure",
    [FakeResponse(500), requests.Timeout("t"), requests.ConnectionError("c"), FakeResponse(404), FakeResponse(200, {})],
)
def test_failures_keep_readings_and_stop_draining(failure):
    enqueue()
    enqueue()
    session = FakeSession(failure)
    status = monitor_push.send_due(make_config(), session, now=NOW, sleep=lambda s: None)
    assert len(session.calls) == 1  # no se insiste con la siguiente
    assert status["pending"] == 2
    assert status["paused"] is False
    assert "Error" in status["last_result"]


def test_nothing_sent_when_disabled_or_incomplete():
    enqueue()
    session = FakeSession()
    for cfg in (
        make_config(enabled=False),
        make_config(url=""),
        make_config(token=""),
        {"server": {}},
    ):
        monitor_push.send_due(cfg, session, now=NOW)
    assert session.calls == []


def test_send_now_enqueues_manual_and_sends():
    session = FakeSession()
    monitor_push.send_now(make_config(), session=session, now=NOW, sleep=lambda s: None)
    assert session.calls[0]["json"]["trigger"] == "manual"
    sess2 = FakeSession()
    monitor_push.send_now(make_config(enabled=False), session=sess2, now=NOW)
    assert sess2.calls == []


# ------------------------------------------------------------------ enqueue_reading


def test_enqueue_reading_never_raises_when_monitor_fails(monkeypatch):
    def boom(*args, **kwargs):
        raise RuntimeError("serial roto")

    monkeypatch.setattr(FiscalMonitor, "get_snapshot", boom)
    assert monitor_push.enqueue_reading("before_z", make_config()) is None
    assert job_store.outbox_count() == 0


def test_enqueue_reading_uses_monitor_snapshot_when_not_injected(monkeypatch):
    monkeypatch.setattr(FiscalMonitor, "get_snapshot", lambda printers_config, force=False: SNAPSHOT_OK)
    assert monitor_push.enqueue_reading("scheduled", make_config(), now=NOW) is not None
    assert job_store.outbox_count() == 1


# ------------------------------------------------------------------ planificador


def test_scheduler_tick_enqueues_by_interval_and_sends():
    clock = {"now": NOW}
    sent: list[dict] = []
    sched = monitor_push.MonitorScheduler(
        lambda: make_config(interval_minutes=15),
        clock=lambda: clock["now"],
        sender=lambda config: sent.append(config) or {},
    )
    sched.tick()
    clock["now"] = NOW + timedelta(minutes=5)
    sched.tick()  # aún no toca otra lectura periódica, pero sí reintentar
    assert job_store.outbox_count() == 1
    clock["now"] = NOW + timedelta(minutes=16)
    sched.tick()
    assert job_store.outbox_count() == 2
    assert len(sent) == 3


def test_scheduler_in_proxy_mode_only_drains_pending():
    """En modo PROXY no se encolan lecturas periódicas (las envía el spooler destino), pero sí se vacía lo pendiente."""
    config = make_config()
    config["server"] = {**(config.get("server") or {}), "server_mode": "PROXY"}
    sent: list = []
    sched = monitor_push.MonitorScheduler(lambda: config, clock=lambda: NOW, sender=lambda cfg: sent.append(1) or {})
    sched.tick()
    assert job_store.outbox_count() == 0
    assert sent == [1]


def test_scheduler_does_nothing_when_disabled():
    sent: list = []
    sched = monitor_push.MonitorScheduler(
        lambda: {"server": {}}, clock=lambda: NOW, sender=lambda config: sent.append(1) or {}
    )
    sched.tick()
    assert sent == []
    assert job_store.outbox_count() == 0


def test_scheduler_tick_survives_config_errors():
    def bad_config():
        raise RuntimeError("sin config")

    monitor_push.MonitorScheduler(bad_config).tick()  # no debe lanzar


def test_start_scheduler_is_idempotent_and_stops_fast():
    calls: list[int] = []
    sched = monitor_push.MonitorScheduler(lambda: {"server": {}}, wake_seconds=0.01)
    sched.tick = lambda: calls.append(1)
    assert sched.start() is True
    assert sched.start() is False
    deadline = time.time() + 1
    while not calls and time.time() < deadline:
        time.sleep(0.01)
    assert calls
    sched.stop()
    assert sched.is_running() is False


def test_module_start_scheduler_returns_single_instance(monkeypatch):
    monkeypatch.setattr(monitor_push, "SCHEDULER_WAKE_SECONDS", 3600)
    first = monitor_push.start_scheduler(lambda: {"server": {}})
    second = monitor_push.start_scheduler(lambda: {"server": {}})
    assert first is second
    assert first.is_running()
    monitor_push.stop_scheduler()
    assert first.is_running() is False
