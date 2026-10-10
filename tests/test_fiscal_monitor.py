"""
Pruebas del monitor fiscal: parsers con respuestas reales (RIF y serial anonimizados), caché, extracción
U0X del controlador con un puerto serial simulado y el endpoint /api/monitor. Nunca se abre un puerto real.
"""

from datetime import datetime
from unittest.mock import MagicMock

import pytest

from controllers.pfhka import FiscalPrinterHka
from server.config_loader import ConfigManager
from server.handlers import fiscal_monitor as fm
from server.handlers import job_store
from server.handlers.fiscal_monitor import FiscalMonitor
from server.handlers.printer_manager import PrinterManager
from server.server_api import create_app

# Respuestas reales capturadas en una HKA80 (flag 63 = 00); RIF y serial anonimizados.
U0X_TEXT = (
    "0148\n261008\n1809\n00001006\n261009\n1453\n00000006\n00000150\n00000202\n"
    "0000000000800\n0000119844450\n0000019175112\n0000000000000\n0000000000000\n0000000000000\n0000000000000\n"
    "0000000000000\n0000000000000\n0000000000000\n0000000000000\n0000000000000\n0000000000000\n0000000000000\n"
    "0000000000800\n0000000000000\n0000000000000\n0000000000000\n0000000000000\n0000000000000\n0000000000000\n"
)
S1_DICT = {
    "status_cajero": "00",
    "ultima_factura": "00001006",
    "facturas_dia": "00012",
    "ultima_nota_debito": "00000006",
    "notas_debito_dia": "00001",
    "ultima_nota_credito": "00000150",
    "notas_credito_dia": "00007",
    "ultimo_doc_no_fiscal": "00000202",
    "docs_no_fiscales_dia": "00002",
    "contador_reportes_memoria": "0002",
    "contador_cierres_z": "0147",
    "rif": "J-00000000-0",
    "registro_maquina": "Z7C0000000",
    "hora_impresora": "152227",
    "fecha_impresora": "091026",
}
S3_TEXT = (
    "S321600\n20800\n23100\n"
    "00000000000000000000000000000000000000000000000000000000000001000000000000000000000000020000000000000100000000000000000000000000\n"
)
EXPECTED_FLAGS = {"30": "01", "43": "02", "50": "01"}
S4_TEXT = "S4" + "\n".join(["0000000000000"] * 3 + ["0000071794140"] + ["0000000000000"] * 20) + "\n"
S5_TEXT = "S5J-00000000-0\nZ7C0000000\n0001\n1908\n1835\n001348\n"


def _raw(now_machine: str = "152227") -> dict:
    """Lecturas crudas equivalentes a las que entrega PrinterManager.read_monitor_data."""
    s1 = dict(S1_DICT, hora_impresora=now_machine)
    s3 = {"General [Percibido]": "16.00", "Reducido [Percibido]": "08.00", "Adicional [Percibido]": "31.00"}
    for n in range(64):
        s3[f"flag_{n}"] = "00"
    s3["flag_30"] = "01"
    return {
        "s1": s1,
        "s3": s3,
        "s4": {f"{i:02d}": line for i, line in enumerate(S4_TEXT[2:].strip().split("\n"), start=1)},
        "s5": {
            "rif": "J-00000000-0",
            "serial": "Z7C0000000",
            "numero_memoria_auditoria": "0001",
            "capacidad_mb_memoria": "1908",
            "disponible_mb_memoria": "1835",
            "documentos_registrados": "001348",
        },
        "sv": {"modelo": "HKA-80", "pais": "VE"},
        "u0x": U0X_TEXT,
    }


# --- Parsers ---------------------------------------------------------------------------------------


def test_parse_x_report_real_frame():
    x = fm.parse_x_report(U0X_TEXT)
    assert x["next_z"] == "0148"
    assert x["last_z_date"] == "2026-10-08"
    assert x["last_z_time"] == "18:09"
    assert x["last_invoice"] == {"number": "00001006", "date": "2026-10-09", "time": "14:53"}
    assert x["last_debit_note"] == "00000006"
    assert x["last_credit_note"] == "00000150"
    assert x["last_non_fiscal"] == "00000202"
    assert x["sales"]["exento"] == 8.00
    assert x["sales"]["rates"][0] == {"rate_index": 1, "base": 1198444.50, "tax": 191751.12}
    assert x["credit"]["exento"] == 8.00
    assert x["debit"]["total"] == 0.0
    assert x["sales"]["total"] == 1390203.62


def test_parse_x_report_ignores_extra_fields_and_rejects_short():
    assert fm.parse_x_report(U0X_TEXT + "0000000000000\n")["next_z"] == "0148"
    with pytest.raises(ValueError):
        fm.parse_x_report("0148\n261008\n")


def test_parse_s4_s5_s3():
    s4 = fm.parse_s4(S4_TEXT)
    assert len(s4) == 24
    assert s4[3] == {"code": "04", "amount": 717941.40, "divisa": False}
    assert s4[19]["divisa"] is True and s4[18]["divisa"] is False

    s5 = fm.parse_s5(S5_TEXT)
    assert (s5["serial"], s5["capacity_mb"], s5["free_mb"], s5["documents"]) == ("Z7C0000000", 1908, 1835, 1348)

    s3 = fm.parse_s3(S3_TEXT)
    assert s3["rates"][0] == {"name": "General", "type": "Excluido", "percent": 16.0}  # tipo 2, verificado en HKA80
    assert s3["rates"][2]["percent"] == 31.0
    assert s3["flags"] == EXPECTED_FLAGS  # solo flags distintos de cero


def test_build_snapshot_computed_fields():
    now = datetime(2026, 10, 9, 15, 22, 0)  # noqa: DTZ001 - hora local de la máquina, sin zona
    snap = fm.build_snapshot(_raw(), now=now)
    assert snap["available"] is True and snap["stale"] is False
    assert snap["machine"]["model"] == "HKA-80"
    assert snap["machine"]["time_drift_seconds"] == 27
    assert snap["machine"]["flags"] == {"30": "01"}
    # venta neta = ventas - créditos + débitos
    assert snap["pre_z"]["net_sales"] == round(1390203.62 - 8.00, 2)
    assert snap["payments_total"] == 717941.40
    assert snap["divisa_total"] == 0.0
    assert snap["counters"]["next_z"] == "0148"


# --- Servicio y caché ------------------------------------------------------------------------------

FISCAL_CFG = {"fiscal": {"fiscal_enabled": True, "fiscal_name": "TFHKA", "fiscal_port": "X"}}


@pytest.fixture
def monitor(monkeypatch):
    """Servicio limpio con la máquina y el job store simulados."""
    FiscalMonitor.reset()
    reader = MagicMock(side_effect=lambda *a, **k: _raw())
    monkeypatch.setattr(PrinterManager, "read_monitor_data", reader)
    busy = MagicMock(return_value=False)
    monkeypatch.setattr(job_store, "has_processing_jobs", busy)
    yield reader, busy
    FiscalMonitor.reset()


def test_cache_prevents_second_read(monitor):
    reader, _ = monitor
    first = FiscalMonitor.get_snapshot(FISCAL_CFG)
    second = FiscalMonitor.get_snapshot(FISCAL_CFG)
    assert first["available"] and second["available"]
    assert reader.call_count == 1


def test_good_read_remembers_machine_serial(monitor):
    """Una lectura buena guarda el serial real de la máquina (respaldo del envío a Odoo cuando no responde)."""
    assert FiscalMonitor.last_known_serial() == ""
    snap = FiscalMonitor.get_snapshot(FISCAL_CFG)
    assert FiscalMonitor.last_known_serial() == snap["machine"]["serial"] != ""


def test_force_respects_minimum_interval(monitor, monkeypatch):
    reader, _ = monitor
    clock = {"t": 1000.0}
    monkeypatch.setattr(fm.time, "monotonic", lambda: clock["t"])
    FiscalMonitor.get_snapshot(FISCAL_CFG)
    clock["t"] += fm.MIN_REFRESH_SECONDS - 1
    FiscalMonitor.get_snapshot(FISCAL_CFG, force=True)
    assert reader.call_count == 1
    clock["t"] += 2
    FiscalMonitor.get_snapshot(FISCAL_CFG, force=True)
    assert reader.call_count == 2
    clock["t"] += fm.CACHE_SECONDS + 1
    FiscalMonitor.get_snapshot(FISCAL_CFG)
    assert reader.call_count == 3


def test_no_read_while_printing(monitor, monkeypatch):
    reader, busy = monitor
    clock = {"t": 1000.0}
    monkeypatch.setattr(fm.time, "monotonic", lambda: clock["t"])
    busy.return_value = True
    empty = FiscalMonitor.get_snapshot(FISCAL_CFG)
    assert empty == {"available": False, "reason": "Impresión en curso"}
    busy.return_value = False
    FiscalMonitor.get_snapshot(FISCAL_CFG)
    assert reader.call_count == 1
    clock["t"] += fm.CACHE_SECONDS + 1
    busy.return_value = True
    stale = FiscalMonitor.get_snapshot(FISCAL_CFG)
    assert stale["available"] and stale["stale"] is True
    assert reader.call_count == 1


def test_read_failure_returns_stale_with_error(monitor, monkeypatch):
    reader, _ = monitor
    clock = {"t": 1000.0}
    monkeypatch.setattr(fm.time, "monotonic", lambda: clock["t"])
    FiscalMonitor.get_snapshot(FISCAL_CFG)
    reader.side_effect = lambda *a, **k: None
    clock["t"] += fm.CACHE_SECONDS + 1
    snap = FiscalMonitor.get_snapshot(FISCAL_CFG)
    assert snap["stale"] is True and "error" in snap


def test_pnp_not_available(monitor):
    reader, _ = monitor
    cfg = {"fiscal": {"fiscal_enabled": True, "fiscal_name": "PNP"}}
    snap = FiscalMonitor.get_snapshot(cfg)
    assert snap == {"available": False, "reason": "Monitor fiscal disponible solo para impresoras TFHKA"}
    assert reader.call_count == 0


# --- Controlador: upload_report ----------------------------------------------------------------------


def _frame(text: str, terminator: int = 0x03) -> bytes:
    """Arma una trama STX + texto + terminador + LRC (XOR de texto y terminador)."""
    body = text.encode("latin-1") + bytes([terminator])
    lrc = 0
    for b in body:
        lrc ^= b
    return b"\x02" + body + bytes([lrc])


class FakeSerial:
    """Puerto serial simulado: entrega bytes en orden y registra lo escrito."""

    def __init__(self, *chunks: bytes):
        """Cada ACK escrito libera el siguiente bloque, como la máquina real (espera la confirmación)."""
        self.chunks = list(chunks)
        self.stream = bytearray(self.chunks.pop(0)) if self.chunks else bytearray()
        self.written: list[bytes] = []

    @property
    def in_waiting(self) -> int:
        return len(self.stream)

    def read(self, n: int = 1) -> bytes:
        out = bytes(self.stream[:n])
        del self.stream[:n]
        return out

    def write(self, data: bytes) -> int:
        self.written.append(bytes(data))
        if data == b"\x06" and self.chunks:
            self.stream.extend(self.chunks.pop(0))
        return len(data)

    def setRTS(self, value):
        pass

    def flushInput(self):
        pass

    def flushOutput(self):
        pass

    def reset_input_buffer(self):
        pass

    def reset_output_buffer(self):
        pass


def _controller(*chunks: bytes) -> tuple[FiscalPrinterHka, FakeSerial]:
    ctrl = FiscalPrinterHka("X")
    ctrl.serial_printer = FakeSerial(*chunks)
    return ctrl, ctrl.serial_printer


def test_upload_report_enq_frame_ack(monkeypatch):
    ctrl, ser = _controller(b"\x05", _frame(U0X_TEXT))
    assert ctrl.upload_report("U0X") == U0X_TEXT
    assert ser.written[0] == _frame("U0X")  # trama enviada
    assert ser.written[1:] == [b"\x06", b"\x06"]  # ACK a ENQ y ACK a la trama


def test_upload_report_etb_blocks_until_eot():
    ctrl, ser = _controller(b"\x05", _frame("AAA\n", 0x17), _frame("BBB\n", 0x17), b"\x04")
    assert ctrl.upload_report("U0X4") == "AAA\nBBB\n"
    assert ser.written[1:] == [b"\x06", b"\x06", b"\x06"]


def test_upload_report_bad_lrc_and_nak():
    bad = bytearray(_frame(U0X_TEXT))
    bad[-1] ^= 0xFF
    ctrl, ser = _controller(b"\x05", bytes(bad))
    assert ctrl.upload_report("U0X") is None
    assert ser.written[-1] == b"\x15"

    ctrl, ser = _controller(b"\x15")  # NAK en lugar de ENQ
    assert ctrl.upload_report("U0X") is None


def test_upload_report_rejects_disallowed_commands():
    ctrl, ser = _controller(b"")
    for cmd in ("U0Z", "I0Z", "U1X", "S1"):
        with pytest.raises(ValueError):
            ctrl.upload_report(cmd)
    assert ser.written == []


def test_get_s4_reads_24_accumulators():
    text = "S4" + "\n".join(["0000000000000"] * 3 + ["0000071794140"] + ["0000000000000"] * 20) + "\n"
    ctrl, _ = _controller(b"")
    ctrl._read_status = lambda cmd: text
    s4 = ctrl.get_s4()
    assert len(s4) == 24 and s4["04"] == "0000071794140"


# --- Endpoint --------------------------------------------------------------------------------------


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(job_store, "_DB_PATH", tmp_path / "monitor_jobs.db")
    job_store.init_db()
    config = dict(ConfigManager.get_config())
    app = create_app(config)
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_monitor_endpoint(client, monkeypatch):
    mock = MagicMock(return_value={"available": True, "stale": False})
    monkeypatch.setattr(FiscalMonitor, "get_snapshot", mock)
    resp = client.get("/api/monitor")
    assert resp.status_code == 200 and resp.get_json()["available"] is True
    assert mock.call_args.kwargs["force"] is False
    client.get("/api/monitor?refresh=1")
    assert mock.call_args.kwargs["force"] is True


def test_monitor_endpoint_unavailable_is_200(client, monkeypatch):
    monkeypatch.setattr(FiscalMonitor, "get_snapshot", MagicMock(return_value={"available": False, "reason": "x"}))
    resp = client.get("/api/monitor")
    assert resp.status_code == 200 and resp.get_json()["reason"] == "x"


def test_parse_s3_controller_dict_uses_verified_rate_type():
    """El diccionario de get_s3 etiqueta el tipo 2 como [Incluido] (Tabla 19); en la HKA80 el tipo 2 es excluido."""
    from server.handlers.fiscal_monitor import parse_s3

    controller_dict = {"General [Incluido]": "16.00", "Reducido [Incluido]": "08.00", "flag_50": "01", "flag_21": "00"}
    result = parse_s3(controller_dict)
    assert result["rates"][0] == {"name": "General", "type": "Excluido", "percent": 16.0}
    assert result["flags"] == {"50": "01"}


# --- Etiquetas de medios de pago ---------------------------------------------------------------------


def test_defaults_file_has_24_labels_and_passes_schema():
    """El archivo de defaults trae las 24 etiquetas y cumple el esquema de configuración."""
    import json
    import os

    from jsonschema import validate

    from handy.runtime_files import default_path_for
    from handy.tools import get_base_path
    from server.config_loader import CONFIG_SCHEMA, FALLBACK_PAYMENT_LABELS

    path = os.path.join(get_base_path(), *default_path_for("config/config.json").split("/"))
    with open(path, encoding="utf-8") as f:
        defaults = json.load(f)
    validate(defaults, CONFIG_SCHEMA)
    labels = defaults["printers"]["fiscal"]["payment_labels"]
    assert list(labels) == [f"{n:02d}" for n in range(1, 25)]
    assert labels["04"] == "Contado" and labels["24"] == "DivisaCashea"
    assert labels == FALLBACK_PAYMENT_LABELS


def test_schema_rejects_bad_payment_labels():
    """El esquema rechaza códigos fuera de 01..24 y valores que no son texto."""
    import copy
    import json
    import os

    from jsonschema import ValidationError, validate

    from handy.runtime_files import default_path_for
    from handy.tools import get_base_path
    from server.config_loader import CONFIG_SCHEMA

    with open(os.path.join(get_base_path(), *default_path_for("config/config.json").split("/")), encoding="utf-8") as f:
        base = json.load(f)
    for bad in ({"25": "x"}, {"1": "x"}, {"01": 5}):
        cfg = copy.deepcopy(base)
        cfg["printers"]["fiscal"]["payment_labels"] = bad
        with pytest.raises(ValidationError):
            validate(cfg, CONFIG_SCHEMA)
    cfg = copy.deepcopy(base)
    del cfg["printers"]["fiscal"]["payment_labels"]
    validate(cfg, CONFIG_SCHEMA)  # es opcional


def test_get_payment_labels_merges_overrides_and_fallbacks(monkeypatch):
    """Los overrides pisan por código (vacío = sin etiqueta); sin clave o sin archivo se usan los defaults."""
    from server import config_loader as cl

    assert cl.get_payment_labels({})["04"] == "Contado"
    assert cl.get_payment_labels(None)["01"] == "Efectivo"
    cfg = {"printers": {"fiscal": {"payment_labels": {"04": "Caja", "05": "", "99": "x"}}}}
    labels = cl.get_payment_labels(cfg)
    assert labels["04"] == "Caja" and labels["05"] == "" and labels["01"] == "Efectivo" and "99" not in labels

    monkeypatch.setattr(cl, "get_base_path", lambda: "/ruta/que/no/existe")
    fallback = cl.get_payment_labels({"printers": {"fiscal": {"payment_labels": {"04": "Caja"}}}})
    assert fallback["04"] == "Caja" and fallback["24"] == "DivisaCashea" and len(fallback) == 24


def test_snapshot_payments_include_labels():
    """build_snapshot y get_snapshot agregan "label" a cada pago."""
    snap = fm.build_snapshot(_raw(), payment_labels={"04": "Contado"})
    assert snap["payments"][3]["label"] == "Contado" and snap["payments"][0]["label"] == ""
    assert all("label" in p for p in snap["payments"])


def test_get_snapshot_applies_current_labels(monitor):
    """El monitor aplica las etiquetas vigentes de la configuración, incluso sobre la caché."""
    fiscal = {"fiscal_enabled": True, "fiscal_name": "TFHKA"}
    first = FiscalMonitor.get_snapshot({"fiscal": fiscal})
    assert first["payments"][3]["label"] == "Contado"
    second = FiscalMonitor.get_snapshot({"fiscal": {**fiscal, "payment_labels": {"04": "Caja"}}})
    assert second["payments"][3]["label"] == "Caja"
