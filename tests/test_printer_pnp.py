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

    def get_status(self) -> dict[str, str | bool]:
        """Emulate a ready printer status (0080 / 0600)."""
        return {
            "status_code": "0080",
            "error_code": "0600",
            "status": "00",
            "status_detallado": "OK",
            "error_critico": False,
            "requiere_servicio": False,
        }

    def get_counters(self) -> dict[str, str]:
        """Emulate the fiscal counters response."""
        return {"ultimo_z": "0010", "fecha_formateada": "2026-01-15"}


@pytest.fixture
def printer(monkeypatch: pytest.MonkeyPatch) -> PnpPrinter:
    """PnpPrinter instance without serial initialization."""
    monkeypatch.setattr(printer_pnp.time, "sleep", lambda _: None)
    instance = PnpPrinter.__new__(PnpPrinter)
    instance._printer = FakeController()
    instance._type_doc = None
    instance._last_document = "0000000000"
    instance._last_response = []
    instance.template_config = {"format": {}}
    instance._model = "PF-220"
    instance._serial = "TEST000001"
    instance.printer = "PNP"
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
    assert printer._extract_document_number(["0080", "0600", "0003", "0000001234"]) == ""  # nunca se inventa un número


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


def _item(price: float, qty: float = 1, discount: float = 0, dtype: str = "") -> dict:
    """Build a minimal fiscal item payload."""
    return {
        "item_name": "Producto",
        "item_quantity": qty,
        "item_price": price,
        "item_tax": 16.0,
        "item_discount": discount,
        "item_discount_type": dtype,
        "item_comment": "nota",
    }


def _item_cmd(printer: PnpPrinter, price: str, qty: str = "1000") -> str:
    """Expected B| command for the item built by _item (tax 16% -> "1600", format XXDD)."""
    return PNPcmd.ITEM_LINE.format(printer._format_text("Producto", "product"), qty, price, "1600")


@pytest.mark.parametrize(
    ("price", "qty", "discount", "dtype", "expected_price"),
    [
        (10.00, 2, 10, "discount_percentage", "900"),
        (10.00, 2, 10, "surcharge_percentage", "1100"),
        (10.00, 2, 1.5, "discount_amount", "850"),
        (10.00, 2, 1.5, "surcharge_amount", "1150"),
        (10.01, 2, 15, "discount_percentage", "851"),  # 8.5085 -> 8.51 (ROUND_HALF_UP)
    ],
)
def test_item_adjustment_sends_adjusted_price(
    printer: PnpPrinter, price: float, qty: int, discount: float, dtype: str, expected_price: str
):
    """Discount/surcharge types send the item line with the adjusted unit price."""
    printer._type_doc = "invoice"
    printer._process_items({"items": [_item(price, qty, discount, dtype)]})
    expected = PNPcmd.ITEM_LINE.format(
        printer._format_text("Producto", "product"), printer._format_number(qty, "quantity"), expected_price, "1600"
    )
    assert printer._printer.sent == [expected]


def test_item_without_discount_is_unchanged(printer: PnpPrinter):
    """An undiscounted item keeps the exact legacy wire format."""
    printer._type_doc = "invoice"
    printer._process_items({"items": [_item(10.5)]})
    assert printer._printer.sent == [_item_cmd(printer, "1050")]
    assert printer._printer.sent[0].startswith("B|Producto|1000|1050|1600|M")


@pytest.mark.parametrize(("discount", "dtype"), [(0, "discount_percentage"), (-5, "discount_amount"), (10, "bogus")])
def test_invalid_adjustment_leaves_price_untouched(printer: PnpPrinter, discount: float, dtype: str):
    """Zero, negative or unknown-type adjustments do not alter the price nor produce text."""
    price, text = printer._apply_item_adjustment(_item(10.0, 1, discount, dtype))
    assert str(price) == "10.00"
    assert text is None


def test_discount_line_only_when_flag_enabled(printer: PnpPrinter):
    """Flag off: no A|DESCUENTO line is sent."""
    printer._type_doc = "invoice"
    printer._process_items({"items": [_item(10.0, 1, 10, "discount_percentage")]})
    assert not any(cmd.startswith("A|DESCUENTO") for cmd in printer._printer.sent)


def test_discount_line_sent_between_item_and_comment(printer: PnpPrinter):
    """Flag on: the info line follows the item line and precedes the item comment."""
    printer.template_config = {"format": {"include_item_discount": True, "include_item_comment": True}}
    printer._type_doc = "invoice"
    printer._process_items({"items": [_item(10.0, 1, 10, "discount_percentage")]})
    assert printer._printer.sent == [
        _item_cmd(printer, "900"),
        "A|DESCUENTO 10,00%",
        PNPcmd.COMMENTS.format(printer._format_text("nota", "comment")),
    ]


def test_failed_item_line_rolls_back_with_adjusted_price(printer: PnpPrinter):
    """A failed item line sends ITEM_LINE_DEL with the adjusted price and raises."""
    printer._type_doc = "invoice"
    item_cmd = _item_cmd(printer, "900")
    printer._printer = FakeController(responses={item_cmd: ["0080", "0600", "0001", "ERROR01"]})
    with pytest.raises(RuntimeError):
        printer._process_items({"items": [_item(10.0, 1, 10, "discount_percentage")]})
    rollback = PNPcmd.ITEM_LINE_DEL.format(printer._format_text("Producto", "product"), "1000", "900", "1600")
    assert printer._printer.sent == [item_cmd, rollback]


def test_print_document_full_flow_with_discount(printer: PnpPrinter):
    """Full invoice flow with a discounted item returns the document number and sends the discounted price."""
    printer._printer = FakeController(responses={PNPcmd.CLOSE_TOTAL: CLOSE_0x45})
    payload = {
        "operation_type": "invoice",
        "customer": {"customer_vat": "V12345678", "customer_name": "Cliente"},
        "document": {"document_number": "INV/0001", "document_date": "2026-01-15"},
        "items": [_item(10.0, 2, 10, "discount_percentage")],
        "payments": [{"payment_method": "01", "payment_amount": 18.0}],
    }
    result = printer.print_document(payload)
    assert result["status"] is True
    assert result["data"]["document_number"] == "0000001234"
    assert _item_cmd(printer, "900", "2000") in printer._printer.sent


def test_short_close_response_reports_printed_without_number(printer: PnpPrinter, caplog):
    """Cierre corto: nunca se inventa un número; se informa 'impreso sin número' y se registran los contadores."""
    printer._printer = FakeController(responses={PNPcmd.CLOSE_TOTAL: ["0080", "0600", "0003", "0000001234"]})
    printer._type_doc = "credit"
    printer._counters_before = {"facturas": "00000010"}
    printer._process_payments({"payments": [{"payment_method": "01", "payment_amount": 10.0}]})
    assert printer._last_document == ""

    with caplog.at_level("WARNING"):
        result = printer._process_send_data()
    assert result["status"] is False
    assert result["printed"] is True
    assert result["data"]["Estado"] == "Documento impreso"
    assert "document_number" not in result["data"]
    assert "Contadores 8|N antes" in caplog.text


def test_complete_close_response_still_succeeds(printer: PnpPrinter):
    """Con el cierre completo el flujo normal no cambia: status True y el número del Campo 4."""
    printer._printer = FakeController(responses={PNPcmd.CLOSE_TOTAL: CLOSE_0x45})
    printer._type_doc = "invoice"
    printer._process_payments({"payments": [{"payment_method": "01", "payment_amount": 10.0}]})
    result = printer._process_send_data()
    assert result["status"] is True
    assert result["data"]["document_number"] == "0000001234"
