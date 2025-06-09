#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import logging
import clr
from System.Reflection import Assembly

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def test_printer():
    try:
        # Obtener path del DLL
        if getattr(sys, "frozen", False):
            # ejecutable compilado
            base_path = os.path.dirname(sys.executable)
            dll_path = os.path.join(base_path, "library", "TfhkaNet.dll")
        else:
            # en desarrollo
            base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            dll_path = os.path.join(base_path, "library", "TfhkaNet.dll")

        logger.info(f"Usando DLL en: {dll_path}")
        if not os.path.exists(dll_path):
            logger.error(f"DLL no encontrado en: {dll_path}")
            return

        logger.info("Cargando DLL...")
        Assembly.LoadFrom(dll_path)
        clr.AddReference("TfhkaNet")
        from TfhkaNet.IF.VE import Tfhka

        printer = Tfhka()

        if printer.OpenFpCtrl("COM3"):
            logger.info("Puerto abierto exitosamente")

            if printer.CheckFPrinter():
                logger.info("Impresora validada correctamente")
            else:
                logger.error("Error al validar impresora")

            if printer.CloseFpCtrl():
                logger.info("Puerto cerrado exitosamente")
            else:
                logger.error("Error al cerrar puerto")
        else:
            logger.error("Error al abrir puerto")

    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)


if __name__ == "__main__":
    test_printer()
