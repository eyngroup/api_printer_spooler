from escpos.printer import Usb

p = Usb(0x0416, 0x5011)  # Ajusta estos valores según el VID y PID

p.set(align="center", font="a", text_type="bold", width=2, height=2)
p.text("TITULO\n")
p.set(align="center", font="a", text_type="normal", width=1, height=1)
p.text("J-123456789\n")
p.text("NOMBRE EMPRESA\n")
p.text("DIRECCION EMPRESA\n")
p.text("RIF/CI: J-87654321\n")
p.text("R.S.: THE COMPANY, C.A.\n")
p.text("DIRECCION: SU DIRECCION\n")
p.text("LA CIUDAD\n")

p.text("-" * 48 + "\n")

p.set(align="left", font="a", text_type="normal", width=1, height=1)
p.text("DESPACHO: ")
p.set(align="right", font="a", text_type="normal", width=1, height=1)
p.text("00000590\n")
p.set(align="left", font="a", text_type="normal", width=1, height=1)
p.text("FECHA: 16-11-2023")
p.set(align="right", font="a", text_type="normal", width=1, height=1)
p.text("HORA: 16:39\n")

p.text("-" * 48 + "\n")

p.cut()
p.close()
