"""Tests de la detección de puerto fiscal (find_fiscal_port y autodetect_serial_port) sin hardware real."""

from types import SimpleNamespace

import pytest

import main
from handy import serial_scan


def fake_port(device, vid=None, pid=None, description="n/a", hwid=""):
    """Crea un puerto falso con los atributos de ListPortInfo."""
    return SimpleNamespace(device=device, vid=vid, pid=pid, description=description, hwid=hwid)


HKA = fake_port("COM3", 0x28E9, 0x018A, "Dispositivo serie USB (COM3)", "USB VID:PID=28E9:018A")
BT = fake_port("COM4", None, None, "Vínculo serie estándar sobre Bluetooth (COM4)", "BTHENUM\\{00001101}")


def make_fake(kind, responding, probed, raising=()):
    """Fabrica un controlador falso que registra los puertos abiertos y responde solo en ``responding``."""

    class Fake:
        def __init__(self, port, baudrate, timeout):
            self.port = port

        def open_port(self):
            probed.append(self.port)
            if self.port in raising:
                raise RuntimeError("boom")
            return True

        def get_status(self):
            if self.port in responding:
                return {"status_code": 96 if kind == "hka" else "0000"}
            return {"status_code": 0, "error_code": 137} if kind == "hka" else None

        def close_port(self):
            pass

    return Fake


@pytest.fixture
def probed(monkeypatch):
    """Registro de puertos sondeados; instala los controladores falsos."""
    return []


def install(monkeypatch, ports, probed, responding, kind="hka", raising=()):
    """Instala puertos y controlador falsos."""
    monkeypatch.setattr(serial_scan.list_ports, "comports", lambda: ports)
    fake = make_fake(kind, responding, probed, raising)
    monkeypatch.setattr(serial_scan, "FiscalPrinterHka" if kind == "hka" else "FiscalPrinterPnp", fake)


def test_spanish_windows_picks_native_usb_not_bluetooth(monkeypatch, probed):
    install(monkeypatch, [BT, HKA], probed, {"COM3"})
    assert serial_scan.find_fiscal_port("tfhka", None) == "COM3"
    assert "COM4" not in probed


def test_current_port_confirmed_is_kept_without_probing_others(monkeypatch, probed):
    other = fake_port("COM9", 0x067B, 0x2303, "Prolific")
    install(monkeypatch, [other, HKA], probed, {"COM3", "COM9"})
    assert serial_scan.find_fiscal_port("tfhka", "COM3") == "COM3"
    assert probed == ["COM3"]


def test_unconfirmed_returns_none_and_bluetooth_never_probed(monkeypatch, probed):
    install(monkeypatch, [BT, HKA], probed, set())
    assert serial_scan.find_fiscal_port("tfhka", None) is None
    assert probed == ["COM3"]


def test_probe_exception_moves_to_next_candidate(monkeypatch, probed):
    other = fake_port("COM9", 0x067B, 0x2303, "Prolific")
    install(monkeypatch, [HKA, other], probed, {"COM9"}, raising={"COM3"})
    assert serial_scan.find_fiscal_port("tfhka", None) == "COM9"
    assert probed == ["COM3", "COM9"]


def test_pnp_uses_pnp_controller(monkeypatch, probed):
    install(monkeypatch, [HKA], probed, {"COM3"}, kind="pnp")
    monkeypatch.setattr(serial_scan, "FiscalPrinterHka", None)
    assert serial_scan.find_fiscal_port("pnp", None) == "COM3"


def _config(port="COM1", name="TFHKA"):
    return {
        "server": {"scan_serial_port": True},
        "printers": {"fiscal": {"fiscal_name": name, "fiscal_port": port, "fiscal_baudrate": 9600}},
    }


def test_autodetect_saves_only_confirmed_different_port(monkeypatch, probed):
    saved = []
    monkeypatch.setattr(main.ConfigManager, "save_config", lambda c: saved.append(c))
    install(monkeypatch, [HKA], probed, {"COM3"})
    config = _config("COM1")
    main.autodetect_serial_port(config)
    assert config["printers"]["fiscal"]["fiscal_port"] == "COM3"
    assert len(saved) == 1


def test_autodetect_unconfirmed_does_not_save(monkeypatch, probed):
    saved = []
    monkeypatch.setattr(main.ConfigManager, "save_config", lambda c: saved.append(c))
    install(monkeypatch, [HKA], probed, set())
    config = _config("COM1")
    main.autodetect_serial_port(config)
    assert config["printers"]["fiscal"]["fiscal_port"] == "COM1"
    assert saved == []
