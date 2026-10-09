"""
Pruebas de la impresora matricial (diario de notas no fiscal) en modo archivo.

El template y el contador se copian a un directorio temporal: el template real nunca se modifica.
"""

import copy
import json
import re
import shutil
import threading
from pathlib import Path

import pytest

import printers.printer_dotmatrix as dotmatrix
from handy.tools import get_base_path
from printers.printer_dotmatrix import MatrixPrinter

ODOO_KEY = "0000000042"  # document_number de Odoo: clave de idempotencia, no debe imprimirse


def make_document(items: list[dict] | None = None) -> dict:
    """Arma un documento con el mismo formato que envía Odoo."""
    return {
        "operation_type": "invoice",
        "document": {
            "document_number": ODOO_KEY,
            "document_date": "2026-10-09",
            "document_name": "INV/2026/0001",
        },
        "customer": {
            "customer_vat": "V-12345678",
            "customer_name": "CLIENTE DE PRUEBA",
            "customer_address": "Caracas",
            "customer_phone": "0414",
        },
        "items": items
        if items is not None
        else [
            {"item_ref": "A1", "item_name": "Producto", "item_quantity": 2, "item_price": 10.0, "item_tax": 16},
        ],
    }


def item_with(discount: float, discount_type: str) -> dict:
    """Item de 2 x 10.00 con IVA 16 % y el ajuste indicado."""
    return {
        "item_ref": "A1",
        "item_name": "Producto",
        "item_quantity": 2,
        "item_price": 10.0,
        "item_tax": 16,
        "item_discount": discount,
        "item_discount_type": discount_type,
    }


@pytest.fixture
def env(tmp_path, monkeypatch):
    """Copia el template a tmp_path y devuelve (config, ruta del template, ruta de salida)."""
    source = Path(get_base_path()) / "templates" / "template_matriz_carta.json"
    template = tmp_path / "template.json"
    shutil.copy(source, template)
    output = tmp_path / "out.txt"
    monkeypatch.setattr(dotmatrix, "PLATFORM_HAS_WIN32", False)  # Modo archivo: debe funcionar sin win32print
    config = {
        "matrix_enabled": True,
        "matrix_direct": False,
        "matrix_file": str(output),
        "matrix_template": str(template),
    }
    return config, template, output


def counter_on_disk(template: Path) -> str:
    """Lee el contador de facturas persistido en el template temporal."""
    return json.loads(template.read_text(encoding="utf-8"))["counter"]["document_invoice"]


def printed(output: Path) -> str:
    """Texto impreso (latin-1) sin los comandos ESC/P, para comparar solo el contenido legible."""
    text = output.read_bytes().decode("latin-1")
    return re.sub(r"\x1b(?:[aCt][\x00-\x02]|.)|[\x0c\x0f]", "", text)


def test_header_prints_counter_and_reference_not_odoo_key(env):
    """El encabezado imprime el número del contador y REF, nunca el document_number de Odoo."""
    config, _, output = env
    result = MatrixPrinter(copy.deepcopy(config)).print_document(make_document())

    text = printed(output)
    assert result["status"] is True
    assert "FECHA: 2026-10-09 | NOTA DE ENTREGA: 00000001" in text  # tipo fijo del template (diario de notas)
    assert "REF: INV/2026/0001" in text
    assert ODOO_KEY not in text


def test_header_without_reference_has_no_ref_line(env):
    """Sin document_name no se imprime la línea REF."""
    config, _, output = env
    data = make_document()
    data["document"]["document_name"] = ""
    MatrixPrinter(config).print_document(data)

    assert "REF:" not in printed(output)


def test_response_number_matches_printed_and_counter_persisted(env):
    """El número devuelto a Odoo es el impreso y el contador avanza +1 en disco."""
    config, template, output = env
    result = MatrixPrinter(config).print_document(make_document())

    number = result["data"]["document_number"]
    assert number == "00000001"
    assert f"NOTA DE ENTREGA: {number}" in printed(output)
    assert counter_on_disk(template) == number
    assert set(result["data"]) == {"document_date", "document_number", "machine_serial", "machine_report"}


def test_failed_print_does_not_consume_number(env, monkeypatch):
    """Si la escritura falla el contador no avanza y el siguiente documento reutiliza el número."""
    config, template, output = env
    real_open = open

    def failing_open(file, *args, **kwargs):
        if str(file) == str(output):
            raise OSError("disco lleno")
        return real_open(file, *args, **kwargs)

    with monkeypatch.context() as patch:
        patch.setattr("builtins.open", failing_open)
        failed = MatrixPrinter(config).print_document(make_document())

    assert failed["status"] is False
    assert failed["data"] is None
    assert counter_on_disk(template) == "00000000"

    retry = MatrixPrinter(config).print_document(make_document())
    assert retry["status"] is True
    assert retry["data"]["document_number"] == "00000001"
    assert counter_on_disk(template) == "00000001"


def test_discount_example(env):
    """10 % de descuento sobre 2 x 10.00 con IVA 16 %: total de línea 18.00 y totales coherentes."""
    config, _, output = env
    MatrixPrinter(config).print_document(make_document([item_with(10, "discount_percentage")]))
    lines = printed(output).splitlines()

    item_line = next(line for line in lines if line.startswith("A1"))
    assert item_line.rstrip().endswith("18.00")
    assert item_line.split() == ["A1", "Producto", "2.00", "10.00", "18.00"]  # PRECIO = unitario original
    adjustment = next(line for line in lines if "Descuento 10.00%" in line)
    assert adjustment.startswith(" " * 8 + "Descuento 10.00%")
    assert adjustment.rstrip().endswith("-2.00")
    assert len(adjustment) == 80
    assert any(line.strip() == "AJUSTES:          -2.00" for line in lines)
    assert any(line.strip() == "SUBTOTAL:          18.00" for line in lines)
    assert any(line.strip() == "IVA:           2.88" for line in lines)
    assert any(line.strip() == "TOTAL:          20.88" for line in lines)
    assert lines.index(next(line for line in lines if "AJUSTES" in line)) < lines.index(
        next(line for line in lines if "SUBTOTAL" in line)
    )


def test_surcharge_percentage_is_positive(env):
    """El recargo del 5 % muestra la leyenda y el monto positivo."""
    config, _, output = env
    MatrixPrinter(config).print_document(make_document([item_with(5, "surcharge_percentage")]))
    lines = printed(output).splitlines()

    adjustment = next(line for line in lines if "Recargo 5.00%" in line)
    assert adjustment.rstrip().endswith("1.00")
    assert "-" not in adjustment.split("Recargo")[1]
    assert any(line.strip() == "SUBTOTAL:          21.00" for line in lines)
    assert any(line.strip() == "AJUSTES:           1.00" for line in lines)  # Recargo: ajuste positivo


def test_amount_adjustments_have_no_percent_sign(env):
    """Los ajustes por monto no llevan el signo de porcentaje."""
    config, _, output = env
    MatrixPrinter(config).print_document(make_document([item_with(1.5, "discount_amount")]))
    text = printed(output)

    assert "Descuento 1.50" in text
    assert "Descuento 1.50%" not in text
    assert "-3.00" in text


def test_no_adjustment_has_no_discount_lines(env):
    """Sin ajustes no hay AJUSTES ni leyendas y los totales salen del modelo."""
    config, _, output = env
    MatrixPrinter(config).print_document(make_document())
    text = printed(output)

    assert "AJUSTES" not in text
    assert "Descuento" not in text and "Recargo" not in text
    assert "SUBTOTAL:          20.00" in text
    assert "IVA:           3.20" in text
    assert "TOTAL:          23.20" in text


def test_concurrent_prints_get_consecutive_numbers(env):
    """Dos hilos imprimiendo a la vez reciben números distintos y consecutivos."""
    config, template, _ = env
    results: list[dict] = []

    def worker() -> None:
        """Imprime un documento con su propia instancia (como en cada petición)."""
        results.append(MatrixPrinter(dict(config)).print_document(make_document()))

    threads = [threading.Thread(target=worker) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    numbers = sorted(r["data"]["document_number"] for r in results)
    assert all(r["status"] for r in results)
    assert numbers == ["00000001", "00000002"]
    assert counter_on_disk(template) == "00000002"


def test_direct_print_requires_win32(env, monkeypatch):
    """La impresión directa sin win32print (Linux) falla de forma explícita al construir la impresora."""
    config, _, _ = env
    monkeypatch.setattr(dotmatrix, "PLATFORM_HAS_WIN32", False)
    with pytest.raises(NotImplementedError):
        MatrixPrinter({**config, "matrix_direct": True})


def test_file_mode_works_without_win32(env):
    """El modo archivo (txt) imprime sin win32print, en cualquier sistema operativo."""
    config, _, output = env
    result = MatrixPrinter(config).print_document(make_document())
    assert result["status"] is True
    assert output.exists()


def test_column_titles_aligned_with_values(env):
    """Los títulos de columnas numéricas terminan en la misma posición que sus valores."""
    config, _, output = env
    MatrixPrinter(config).print_document(make_document())
    lines = printed(output).splitlines()
    title = next(line for line in lines if "DESCRIPCION" in line)
    row = next(line for line in lines if line.startswith("A1"))
    for label, value in (("CANT", "2.00"), ("PRECIO", "10.00"), ("TOTAL", "20.00")):
        assert title.index(label) + len(label) == row.index(value) + len(value)
