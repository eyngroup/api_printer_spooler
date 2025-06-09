# Archivo: benchmarks/pnp_functional_test.py
import sys
import time
from pathlib import Path
import logging

logging.basicConfig(level=logging.DEBUG)

sys.path.append(str(Path(__file__).parent.parent))
from controllers.pfpnp import FiscalPrinter

def test_commands():
    start_total = time.perf_counter()
    printer = FiscalPrinter(port="COM96", timeout=2)
    
    if not printer.open_port():
        print("Error abriendo puerto")
        return

    test_sequence = [("H", "Test hardware")] + \
                    [(f"I|Prueba {i}", f"Línea {i}") for i in range(1, 9)] + \
                    [("J", "Corte de papel")]
    
    total_commands_time = 0.0 
    
    for cmd, desc in test_sequence:
        print(f"\n=== Enviando: {desc} ===")
        cmd_start = time.perf_counter()
        response = printer.send_cmd(cmd)
        elapsed = time.perf_counter() - cmd_start
        total_commands_time += elapsed
    
    printer.close_port()
    
    total_execution_time = time.perf_counter() - start_total
    print(f"\n=== RESUMEN EJECUCIÓN ===")
    print(f"Comandos ejecutados: {len(test_sequence)}")
    print(f"Tiempo total comandos: {total_commands_time*1000:.2f}ms")
    print(f"Tiempo total ejecución: {total_execution_time*1000:.2f}ms")
    print(f"Overhead: {(total_execution_time - total_commands_time)*1000:.2f}ms")

if __name__ == "__main__":
    test_commands()