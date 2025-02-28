#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Utilidades para el manejo de rutas, textos, numeros y fechas"""

import re
from datetime import datetime
import sys
import os
import textwrap
from typing import List

import unicodedata


def get_base_path():
    """ Retornar os path"""
    if getattr(sys, "frozen", False):
        # Si está congelado, usar el directorio del ejecutable
        return os.path.dirname(sys.executable)

    # Si no está congelado, subir dos niveles desde utils/tools.py para llegar a la raíz
    return os.path.dirname(os.path.dirname(__file__))


def normalize_text(text: str) -> str:
    """
    Normaliza el texto reemplazando acentos y eliminando caracteres no permitidos.
    Args:
        text (str): Texto a normalizar.
    Returns:
        str: Texto normalizado.
    """
    text = unicodedata.normalize("NFD", text)
    text = "".join([c for c in text if not unicodedata.combining(c)])

    allowed_chars = r"[^a-zA-Z0-9\s\*\+\"\(\)\[\]\#@\'`|~{}:;?,\-_\^$!=%]"
    text = re.sub(allowed_chars, "", text)

    text = text.encode("ascii", "ignore").decode("utf-8")
    return " ".join(text.split())


def normalize_date(date):
    """
    Convierte una fecha en formato YYYY-MM-DD a DD/MM/YY.
    Args:
        date (str): Fecha en formato YYYY-MM-DD.
    Returns:
        str: Fecha en formato DD/MM/YY.
    """
    if not isinstance(date, str):
        raise ValueError("La fecha debe ser una cadena de texto.")

    date_obj = datetime.strptime(date, "%Y-%m-%d")
    date_format = date_obj.strftime("%d/%m/%y")
    return date_format


def normalize_number(number: str, length: int = 8) -> str:
    """
    Limpia un número eliminando caracteres no numéricos y lo rellena con ceros a la izquierda.
    Args:
        number (str): Número a limpiar (puede contener guiones, barras, etc.).
        length (int): Longitud deseada del número. Por defecto es 8.
                     Valores comunes para documentos fiscales:
                     - 4 para reportes Z
                     - 8 para facturas fiscales
                     - 10 para notas de crédito y total de documentos
    Returns:
        str: Número limpio y rellenado con ceros.
    Examples:
        >>> normalize_number("123", 4)  # Para reportes Z
        '0123'
        >>> normalize_number("123", 8)  # Para facturas fiscales
        '00000123'
        >>> normalize_number("123", 10)  # Para notas de crédito
        '0000000123'
        >>> normalize_number("A-123-B", 4)  # Limpia caracteres no numéricos
        '0123'
    """
    # Elimina todos los caracteres no numéricos
    cleaned = "".join(c for c in str(number) if c.isdigit())
    # Rellena con ceros a la izquierda hasta alcanzar la longitud deseada
    return cleaned.zfill(length)


def format_date(date_str: str) -> str:
    """
    Convierte una fecha de impresora en formato AAMMDD a YYYY-MM-DD.
    Args:
        date_str (str): Fecha en formato AAMMDD.
    Returns:
        str: Fecha en formato YYYY-MM-DD o 'Fecha inválida' si hay error.
    """
    try:
        year = 2000 + int(date_str[:2])
        month = int(date_str[2:4])
        day = int(date_str[4:])
        return f"{year:04d}-{month:02d}-{day:02d}"
    except (ValueError, IndexError):
        return "Fecha inválida"


def format_time(time_str: str) -> str:
    """
    Convierte una hora de impresora en formato HHMMSS a HH:MM:SS.
    Args:
        time_str (str): Hora en formato HHMMSS.
    Returns:
        str: Hora en formato HH:MM:SS o 'Hora inválida' si hay error.
    """
    try:
        hour = time_str[:2]
        minute = time_str[2:4]
        second = time_str[4:]
        return f"{hour}:{minute}:{second}"
    except (ValueError, IndexError):
        return "Hora inválida"


def format_multiline(text: str, width: int, prefix: str = "") -> List[str]:
    """
    Formatea texto largo en múltiples líneas
    Args:
        text: Texto a formatear
        width: Ancho máximo por línea
        prefix: Prefijo para cada línea
    Returns:
        List[str]: Lista de líneas formateadas
    """
    lines = textwrap.wrap(text, width)
    formatted_lines = [f"{prefix}{line}" for line in lines]
    return formatted_lines
