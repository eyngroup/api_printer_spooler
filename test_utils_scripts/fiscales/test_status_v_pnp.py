#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para probar los métodos status_if y get_status de la impresora PNP
"""

import os
import sys
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from controllers.pfpnp import FiscalPrinter


class TestStatusV:
    Printer = FiscalPrinter()
    PORT = "COM96" 

    try:
        print("=== PRUEBA DE LOS MÉTODOS status_if Y get_status CON IMPLEMENTACIÓN MEJORADA ===")
        PortOpen = Printer.open_port()
        if PortOpen:
            print("Puerto: " + Printer.port + " ABIERTO")

            print("\n=== Probando el método status_if con parámetro 'V' ===")
            resultado_status_if = Printer.status_if("V")

            if resultado_status_if and isinstance(resultado_status_if, dict):
                print("\nRespuesta formateada del método status_if:")
                print(json.dumps(resultado_status_if, indent=2, ensure_ascii=False))

                print("\nCampos individuales:")
                for key, value in resultado_status_if.items():
                    if key != "respuesta_completa":  # No mostrar la respuesta completa para no saturar la salida
                        print(f"{key}: {value}")
            else:
                print(f"Respuesta en bruto: {resultado_status_if}")
                if isinstance(resultado_status_if, bytes):
                    print(f"Respuesta decodificada: {resultado_status_if.decode('latin-1')}")

            print("\n=== Probando el método get_status ===")
            resultado_get_status = Printer.get_status()

            if resultado_get_status:
                print("\nRespuesta formateada del método get_status:")
                resultado_para_json = {}
                for k, v in resultado_get_status.items():
                    if k != "campos_originales":
                        resultado_para_json[k] = v

                print(json.dumps(resultado_para_json, indent=2, ensure_ascii=False))

                print("\nCampos principales:")
                print(f"Status impresora: {resultado_get_status.get('status_impresora', '')}")
                print(f"Status fiscal: {resultado_get_status.get('status_fiscal', '')}")

                print(f"\nCódigo impresora: {resultado_get_status.get('codigo_impresora', '')}")
                if "estado_impresora_detallado" in resultado_get_status:
                    print(f"Estado detallado: {resultado_get_status.get('estado_impresora_detallado', '')}")

                if "error_critico" in resultado_get_status:
                    print(f"Error crítico: {'SÍ' if resultado_get_status.get('error_critico') else 'NO'}")
                    if resultado_get_status.get("error_critico"):
                        print(
                            f"Requiere servicio técnico: {'SÍ' if resultado_get_status.get('requiere_servicio_tecnico') else 'NO'}"
                        )
            else:
                print("No se pudo obtener el estado de la impresora")

            Printer.close_port()
            print("\nPuerto cerrado")
        else:
            print(f"No se pudo abrir el puerto {Printer.port}")
    except Exception as e:
        import traceback

        print("OCURRIO UNA EXCEPCION: \nDetalles del Error: \n", e)
        print(traceback.format_exc())


if __name__ == "__main__":
    TestStatusV()
