from typing import List
import textwrap


def _format_multiline(text: str, width: int, prefix: str = "") -> List[str]:
    """
    Formatea texto largo en múltiples líneas.
    Args:
        text: Texto a formatear.
        width: Ancho máximo por línea.
        prefix: Prefijo para cada línea.
    Returns:
        List[str]: Lista de líneas formateadas.
    """
    # wrapped_text = textwrap.fill(text, width)
    # lines = wrapped_text.split('\n')
    # formatted_lines = [f"{prefix}{line}" for line in lines]

    lines = textwrap.wrap(text, width)
    formatted_lines = [f"{prefix}{line}" for line in lines]

    return formatted_lines


# Ejemplo de uso
if __name__ == "__main__":
    texto = "ESTA ES LA DIRECCION DEL CLIENTE EN UNA CIUDAD QUE NO CONOZCO"
    ancho = 47  # Ancho máximo por línea
    prefijo = ""  # Prefijo para cada línea, puedes cambiarlo si deseas

    lineas_formateadas = _format_multiline(texto, ancho, prefijo)
    for linea in lineas_formateadas:
        print(linea)

    print("--------------------------------------------------")
    """La función wrap() toma un texto y lo divide en una lista de líneas, cada una con una 
    longitud máxima especificada. No divide las palabras, asegurándose de que cada línea 
    contenga palabras completas."""

    text = "Este es un texto de ejemplo que vamos a dividir en múltiples líneas."
    wrapped_text = textwrap.wrap(text, width=46)
    print(wrapped_text)
    # Salida: ['Este es un texto de', 'ejemplo que vamos a', 'dividir en múltiples', 'líneas.']

    print("--------------------------------------------------")
    """La función fill() funciona de manera similar a wrap(), pero en lugar de devolver una 
    lista de líneas, devuelve una sola cadena con líneas separadas por saltos de línea (\n)."""

    text = "Este es un texto de ejemplo que vamos a dividir en múltiples líneas."
    filled_text = textwrap.fill(text, width=46)
    print(filled_text)
    # Salida:
    # Este es un texto de
    # ejemplo que vamos a
    # dividir en múltiples
    # líneas.

    print("--------------------------------------------------")
    """Puedes personalizar aún más el comportamiento de wrap() y fill() usando argumentos 
    adicionales como expand_tabs, replace_whitespace, drop_whitespace, initial_indent, 
    subsequent_indent, entre otros."""

    wrapped_text = textwrap.fill(text, width=46, initial_indent="*", subsequent_indent="  ")
    print(wrapped_text)
    # Salida:
    # *Este es un texto de
    #   ejemplo que vamos a
    #   dividir en múltiples
    #   líneas.
