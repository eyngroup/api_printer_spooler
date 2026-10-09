"""
Pruebas de la impresora de tickets en modo archivo (sin impresora real).

El template y el contador se copian a un directorio temporal: el template real nunca se modifica.
"""

import copy
import json
import re
import shutil
import subprocess
import threading
from pathlib import Path

import pytest

import printers.printer_ticket as ticket
from handy.tools import get_base_path
from printers.printer_counter import FiscalCounter
from printers.printer_ticket import TicketPrinter


def make_document(items: list[dict]) -> dict:
    """Arma un documento con el mismo formato que envía Odoo."""
    return {
        "operation_type": "invoice",
        "document": {"document_number": "0000000042", "document_date": "2026-10-09", "document_name": "INV/2026/0001"},
        "customer": {"customer_vat": "V-12345678", "customer_name": "CLIENTE DE PRUEBA"},
        "items": items,
    }


def make_item(price: float, discount: float = 0, discount_type: str = "", tax: int = 16, quantity: int = 2) -> dict:
    """Item con el ajuste indicado (sin ajuste si discount es 0)."""
    item = {"item_ref": "A1", "item_name": "Producto", "item_quantity": quantity, "item_price": price, "item_tax": tax}
    if discount:
        item.update({"item_discount": discount, "item_discount_type": discount_type})
    return item


@pytest.fixture
def env(tmp_path):
    """Copia el template a tmp_path y devuelve (config, ruta del template, ruta de salida). Sin ticket_port."""
    source = Path(get_base_path()) / "templates" / "template_ticket_simple.json"
    template = tmp_path / "template.json"
    shutil.copy(source, template)
    output = tmp_path / "out.txt"
    config = {
        "ticket_enabled": True,
        "ticket_direct": False,
        "ticket_file": str(output),
        "ticket_template": str(template),
    }
    return config, template, output


def counter_on_disk(template: Path) -> str:
    """Lee el contador de facturas persistido en el template temporal."""
    return json.loads(template.read_text(encoding="utf-8"))["counter"]["document_invoice"]


def printed(output: Path) -> str:
    """Texto impreso (CP850) sin los comandos ESC/GS, para comparar solo el contenido legible."""
    text = output.read_bytes().decode("cp850")
    return re.sub(r"\x1b[!-~]?[\x00-\x03]?|\x1d[V-~][\x00-\x41]?", "", text)


def line_with(text: str, needle: str) -> str:
    """Devuelve la primera línea que contiene needle, con espacios internos colapsados."""
    line = next(row for row in text.splitlines() if needle in row)
    return re.sub(r"\s{2,}", "  ", line.strip())


def test_discount_surcharge_and_totals(env):
    """Descuento 10 % y recargo 5 % con leyendas, AJUSTES y totales iguales a los del modelo de Odoo."""
    config, _, output = env
    data = make_document(
        [
            make_item(10.0, 10, "discount_percentage"),
            make_item(20.0, 5, "surcharge_percentage", quantity=1),
            make_item(5.0, tax=0, quantity=1),
        ]
    )
    result = TicketPrinter(config).print_document(data)

    text = printed(output)
    assert result["status"] is True
    assert line_with(text, "Producto (G)") == "A1 Producto (G)  Bs 18.00"
    assert line_with(text, "Descuento 10.00%") == "Descuento 10.00%  Bs -2.00"
    assert line_with(text, "Recargo 5.00%") == "Recargo 5.00%  Bs 1.00"
    assert "Bs 21.00" in text
    totals = text[text.index("AJUSTES:") :]
    assert totals.splitlines()[0].split() == ["AJUSTES:", "Bs", "-1.00"]
    assert line_with(totals, "EXENTO") == "EXENTO  Bs 5.00"
    assert line_with(totals, "BI G") == "BI G (16,00%)  Bs 39.00"
    assert line_with(totals, "IVA G") == "IVA G (16,00%)  Bs 6.24"
    assert line_with(totals, "TOTAL:") == "TOTAL:  Bs 50.24"


def test_amount_adjustments_use_plain_amount(env):
    """Los ajustes por monto no llevan el signo porcentual."""
    config, _, output = env
    TicketPrinter(config).print_document(make_document([make_item(10.0, 1.5, "discount_amount", quantity=1)]))

    assert line_with(printed(output), "Descuento 1.50") == "Descuento 1.50  Bs -1.50"


def test_document_without_adjustment_has_no_adjustment_lines(env):
    """Sin descuentos ni recargos no aparece AJUSTES ni leyendas."""
    config, _, output = env
    TicketPrinter(config).print_document(make_document([make_item(10.0)]))

    text = printed(output)
    assert "AJUSTES" not in text
    assert "Descuento" not in text
    assert "Recargo" not in text
    assert line_with(text, "TOTAL:") == "TOTAL:  Bs 23.20"


def test_printed_number_equals_response_and_counter_persisted(env):
    """El número impreso es el reservado, se devuelve a Odoo y el contador avanza +1 en disco."""
    config, template, output = env
    result = TicketPrinter(config).print_document(make_document([make_item(10.0)]))

    assert result["status"] is True
    assert result["data"]["document_number"] == "00000001"
    assert "NUMERO" in line_with(printed(output), "NUMERO")
    assert line_with(printed(output), "NUMERO").endswith("00000001")
    assert counter_on_disk(template) == "00000001"


def test_failed_write_keeps_counter_and_next_print_reuses_number(env, monkeypatch):
    """Si falla la escritura no se confirma el contador y el siguiente documento reutiliza el número."""
    config, template, output = env
    document = make_document([make_item(10.0)])
    real_open = open

    def failing_open(file, *args, **kwargs):
        if str(file) == str(output):
            raise OSError("disco lleno")
        return real_open(file, *args, **kwargs)

    with monkeypatch.context() as patch:
        patch.setattr("builtins.open", failing_open)
        failed = TicketPrinter(copy.deepcopy(config)).print_document(document)

    assert failed["status"] is False
    assert failed["data"] is None
    assert counter_on_disk(template) == "00000000"

    retry = TicketPrinter(copy.deepcopy(config)).print_document(document)
    assert retry["status"] is True
    assert retry["data"]["document_number"] == "00000001"
    assert counter_on_disk(template) == "00000001"


def test_commit_failure_after_print_still_succeeds(env, monkeypatch, caplog):
    """Si el contador no se puede persistir tras imprimir, se registra CRITICAL pero se reporta éxito."""
    config, _, _ = env

    def broken_commit(self, document_type, reserved):
        raise OSError("sin permisos")

    monkeypatch.setattr(FiscalCounter, "commit_counter", broken_commit)
    result = TicketPrinter(config).print_document(make_document([make_item(10.0)]))

    assert result["status"] is True
    assert "Documento impreso pero no se pudo persistir el contador" in caplog.text


def test_file_mode_does_not_touch_the_operating_system_printer(env, monkeypatch):
    """En modo archivo no se consulta lpstat ni OpenPrinter aunque no haya ticket_port."""
    config, _, _ = env

    def forbidden(*args, **kwargs):
        raise AssertionError("no debe consultar la impresora del sistema en modo archivo")

    monkeypatch.setattr(subprocess, "check_output", forbidden)
    monkeypatch.setattr(subprocess, "Popen", forbidden)
    if hasattr(ticket, "win32print"):
        monkeypatch.setattr(ticket.win32print, "OpenPrinter", forbidden)

    result = TicketPrinter(config).print_document(make_document([make_item(10.0)]))

    assert result["status"] is True


def test_concurrent_prints_get_consecutive_numbers(env):
    """Dos hilos imprimiendo a la vez reciben números distintos y consecutivos."""
    config, template, _ = env
    numbers: list[str] = []

    def worker():
        result = TicketPrinter(copy.deepcopy(config)).print_document(make_document([make_item(10.0)]))
        numbers.append(result["data"]["document_number"])

    threads = [threading.Thread(target=worker) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert sorted(numbers) == ["00000001", "00000002"]
    assert counter_on_disk(template) == "00000002"


def test_spanish_characters_printed_in_cp850(env):
    """ñ, acentos (también en mayúscula), ¡ y ¿ se envían en CP850 tras ESC t 2 (verificado en tiquera POS80)."""
    config, _, output = env
    document = make_document([{**make_item(10.0), "item_name": "Café Añejo ÍÓÚ"}])
    document["customer"].update({"customer_name": "JOSÉ MUÑOZ ÁLVAREZ", "customer_address": "Av. Bolívar, Caño"})
    document["document"]["document_cashier"] = "María Pérez"
    TicketPrinter(config).print_document(document)
    raw = output.read_bytes()

    assert b"\x1bt\x02" in raw  # ESC t 2 = PC850
    assert b"\x1bt\x12" not in raw  # ESC t 18 (PC852) ya no se usa
    for text in ("JOSÉ MUÑOZ ÁLVAREZ", "Café Añejo ÍÓÚ", "Av. Bolívar, Caño", "María Pérez"):
        assert text.encode("cp850") in raw, text  # sin quitar acentos ni puntos
    assert "JOSÉ".encode("utf-8") not in raw  # ya no se envía UTF-8
