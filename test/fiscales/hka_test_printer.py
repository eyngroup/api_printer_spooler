#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import unittest
from unittest.mock import patch

from printers.printer_hka import FiscalPrinterHka


class TestFiscalPrinterHka(unittest.TestCase):
    def setUp(self):
        """Configuración inicial para cada prueba"""

        self.config = {"enabled": True, "model": "pnp", "connection": {"port": "COM96"}}

        example_path = os.path.join(os.path.dirname(__file__), "..", "resources", "example.json")
        with open(example_path, "r") as f:
            self.example_document = json.load(f)

        with patch("printers.fiscal_hka.TfhkaPy") as mock_tfhka:
            self.mock_printer = mock_tfhka.Tfhka.return_value
            self.printer = FiscalPrinterHka(self.config)
            self.printer.printer_hka = self.mock_printer

    def test_connect(self):
        """Prueba el método connect"""

        self.mock_printer.OpenFpctrl.return_value = True
        self.mock_printer._HandleCTSRTS.return_value = True

        result = self.printer.connect()
        self.assertTrue(result)
        self.assertTrue(self.printer.is_connected)
        self.mock_printer.OpenFpctrl.assert_called_once_with("COM1")

        self.mock_printer.OpenFpctrl.return_value = False
        result = self.printer.connect()
        self.assertFalse(result)
        self.assertFalse(self.printer.is_connected)

    def test_disconnect(self):
        """Prueba el método disconnect"""

        self.printer.disconnect()
        self.mock_printer.CloseFpctrl.assert_called_once()
        self.assertFalse(self.printer.is_connected)

    def test_check_status(self):
        """Prueba el método check_status"""

        self.mock_printer.ReadFpStatus.return_value = "0 0 Sin error"

        status = self.printer.check_status()
        self.assertIsNone(status["error"])
        self.assertEqual(status["code1"], "0")
        self.assertEqual(status["code2"], "0")

        self.mock_printer.ReadFpStatus.return_value = "1 2 Error de impresora"
        status = self.printer.check_status()
        self.assertEqual(status["error"], "Error de impresora")
        self.assertEqual(status["code1"], "1")
        self.assertEqual(status["code2"], "2")

    def test_enviar_comando(self):
        """Prueba el método enviar_comando"""

        self.mock_printer.SendCmd.return_value = True
        result = self.printer.enviar_comando("iR*V123456789")
        self.assertTrue(result["success"])
        self.mock_printer.SendCmd.assert_called_with("iR*V123456789")

        self.mock_printer.SendCmd.return_value = False
        self.mock_printer.ReadFpStatus.return_value = "1 0 Error en comando"
        result = self.printer.enviar_comando("comando_invalido")
        self.assertFalse(result["success"])
        self.assertIn("Error en comando", result["message"])

    def test_print_document(self):
        """Prueba el método print_document"""

        self.mock_printer.OpenFpctrl.return_value = True
        self.mock_printer._HandleCTSRTS.return_value = True
        self.mock_printer.SendCmd.return_value = True
        self.mock_printer.ReadFpStatus.return_value = "0 0 Sin error"

        result = self.printer.print_document(self.example_document)
        self.assertTrue(result["success"])
        self.assertEqual(result["message"], "Documento fiscal impreso correctamente")

        expected_commands = [
            "iR*V131348076",  # RIF
            "iS*NOMBRE DEL CLIENTE",  # Nombre
        ]
        for cmd in expected_commands:
            self.mock_printer.SendCmd.assert_any_call(cmd)

    def test_print_report_x(self):
        """Prueba el método print_report_x"""

        self.mock_printer.OpenFpctrl.return_value = True
        self.mock_printer._HandleCTSRTS.return_value = True
        self.mock_printer.SendCmd.return_value = True
        self.mock_printer.ReadFpStatus.return_value = "0 0 Sin error"

        result = self.printer.print_report_x()
        self.assertTrue(result["success"])
        self.mock_printer.SendCmd.assert_called_with("I0X")

    def test_print_report_z(self):
        """Prueba el método print_report_z"""

        self.mock_printer.OpenFpctrl.return_value = True
        self.mock_printer._HandleCTSRTS.return_value = True
        self.mock_printer.SendCmd.return_value = True
        self.mock_printer.ReadFpStatus.return_value = "0 0 Sin error"

        result = self.printer.print_report_z()
        self.assertTrue(result["success"])
        self.mock_printer.SendCmd.assert_called_with("I0Z")

    def test_validate_printer_state(self):
        """Prueba el método _validate_printer_state"""

        self.printer.config["enabled"] = False
        result = self.printer._validate_printer_state()
        self.assertFalse(result["success"])
        self.assertIn("deshabilitada", result["message"])

        self.printer.config["enabled"] = True
        self.mock_printer.OpenFpctrl.return_value = False
        result = self.printer._validate_printer_state()
        self.assertFalse(result["success"])
        self.assertIn("No se pudo conectar", result["message"])

        self.mock_printer.OpenFpctrl.return_value = True
        self.mock_printer._HandleCTSRTS.return_value = True
        self.mock_printer.ReadFpStatus.return_value = "1 0 Error de impresora"
        result = self.printer._validate_printer_state()
        self.assertFalse(result["success"])
        self.assertIn("Error de impresora", result["message"])


if __name__ == "__main__":
    unittest.main()
