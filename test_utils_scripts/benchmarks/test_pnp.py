import time
from pfpnp import FiscalPrinter

printer = FiscalPrinter()
printer.open_port()

start = time.time()
resp = printer.status_if("W")
print(f"Aqui: {resp}")
print(f"Tiempo ejecución: {time.time() - start:.3f}s")  

printer.close_port()