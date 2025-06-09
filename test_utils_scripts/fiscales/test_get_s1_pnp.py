#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para probar el método get_s1 de la impresora PNP
"""

import os
import sys
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from controllers.pfpnp import FiscalPrinter


class TestGetS1:
    Printer = FiscalPrinter()
    PORT = "COM96"

    try:
        print("=== PRUEBA DEL MÉTODO get_s1 CON IMPLEMENTACIÓN MEJORADA ===")
        PortOpen = Printer.open_port()
        if PortOpen:
            print("Puerto: " + Printer.port + " ABIERTO")

            print("\n=== Obteniendo información fiscal con get_s1 ===")
            resultado = Printer.get_counters()

            if resultado:
                print("\nRespuesta formateada:")
                print(json.dumps(resultado, indent=2, ensure_ascii=False))

                print("\nCampos individuales:")
                print(f"Estado impresora: {resultado.get('status_impresora', '')}")
                print(f"Estado fiscal: {resultado.get('status_fiscal', '')}")
                print(f"Última secuencia: {resultado.get('ultima_secuencia', '')}")

                print(f"\nCódigo impresora: {resultado.get('codigo_impresora', '')}")
                if "estado_impresora_detallado" in resultado:
                    print(f"Estado detallado: {resultado.get('estado_impresora_detallado', '')}")

                if "error_critico" in resultado:
                    print(f"Error crítico: {'SÍ' if resultado.get('error_critico') else 'NO'}")
                    if resultado.get("error_critico"):
                        print(
                            f"Requiere servicio técnico: {'SÍ' if resultado.get('requiere_servicio_tecnico') else 'NO'}"
                        )

                print(f"\nÚltimo comando: {resultado.get('ultimo_comando', '')}")
                print(f"\nFecha: {resultado.get('fecha', '')}")
                if "fecha_formateada" in resultado:
                    print(f"Fecha formateada: {resultado.get('fecha_formateada', '')}")

                print(f"Hora: {resultado.get('hora', '')}")
                if "hora_formateada" in resultado:
                    print(f"Hora formateada: {resultado.get('hora_formateada', '')}")

                print(f"\nFacturas día: {resultado.get('facturas_dia', '')}")
                print(f"DNF día: {resultado.get('dnf_dia', '')}")
                print(f"Facturas acumuladas: {resultado.get('facturas_acumuladas', '')}")
                print(f"DNF acumuladas: {resultado.get('dnf_acumuladas', '')}")
                print(f"Último Z: {resultado.get('ultimo_z', '')}")
            else:
                print("No se pudo obtener información fiscal")

            Printer.close_port()
            print("\nPuerto cerrado")
        else:
            print(f"No se pudo abrir el puerto {Printer.port}")
    except Exception as e:
        import traceback

        print("OCURRIO UNA EXCEPCION: \nDetalles del Error: \n", e)
        print(traceback.format_exc())


if __name__ == "__main__":
    TestGetS1()
