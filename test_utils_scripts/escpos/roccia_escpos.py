from escpos.printer import Usb

p = Usb(0x0416, 0x5011) 

# Encabezado
p.set(align="center", font="a", text_type="bold", width=2, height=2)
p.text("SENIAT\n")
p.set(align="center", font="a", text_type="normal", width=1, height=1)
p.text("J-312171197\n")
p.text("THE FACTORY HKA\n")
p.text("CALIFORNIA NORTE, CARACAS\n")
p.text("RIF/CI: J-312171197\n")
p.text("R.S.: THE FACTORY HKA, C.A.\n")
p.text("DIRECCION: LA CALIFORNIA\n")
p.text("CARACAS\n")

# Línea de separación
p.text("-" * 48 + "\n")

# Factura y Fecha/Hora
p.set(align="left", font="a", text_type="normal", width=1, height=1)
p.text("FACTURA: ")
p.set(align="right", font="a", text_type="normal", width=1, height=1)
p.text("00000590\n")
p.set(align="left", font="a", text_type="normal", width=1, height=1)
p.text("FECHA: 16-11-2023")
p.set(align="right", font="a", text_type="normal", width=1, height=1)
p.text("HORA: 16:39\n")

# Línea de separación
p.text("-" * 48 + "\n")

# Cerrar la conexión con la impresora
p.cut()
p.close()
