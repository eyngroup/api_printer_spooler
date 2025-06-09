#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script simple para probar la conexión con la impresora PNP
"""

import os
import sys
import binascii

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from controllers.pfpnp import FiscalPrinter

pf = FiscalPrinter()
PORT = "COM96"

pf.open_port()
resultado = pf.send_cmd("8|N")

# resultado = pf.send_command("8|V")
# resultado = pf.send_command("8|W")


# resultado = pf.send_command("9|X|T")
# resultado = pf.send_command("9|Z|T")
# resultado = pf.send_command("\x80|")


# resultado = pf.get_s5()
# resultado = pf.get_status()
# print(f"Respuesta: {resultado}")
pf.close_port()
