"""Tests de la normalización de texto que usan los drivers fiscales (HKA y PNP)."""

import pytest

from handy.tools import normalize_text


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Pérez & Hijos, C.A.", "Perez & Hijos, C.A."),  # el & y los puntos se imprimen
        ("A&B", "A&B"),
        ("Inversiones  &  Servicios", "Inversiones & Servicios"),
    ],
)
def test_normalize_text_keeps_ampersand(text: str, expected: str):
    """El "&" es ASCII imprimible y los manuales HKA/PNP no lo restringen: debe llegar a la impresora."""
    assert normalize_text(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Ñandú Café", "Nandu Cafe"),  # acentos y eñe se reducen a ASCII
        ("Av. Bolívar c/ calle 5", "Av. Bolivar c calle 5"),  # el punto se conserva; la barra se quita
        ("Precio <10> \\ ok", "Precio 10 ok"),
        ("Tornillo 1|2", "Tornillo 12"),  # "|" es el separador de campos 0x1C del PNP: se quita
        ("ventas@empresa.com.ve", "ventas@empresa.com.ve"),  # los correos conservan sus puntos
        ("  varios   espacios  ", "varios espacios"),
    ],
)
def test_normalize_text_other_rules_unchanged(text: str, expected: str):
    """El resto de la normalización se mantiene igual."""
    assert normalize_text(text) == expected
