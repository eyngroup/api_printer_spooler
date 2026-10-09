"""
Unit tests for PNP fiscal printer response handling (no serial port required).
"""

import pytest

from printers import printer_pnp
from printers.printer_commands import PNPcmd
from printers.printer_pnp import PnpPrinter

# Close-command responses per PNP manual v5.4 (fields after the command byte)
CLOSE_0x45 = ["0080", "0600", "0003", "0000001234", "0000000056", "0.00"]
CLOSE_0x4A = ["0080", "0600", "0000000789"]


class FakeController:
    """Simulated FiscalPrinterPnp that returns queued responses."""

    def __init__(self, responses: dict[str, list[str]] | None = None, default: list[str] | None = None):
        self.responses = responses or {}
        self.default = default if default is not None else ["0080", "0600"]
        self.sent: list[str] = []

    def send_cmd(self, command: str) -> list[str]:
        """Record the command and return its configured response."""
        self.sent.append(command)
        return self.responses.get(command, self.default)


@pytest.fixture
def printer(monkeypatch: pytest.MonkeyPatch) -> PnpPrinter:
    """PnpPrinter instance without serial initialization."""
    monkeypatch.setattr(printer_pnp.time, "sleep", lambda _: None)
    instance = PnpPrinter.__new__(PnpPrinter)
    instance._printer = FakeController()
    instance._type_doc = None
    instance._last_document = "0000000000"
    instance._last_response = []
    return instance


def test_error_response_is_rejected(printer: PnpPrinter):
    """A negative response containing 'ERROR' must not be treated as success."""
    printer._printer = FakeController(default=["0080", "0600", "0001", "ERROR01"])
    printer._type_doc = "invoice"
    assert printer.send_command(PNPcmd.CLOSE_TOTAL) is False
    assert printer._last_document == "0000000000"


def test_non_close_command_does_not_set_document_number(printer: PnpPrinter):
    """Commands with extra fields (e.g. subtotal) must not overwrite the document number."""
    printer._printer = FakeController(default=["0080", "0600", "000000010000", "000000001600"])
    printer._type_doc = "invoice"
    assert printer.send_command("C") is True
    assert printer._last_document == "0000000000"


@pytest.mark.parametrize(
    ("doc_type", "response", "expected"),
    [
        ("note", CLOSE_0x4A, "0000000789"),
        ("invoice", CLOSE_0x45, "0000001234"),
        ("debit", CLOSE_0x45, "0000001234"),
        ("credit", CLOSE_0x45, "0000000056"),
    ],
)
def test_extract_document_number_per_type(printer: PnpPrinter, doc_type: str, response: list[str], expected: str):
    """Document number field matches the PNP manual for each document type."""
    printer._type_doc = doc_type
    assert printer._extract_document_number(response) == expected


def test_extract_document_number_short_response(printer: PnpPrinter):
    """A short close response (older firmware) falls back without raising."""
    printer._type_doc = "credit"
    assert printer._extract_document_number(["0080", "0600", "0003", "0000001234"]) == "0000000000"


@pytest.mark.parametrize(
    ("doc_type", "close_cmd", "response", "expected"),
    [
        ("debit", PNPcmd.CLOSE_TOTAL, CLOSE_0x45, "0000001234"),
        ("note", PNPcmd.DNF_CLOSE, CLOSE_0x4A, "0000000789"),
    ],
)
def test_process_payments_sets_number_from_close(
    printer: PnpPrinter, doc_type: str, close_cmd: str, response: list[str], expected: str
):
    """The document number is taken from the close command response."""
    printer._printer = FakeController(responses={close_cmd: response})
    printer._type_doc = doc_type
    printer._process_payments({"payments": [{"payment_method": "01", "payment_amount": 10.0}]})
    assert printer._last_document == expected
