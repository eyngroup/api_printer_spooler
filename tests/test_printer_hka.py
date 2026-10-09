"""
Unit tests for TFHKA printed-total reading (data.total), emulating the real HKA80 responses.

The S1/S2 texts below are the exact frames captured from a fiscalized HKA80 (2026-10-09) while issuing
invoice 998 (exempt 1.00 paid in divisa -> TOTAL 1,03) and invoice 999 (exempt 2.00, Bs 1.00 + divisa
-> TOTAL 2,03). Only the serial transport is emulated; the controller's own parsers are exercised.
"""

import json
from pathlib import Path

import pytest

from controllers.pfhka import FiscalPrinterHka
from printers.printer_commands import HKAcmd
from printers.printer_hka import TfhkaPrinter

# Real S2 after the divisa payment and before 199 (invoice 998: single divisa payment)
S2_AFTER_PAYMENT_998 = "S2 0000000000100\n 0000000000000\n 0000000000103\n000000\n 0000000000000\n0001\n1\n"
# Real S2 after both payments and before 199 (invoice 999: Bs 1.00 partial + divisa full)
S2_AFTER_PAYMENTS_999 = "S2 0000000000200\n 0000000000000\n 0000000000203\n000000\n 0000000000000\n0002\n1\n"
# Real S1 after invoice 999 was closed (RIF and machine register anonymized)
S1_AFTER_999 = (
    "S100\n00000000061891800\n00000999\n00005\n00000005\n00000\n00000144\n00001\n00000201\n00001\n"
    "0002\n0147\nJ-000000000\nZ7C0000000\n124703\n091026\n"
)


class FakeTransportController(FiscalPrinterHka):
    """Real HKA controller whose serial transport is replaced by recorded responses."""

    def __init__(self, s2: str | bool = S2_AFTER_PAYMENT_998, s1: str = S1_AFTER_999):
        super().__init__("emulated")
        self.s2 = s2
        self.s1 = s1
        self.sent: list[str] = []

    def send_cmd(self, command: str, retries: int = 3) -> bool | str:
        """Record the command; status reads return the captured frame text, writes are ACKed."""
        self.sent.append(command)
        if command == "S2":
            return self.s2
        if command == "S1":
            return self.s1
        return True


@pytest.fixture
def printer() -> TfhkaPrinter:
    """TfhkaPrinter without serial initialization, IGTF enabled (flag 50 = 01) as on the HKA80."""
    instance = TfhkaPrinter.__new__(TfhkaPrinter)
    instance._printer = FakeTransportController()
    instance.template_config = {"format": {}}
    instance.printer = "TFHKA"
    instance._flag_50 = "01"
    instance._flag_21 = "00"  # valor real de la HKA80 (S3)
    config_dir = Path(__file__).parents[1] / "config"
    instance.flag_config = json.loads((config_dir / "hka_flag_21.json").read_text())
    instance.max_char_config = json.loads((config_dir / "hka_max_char.json").read_text())
    instance._model = "HKA-80"  # modelo que reporta la máquina real
    instance._printed_total = None
    return instance


def test_single_divisa_payment_reads_total_before_close(printer: TfhkaPrinter):
    """S2 is read after the last payment and before 199; its field 2 is the printed TOTAL (1,03)."""
    printer._process_payments({"payments": [{"payment_method": "20", "payment_amount": 1.03}]}, "invoice")
    assert printer._printer.sent == ["120", "S2", HKAcmd.IGTF_CLOSE]
    assert printer._printed_total == pytest.approx(1.03)


def test_mixed_payment_reads_real_igtf_total(printer: TfhkaPrinter):
    """With Bs + divisa payments the total read after the last payment includes the real IGTF (2,03)."""
    printer._printer = FakeTransportController(s2=S2_AFTER_PAYMENTS_999)
    payments = [
        {"payment_method": "01", "payment_amount": 1.0},
        {"payment_method": "20", "payment_amount": 1.03},
    ]
    printer._process_payments({"payments": payments}, "invoice")
    # El driver ordena los pagos por código descendente: parcial en divisa y pago total en Bs.
    # El ancho del monto (12 dígitos, flag 21 = 00) es el mismo de la trama real "201000000000100".
    assert printer._printer.sent == ["220000000000103", "101", "S2", HKAcmd.IGTF_CLOSE]
    assert printer._printed_total == pytest.approx(2.03)


def test_without_igtf_flag_no_extra_read(printer: TfhkaPrinter):
    """Flag 50 != 01: the last payment closes the document, so S2 is not read and no total is set."""
    printer._flag_50 = "00"
    printer._process_payments({"payments": [{"payment_method": "01", "payment_amount": 1.0}]}, "invoice")
    assert printer._printer.sent == ["101"]
    assert printer._printed_total is None


@pytest.mark.parametrize("s2", [False, "S2 basura\n", ""])
def test_unreadable_s2_never_breaks_the_print(printer: TfhkaPrinter, s2):
    """A failed or malformed S2 read leaves the total empty and the document is still closed."""
    printer._printer = FakeTransportController(s2=s2)
    printer._process_payments({"payments": [{"payment_method": "20", "payment_amount": 1.03}]}, "invoice")
    assert printer._printer.sent[-1] == HKAcmd.IGTF_CLOSE
    assert printer._printed_total is None


def test_send_data_includes_total_when_read(printer: TfhkaPrinter):
    """The response carries data.total (with IGTF) next to the fiscal data read from the real S1."""
    printer._printed_total = 2.03
    result = printer._process_send_data("invoice")
    assert result["status"] is True
    assert result["data"]["document_number"] == "00000999"
    assert result["data"]["machine_report"] == "0148"
    assert result["data"]["total"] == pytest.approx(2.03)


def test_send_data_omits_total_when_unknown(printer: TfhkaPrinter):
    """Without a machine total the key is omitted so Odoo falls back to its own calculation."""
    result = printer._process_send_data("invoice")
    assert "total" not in result["data"]


def test_print_document_resets_total_between_documents(printer: TfhkaPrinter, monkeypatch: pytest.MonkeyPatch):
    """The singleton must not carry the previous document's total into the next one."""
    printer._printed_total = 9.99  # total del documento anterior
    printer._flag_50 = "00"  # sin IGTF: este documento no lee S2
    ready = {"status_code": 96, "error_code": 64, "status": "Lista", "error": "Sin error"}
    monkeypatch.setattr(printer, "get_printer_status", lambda: ready)
    for step in ("_process_customer_data", "_process_items", "_process_footer"):
        monkeypatch.setattr(printer, step, lambda *args, **kwargs: None)

    result = printer.print_document(
        {"operation_type": "invoice", "payments": [{"payment_method": "01", "payment_amount": 1.0}]}
    )
    assert result["status"] is True
    assert "total" not in result["data"]
    assert printer._printed_total is None


# Prefijo de tasa por tipo de documento según el manual TFHKA v8.5.0 (págs. 33-39):
# exento, general (16 %), reducida (8 %), adicional (31 %).
MANUAL_TAX_PREFIXES = {
    "invoice": {0.0: " ", 16.0: "!", 8.0: '"', 31.0: "#"},
    "credit": {0.0: "d0", 16.0: "d1", 8.0: "d2", 31.0: "d3"},
    "debit": {0.0: "`0", 16.0: "`1", 8.0: "`2", 31.0: "`3"},
}


@pytest.mark.parametrize(
    ("operation_type", "tax", "prefix"),
    [(op, tax, prefix) for op, rates in MANUAL_TAX_PREFIXES.items() for tax, prefix in rates.items()],
)
def test_item_tax_prefix_matches_manual(printer: TfhkaPrinter, operation_type: str, tax: float, prefix: str):
    """Each contract tax rate (float percent, as Odoo sends it) maps to the manual's machine rate prefix."""
    item = {"item_name": "Producto", "item_quantity": 1.0, "item_price": 1.0, "item_tax": tax}
    printer._process_items({"items": [item]}, operation_type)
    item_line = printer._printer.sent[0]
    assert item_line.startswith(prefix)
    assert item_line[len(prefix) : len(prefix) + 10].isdigit()  # Seguido del precio
