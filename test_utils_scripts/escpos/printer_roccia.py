import win32print
import win32ui

printer_name = "POS-80C"

hDC = win32ui.CreateDC()
hDC.CreatePrinterDC(printer_name)
hDC.StartDoc("Ticket")
hDC.StartPage()

font_monospace = win32ui.CreateFont(
    {
        "name": "Console",  # Ajustar la fuente según lo deseado
        "height": 30,  # Altura de la fuente
        "weight": 400,  # Peso de la fuente
    }
)
font_bold = win32ui.CreateFont(
    {
        "name": "Arial Black",  # Cambiamos a Arial Black para negritas más marcadas
        "height": 40,  # Altura de la fuente
        "weight": 700,  # Negritas
    }
)


# Función para centrar el texto
def center_text(hDC, text, y):
    text_size = hDC.GetTextExtent(text)
    x = (hDC.GetDeviceCaps(8) - text_size[0]) // 2
    hDC.TextOut(x, y, text)


# Función para alinear texto a la derecha
def right_align_text(hDC, text, y):
    text_size = hDC.GetTextExtent(text)
    x = hDC.GetDeviceCaps(8) - text_size[0] - 0  # Ajusta 50 según el margen que desees
    hDC.TextOut(x, y, text)


# Función para alinear texto a la izquierda
def left_align_text(hDC, text, y, x=0):  # Ajusta 50 según el margen que desees
    hDC.TextOut(x, y, text)


# Espaciado entre líneas
line_height = 25

# Posición inicial
current_y = 10

# Encabezado
hDC.SelectObject(font_bold)
center_text(hDC, "SENIAT", current_y)

# Ajuste especial para la siguiente línea
current_y += 40

# Resto del texto
hDC.SelectObject(font_monospace)

center_text(hDC, "J-312171197", current_y)
current_y += line_height
center_text(hDC, "THE FACTORY HKA", current_y)
current_y += line_height
center_text(hDC, "CALIFORNIA NORTE, CARACAS", current_y)
current_y += line_height
left_align_text(hDC, "RIF/CI: J-312171197", current_y)
current_y += line_height
left_align_text(hDC, "R.S.: THE FACTORY HKA, C.A.", current_y)
current_y += line_height
left_align_text(hDC, "DIRECCION: LA CALIFORNIA", current_y)


# Línea de separación
left_align_text(hDC, " " * 80, current_y)
current_y += line_height

# Factura y Fecha/Hora
left_align_text(hDC, "FACTURA:", current_y)
right_align_text(hDC, "00000590", current_y)
current_y += line_height
left_align_text(hDC, "FECHA: 16-11-2023", current_y)
right_align_text(hDC, "HORA: 16:39", current_y)
current_y += line_height

# Línea de separación
left_align_text(hDC, "-" * 80, current_y)
current_y += line_height

# Finalizar página y documento
hDC.EndPage()
hDC.EndDoc()
hDC.DeleteDC()
