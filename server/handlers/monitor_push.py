#!/usr/bin/env python
"""
Copyright © 2024, Iron Graterol
Licensed under the GNU Affero General Public License, version 3 or later.

Envío (push) de las lecturas del monitor fiscal a Odoo.
Cada lectura se guarda primero en la cola SQLite (monitor_outbox) y luego se envía por HTTPS con reintentos.
Contrato: odd/monitor-push-contract.md (versión 1.0). El monitor nunca debe interferir con la impresión:
ninguna función pública de este módulo lanza excepciones hacia quien la llama.
"""

import logging
import socket
import threading
import time
import uuid
from collections.abc import Callable
from datetime import datetime, timedelta
from typing import Any

import requests

from handy.version import __version__
from server.config_loader import ConfigManager, get_monitor_push_config

from . import job_store
from .fiscal_monitor import FiscalMonitor

logger = logging.getLogger(__name__)

CONTRACT_VERSION = "1.0"
VALID_TRIGGERS = ("scheduled", "manual", "after_z", "before_z")
REQUEST_TIMEOUT_SECONDS = 15
# Máximo una solicitud cada 5 s mientras se vacía la cola (sin ráfagas tras una caída)
MIN_SECONDS_BETWEEN_REQUESTS = 5
# Espera (minutos) tras el 1.er, 2.º, 3.er, 4.º y 5.º fallo; después se usa el intervalo configurado
BACKOFF_MINUTES = (1, 2, 5, 10, 30)
# Cada cuántos segundos despierta el hilo para reintentar lo pendiente
SCHEDULER_WAKE_SECONDS = 30

_state_lock = threading.Lock()
_state: dict[str, Any] = {
    "last_attempt_at": None,
    "last_result": "Sin envíos todavía",
    "paused_unauthorized": False,
    "paused_token": None,
}
# Evita dos vaciados de la cola a la vez (hilo del planificador y botón "Enviar ahora")
_send_lock = threading.Lock()


def _now() -> datetime:
    """
    Devuelve la hora local actual (sin zona horaria, como el resto del código).
    Returns:
        datetime: Hora local
    """
    return datetime.now()  # noqa: DTZ005 - hora local, como el resto del spooler


def _format_offset(now: datetime) -> str:
    """
    Calcula el desfase de la zona horaria local respecto a UTC con formato ±HH:MM.
    Args:
        now: Hora local de referencia
    Returns:
        str: Desfase, p. ej. "-04:00"
    """
    offset = now.astimezone().utcoffset() or timedelta(0)
    minutes = int(offset.total_seconds() // 60)
    sign = "-" if minutes < 0 else "+"
    hours, mins = divmod(abs(minutes), 60)
    return f"{sign}{hours:02d}:{mins:02d}"


def _machine_serial(snapshot: dict[str, Any]) -> str:
    """
    Serial de la máquina: el leído en el snapshot o, si no hay lectura, el último leído de la máquina en este proceso
    y, en último caso, el configurado en el template fiscal. Odoo compara SIEMPRE este serial con el del diario
    (también cuando la máquina no respondió); el template puede conservar el serial de ejemplo hasta la primera
    impresión, por eso se prefiere el último serial real.
    Args:
        snapshot: Snapshot del monitor
    Returns:
        str: Serial (o "unknown" si no se pudo determinar)
    """
    serial = ((snapshot or {}).get("machine") or {}).get("serial")
    if (snapshot or {}).get("available") and serial:
        return str(serial)
    last_serial = FiscalMonitor.last_known_serial()
    if last_serial:
        return last_serial
    from server.server_api import _configured_serial  # importación diferida: evita cargar Flask al importar

    return _configured_serial()


def build_envelope(
    snapshot: dict[str, Any], trigger: str, config: dict[str, Any], now: datetime | None = None
) -> dict[str, Any]:
    """
    Construye el cuerpo de la solicitud según el contrato (§4).
    Args:
        snapshot: Snapshot del monitor, tal cual lo devuelve GET /api/monitor
        trigger: scheduled, manual, after_z o before_z
        config: Configuración completa
        now: Hora local de referencia (para pruebas); None usa la hora actual
    Returns:
        dict: Envelope listo para serializar a JSON
    """
    moment = now or _now()
    settings = get_monitor_push_config(config)
    return {
        "contract_version": CONTRACT_VERSION,
        "reading_id": str(uuid.uuid4()),
        "trigger": trigger,
        "sent_at": moment.isoformat(timespec="seconds"),
        "utc_offset": _format_offset(moment),
        "spooler": {
            "version": __version__,
            "host": socket.gethostname(),
            "mode": ((config or {}).get("server") or {}).get("server_mode", "SPOOLER"),
        },
        "branch_code": settings["branch_code"],
        "machine_serial": _machine_serial(snapshot),
        "snapshot": snapshot,
    }


def enqueue_reading(
    trigger: str, config: dict[str, Any], snapshot: dict[str, Any] | None = None, now: datetime | None = None
) -> str | None:
    """
    Arma una lectura y la guarda en la cola de salida. Nunca lanza excepciones: el monitor no debe romper la impresión.
    Args:
        trigger: scheduled, manual, after_z o before_z
        config: Configuración completa
        snapshot: Snapshot ya obtenido (p. ej. lectura nueva previa al Z); None usa la caché del monitor
        now: Hora local de referencia (para pruebas)
    Returns:
        str | None: reading_id encolado, o None si falló
    """
    try:
        if snapshot is None:
            snapshot = FiscalMonitor.get_snapshot((config or {}).get("printers", {}))
        moment = now or _now()
        envelope = build_envelope(snapshot, trigger, config, moment)
        job_store.outbox_enqueue(envelope["reading_id"], trigger, envelope, moment.isoformat(timespec="seconds"))
        job_store.outbox_purge(moment)
        return envelope["reading_id"]
    except Exception as e:  # noqa: BLE001 - el monitor nunca debe interferir con la impresión
        logger.error("Monitor push: no se pudo encolar la lectura '%s': %s", trigger, e)
        return None


def _z_push_config(config: dict[str, Any]) -> dict[str, Any] | None:
    """
    Copia de lo mínimo de la configuración que usan las lecturas ligadas a un Z, o None si no corresponde hacerlas:
    envío deshabilitado o incompleto (sin url o token) o modo PROXY (la máquina está en el spooler destino, que
    envía sus propias lecturas). La copia permite usarla en un hilo sin depender del contexto de Flask.
    Args:
        config: Configuración completa (p. ej. current_app.config)
    Returns:
        dict | None: Copia con printers, server y monitor_push, o None si no hay que leer
    """
    settings = get_monitor_push_config(config)
    if not (settings["enabled"] and settings["url"] and settings["token"]):
        return None
    server = dict((config or {}).get("server") or {})
    if str(server.get("server_mode", "")).upper() == "PROXY":
        return None
    return {
        "printers": dict((config or {}).get("printers") or {}),
        "server": server,
        "monitor_push": dict((config or {}).get("monitor_push") or {}),
    }


def _read_and_enqueue(trigger: str, config: dict[str, Any]) -> str | None:
    """
    Lee la máquina ahora (sin caché) y encola la lectura. Si la máquina no responde o hay una impresión en curso
    no se encola nada: Odoo trata la lectura faltante como "aproximada" y un snapshot no disponible no aporta datos.
    Nunca lanza excepciones.
    Args:
        trigger: before_z o after_z
        config: Copia de configuración devuelta por _z_push_config
    Returns:
        str | None: reading_id encolado, o None si no se encoló
    """
    try:
        snapshot = FiscalMonitor.read_fresh(config.get("printers", {}))
        if not snapshot.get("available"):
            logger.warning("Monitor push: lectura '%s' omitida: %s", trigger, snapshot.get("reason", "sin datos"))
            return None
        return enqueue_reading(trigger, config, snapshot=snapshot)
    except Exception as e:  # noqa: BLE001 - el monitor nunca debe interferir con el Z
        logger.error("Monitor push: error en la lectura '%s': %s", trigger, e)
        return None


def enqueue_before_z(config: dict[str, Any]) -> str | None:
    """
    Lectura nueva justo antes de un Z: el total oficial del día. Solo encola (el planificador la envía después);
    cualquier fallo se registra y el Z continúa igual. Sin envío habilitado no lee la máquina en absoluto.
    Args:
        config: Configuración completa (current_app.config)
    Returns:
        str | None: reading_id encolado, o None si no corresponde o falló
    """
    try:
        push_config = _z_push_config(config)
        if push_config is None:
            return None
        return _read_and_enqueue("before_z", push_config)
    except Exception as e:  # noqa: BLE001 - el monitor nunca debe interferir con el Z
        logger.error("Monitor push: error preparando la lectura previa al Z: %s", e)
        return None


def start_after_z(config: dict[str, Any]) -> threading.Thread | None:
    """
    Tras un Z exitoso: descarta la caché del monitor (ya no refleja la máquina) y, si el envío está habilitado,
    lanza un hilo daemon que lee y encola la lectura "after_z" para no demorar la respuesta HTTP a Odoo. Debe
    llamarse DESPUÉS del ajuste de reloj: tras un Z la máquina solo acepta PF/PG de inmediato. Nunca lanza.
    Args:
        config: Configuración completa (current_app.config)
    Returns:
        threading.Thread | None: Hilo iniciado (para pruebas), o None si no hay lectura que hacer
    """
    try:
        FiscalMonitor.invalidate()
        push_config = _z_push_config(config)
        if push_config is None:
            return None
        thread = threading.Thread(
            target=_read_and_enqueue, args=("after_z", push_config), name="monitor-after-z", daemon=True
        )
        thread.start()
        return thread
    except Exception as e:  # noqa: BLE001 - el monitor nunca debe interferir con el Z
        logger.error("Monitor push: no se pudo iniciar la lectura posterior al Z: %s", e)
        return None


def _set_state(**changes: Any) -> None:
    """
    Actualiza el estado visible en la ventana (hilo seguro).
    Args:
        **changes: Campos de _state a modificar
    """
    with _state_lock:
        _state.update(changes)


def reset_state() -> None:
    """Reinicia el estado en memoria (pausa, último resultado). Sirve para pruebas."""
    _set_state(last_attempt_at=None, last_result="Sin envíos todavía", paused_unauthorized=False, paused_token=None)


def get_status() -> dict[str, Any]:
    """
    Estado del envío para la ventana de escritorio.
    Returns:
        dict: last_attempt_at (ISO o None), last_result (texto), pending (lecturas en cola) y paused (401 activo)
    """
    with _state_lock:
        status = {
            "last_attempt_at": _state["last_attempt_at"],
            "last_result": _state["last_result"],
            "paused": _state["paused_unauthorized"],
        }
    try:
        status["pending"] = job_store.outbox_count()
    except Exception as e:  # noqa: BLE001 - informativo
        logger.warning("Monitor push: no se pudo contar la cola: %s", e)
        status["pending"] = 0
    return status


def _backoff_delay(attempts: int, interval_minutes: int) -> timedelta:
    """
    Espera antes del siguiente intento: 1, 2, 5, 10 y 30 minutos; luego el intervalo configurado.
    Args:
        attempts: Intentos fallidos acumulados (ya incluye el que acaba de fallar)
        interval_minutes: Intervalo configurado
    Returns:
        timedelta: Espera
    """
    index = max(attempts, 1) - 1
    minutes = BACKOFF_MINUTES[index] if index < len(BACKOFF_MINUTES) else interval_minutes
    return timedelta(minutes=minutes)


def _is_paused(token: str) -> bool:
    """
    Indica si el envío está pausado por un 401. Se reanuda solo cuando cambia el token configurado.
    Args:
        token: Token configurado actualmente
    Returns:
        bool: True si sigue pausado
    """
    with _state_lock:
        if not _state["paused_unauthorized"]:
            return False
        if token != _state["paused_token"]:
            _state.update(paused_unauthorized=False, paused_token=None)
            logger.info("Monitor push: token cambiado, se reanuda el envío")
            return False
        return True


def _error_text(response: requests.Response) -> str:
    """
    Extrae un texto corto del cuerpo de error de Odoo para el log.
    Args:
        response: Respuesta HTTP
    Returns:
        str: "code: message" o el código HTTP si el cuerpo no es interpretable
    """
    try:
        body = response.json()
        return f"{body.get('code', '')}: {body.get('message', '')}".strip(": ") or f"HTTP {response.status_code}"
    except Exception:  # noqa: BLE001 - el cuerpo de error es solo informativo
        return f"HTTP {response.status_code}"


def _fail(item: dict[str, Any], error: str, settings: dict[str, Any], now: datetime) -> None:
    """
    Deja la lectura en la cola con espera progresiva y actualiza el estado visible.
    Args:
        item: Fila de la cola
        error: Motivo del fallo
        settings: Ajustes del monitor
        now: Hora local actual
    """
    delay = _backoff_delay(int(item["attempts"]) + 1, settings["interval_minutes"])
    job_store.outbox_mark_failed(item["reading_id"], error, (now + delay).isoformat(timespec="seconds"))
    _set_state(last_result=f"Error: {error}. Se reintenta en {int(delay.total_seconds() // 60)} min")
    logger.warning("Monitor push: envío fallido (%s); reintento en %s", error, delay)


def send_due(
    config: dict[str, Any],
    session: Any = None,
    now: datetime | None = None,
    sleep: Callable[[float], None] = time.sleep,
) -> dict[str, Any]:
    """
    Envía a Odoo, de una en una, las lecturas vencidas de la cola, según las respuestas del contrato (§6).
    200 ok/duplicate -> se elimina; 401 -> pausa hasta cambiar el token; 422 -> se descarta y sigue;
    5xx, timeout o error de red -> espera progresiva y se deja de vaciar la cola. Nunca lanza excepciones.
    Args:
        config: Configuración completa (se lee en cada llamada)
        session: Objeto con .post() compatible con requests; None usa el módulo requests
        now: Hora local de referencia (para pruebas)
        sleep: Función de espera entre envíos (inyectable en pruebas)
    Returns:
        dict: Estado actual (ver get_status)
    """
    try:
        settings = get_monitor_push_config(config)
        if not (settings["enabled"] and settings["url"] and settings["token"]):
            return get_status()
        if _is_paused(settings["token"]):
            return get_status()
        if not _send_lock.acquire(blocking=False):
            return get_status()
        try:
            _drain(settings, session or requests, now, sleep)
        finally:
            _send_lock.release()
    except Exception as e:  # noqa: BLE001 - el monitor nunca debe interferir con el resto del spooler
        logger.error("Monitor push: error inesperado al enviar: %s", e)
        _set_state(last_result=f"Error inesperado: {e}")
    return get_status()


def _drain(settings: dict[str, Any], http: Any, now: datetime | None, sleep: Callable[[float], None]) -> None:
    """
    Recorre la cola de salida enviando las lecturas vencidas hasta vaciarla o hasta un fallo que detenga el envío.
    Args:
        settings: Ajustes del monitor ya normalizados
        http: Objeto con .post()
        now: Hora local de referencia (para pruebas)
        sleep: Función de espera entre envíos
    """
    sent_before = False
    while True:
        moment = now or _now()
        item = job_store.outbox_fetch_due(moment.isoformat(timespec="seconds"))
        if item is None:
            return
        if sent_before:
            sleep(MIN_SECONDS_BETWEEN_REQUESTS)
            moment = now or _now()
        sent_before = True

        body = dict(item["payload"])
        body["sent_at"] = moment.isoformat(timespec="seconds")  # Se refresca en cada (re)envío; reading_id no cambia
        _set_state(last_attempt_at=moment.isoformat(timespec="seconds"))
        try:
            response = http.post(
                settings["url"],
                json=body,
                headers={"Authorization": f"Bearer {settings['token']}"},
                timeout=REQUEST_TIMEOUT_SECONDS,
            )
        except requests.RequestException as e:
            _fail(item, f"sin conexión ({type(e).__name__})", settings, moment)
            return

        code = response.status_code
        if code == 200:
            try:
                result = (response.json() or {}).get("status")
            except Exception:  # noqa: BLE001 - un 200 sin JSON válido no confirma la entrega
                result = None
            if result in ("ok", "duplicate"):
                job_store.outbox_mark_sent(item["reading_id"])
                _set_state(last_result="Enviado correctamente" if result == "ok" else "Enviado (ya registrado)")
                continue
            _fail(item, "respuesta 200 no reconocida", settings, moment)
            return
        if code == 401:
            _set_state(
                paused_unauthorized=True,
                paused_token=settings["token"],
                last_result="Token no autorizado por Odoo: envío en pausa hasta cambiar el token",
            )
            logger.error("Monitor push: Odoo rechazó el token (401); el envío queda en pausa hasta cambiarlo")
            return
        if code == 422:
            reason = _error_text(response)
            job_store.outbox_drop(item["reading_id"], reason)
            _set_state(last_result=f"Lectura rechazada por Odoo (422): {reason}")
            logger.error("Monitor push: Odoo rechazó la lectura %s (422): %s", item["reading_id"], reason)
            continue
        _fail(item, f"HTTP {code}", settings, moment)
        return


def send_now(config: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
    """
    Botón "Enviar ahora": encola una lectura manual y vacía la cola. Nunca lanza excepciones.
    Args:
        config: Configuración completa
        **kwargs: Parámetros opcionales de send_due (session, now, sleep)
    Returns:
        dict: Estado actual (ver get_status)
    """
    settings = get_monitor_push_config(config)
    if settings["enabled"] and settings["url"] and settings["token"]:
        enqueue_reading("manual", config, now=kwargs.get("now"))
    return send_due(config, **kwargs)


class MonitorScheduler:
    """Hilo daemon que encola una lectura cada `interval_minutes` y reintenta lo pendiente al despertar."""

    def __init__(
        self,
        get_config: Callable[[], dict[str, Any]],
        wake_seconds: float = SCHEDULER_WAKE_SECONDS,
        clock: Callable[[], datetime] = _now,
        sender: Callable[..., dict[str, Any]] | None = None,
    ):
        """
        Args:
            get_config: Devuelve la configuración vigente (se lee en cada despertar)
            wake_seconds: Segundos entre despertares
            clock: Reloj local (inyectable en pruebas)
            sender: Función de envío; None usa send_due
        """
        self._get_config = get_config
        self._wake_seconds = wake_seconds
        self._clock = clock
        self._sender = sender or send_due
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._last_scheduled: datetime | None = None

    def tick(self) -> None:
        """Un despertar: si está habilitado y completo, encola la lectura periódica si toca y vacía la cola."""
        try:
            config = self._get_config()
            settings = get_monitor_push_config(config)
            if not (settings["enabled"] and settings["url"] and settings["token"]):
                return
            now = self._clock()
            interval = timedelta(minutes=settings["interval_minutes"])
            # En modo PROXY la máquina está en el spooler destino, que envía sus propias lecturas: aquí solo se
            # vacía lo pendiente, sin encolar lecturas nuevas (evita avisos "solo TFHKA" o rechazos por serial).
            proxy_mode = str(((config or {}).get("server") or {}).get("server_mode", "")).upper() == "PROXY"
            if not proxy_mode and (self._last_scheduled is None or now - self._last_scheduled >= interval):
                self._last_scheduled = now
                enqueue_reading("scheduled", config, now=now)
            self._sender(config)
        except Exception as e:  # noqa: BLE001 - el hilo nunca debe morir por un error puntual
            logger.error("Monitor push: error en el planificador: %s", e)

    def _run(self) -> None:
        """Bucle del hilo: espera (interrumpible) y ejecuta tick hasta que se pida detener."""
        while not self._stop.wait(self._wake_seconds):
            self.tick()

    def start(self) -> bool:
        """
        Inicia el hilo daemon; es idempotente.
        Returns:
            bool: True si lo inició ahora, False si ya estaba corriendo
        """
        if self._thread is not None and self._thread.is_alive():
            return False
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, name="monitor-push", daemon=True)
        self._thread.start()
        logger.info("Monitor push: planificador iniciado")
        return True

    def stop(self, timeout: float | None = 2.0) -> None:
        """
        Pide detener el hilo y espera brevemente.
        Args:
            timeout: Segundos máximos de espera
        """
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout)
            self._thread = None

    def is_running(self) -> bool:
        """
        Indica si el hilo está activo.
        Returns:
            bool: True si corre
        """
        return self._thread is not None and self._thread.is_alive()


_scheduler: MonitorScheduler | None = None
_scheduler_lock = threading.Lock()


def start_scheduler(get_config: Callable[[], dict[str, Any]] | None = None) -> MonitorScheduler:
    """
    Inicia el único planificador del proceso (idempotente). Se llama desde main.py, nunca desde create_app.
    Args:
        get_config: Devuelve la configuración vigente; None usa ConfigManager.get_config
    Returns:
        MonitorScheduler: El planificador en ejecución
    """
    global _scheduler
    with _scheduler_lock:
        if _scheduler is None:
            _scheduler = MonitorScheduler(get_config or ConfigManager.get_config)
        _scheduler.start()
        return _scheduler


def stop_scheduler() -> None:
    """Detiene el planificador del proceso, si existe."""
    global _scheduler
    with _scheduler_lock:
        if _scheduler is not None:
            _scheduler.stop()
            _scheduler = None
