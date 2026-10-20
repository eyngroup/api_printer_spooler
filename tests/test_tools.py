"""Tests de la normalización de texto que usan los drivers fiscales (HKA y PNP)."""

import pytest

from handy.tools import normalize_text


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Pérez & Hijos, C.A.", "Perez & Hijos, CA"),  # el & se imprime; el punto se sigue quitando (acorta el nombre)
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
        ("Av. Bolívar c/ calle 5", "Av Bolivar c calle 5"),  # punto y barra se siguen quitando
        ("Precio <10> \\ ok", "Precio 10 ok"),
        ("  varios   espacios  ", "varios espacios"),
    ],
)
def test_normalize_text_other_rules_unchanged(text: str, expected: str):
    """El resto de la normalización se mantiene igual."""
    assert normalize_text(text) == expected
