#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright © 2024, Iron Graterol
Licensed under the GNU Affero General Public License, version 3 or later.

Clase para gestionar el contador fiscal usando un archivo JSON.
"""

import datetime
import json
import logging
from typing import Dict

logger = logging.getLogger(__name__)


class FiscalCounter:  # pylint: disable=R0903
    """
    Clase para gestionar el contador fiscal usando un archivo JSON.
    Métodos:
    - update_counter: Actualiza los contadores y devuelve los datos actualizados.
    """

    def __init__(self, template_file: str) -> None:
        """
        Inicializa la clase con el archivo de template que contiene los contadores.
        Args:
            template_file: Ruta al archivo de template JSON que contiene los contadores.
        """
        self.template_file = template_file
        self.template = self._read_template()

    def _read_template(self) -> Dict:
        """
        Lee el template JSON que contiene los contadores.
        Si no existe la sección counter, se crea con valores por defecto.
        Returns:
            Dict: Template completo con los contadores
        """
        try:
            with open(self.template_file, "r", encoding="utf-8") as file:
                template = json.load(file)

            if "counter" not in template:
                fecha_hoy = datetime.date.today().strftime("%Y-%m-%d")
                template["counter"] = {
                    "document_date": fecha_hoy,
                    "document_invoice": "00000000",
                    "document_credit": "00000000",
                    "document_debit": "00000000",
                    "document_note": "00000000",
                    "machine_report": "0001",
                    "machine_serial": "Z1B1234567",
                }
                self._write_template(template)
            return template
        except FileNotFoundError:
            logger.error("El archivo %s no se encontró.", self.template_file)
            raise
        except json.JSONDecodeError:
            logger.error("El archivo %s no es un JSON válido.", self.template_file)
            raise
        except Exception as e:
            logger.error("Error leyendo template: %s", str(e))
            raise

    def _write_template(self, template: Dict) -> None:
        """
        Escribe el template actualizado en el archivo JSON.
        Args:
            template: Template completo con los contadores actualizados
        """
        try:
            with open(self.template_file, "w", encoding="utf-8") as file:
                json.dump(template, file, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error("Error escribiendo template: %s", str(e))
            raise

    def update_counter(self, document_type: str = "invoice") -> Dict[str, str]:
        """
        Actualiza los contadores y escribe los datos actualizados en el template.
        Args:
            document_type: Tipo de documento ('invoice', 'credit', 'debit', 'note')
        Returns:
            Dict[str, str]: Datos actualizados del contador fiscal
        """
        try:
            fecha_hoy = datetime.date.today().strftime("%Y-%m-%d")
            counter = self.template["counter"]

            counter_mapping = {
                "invoice": "document_invoice",
                "credit": "document_credit",
                "debit": "document_debit",
                "note": "document_note",
            }

            counter_key = counter_mapping.get(document_type, "document_invoice")

            if counter["document_date"] != fecha_hoy:
                old_date = counter["document_date"]
                old_report = counter["machine_report"]
                counter["document_date"] = fecha_hoy
                counter["machine_report"] = str(int(counter["machine_report"]) + 1).zfill(4)
                logger.info(
                    "Nuevo día detectado. Fecha: %s -> %s\nReporte: %s -> %s",
                    old_date,
                    fecha_hoy,
                    old_report,
                    counter["machine_report"],
                )
            else:
                counter["machine_report"] = counter["machine_report"].zfill(4)

            old_number = counter[counter_key]  # Incrementar documento específico
            counter[counter_key] = str(int(counter[counter_key]) + 1).zfill(8)

            logger.info(
                "Incrementando contador %s: %s -> %s",
                counter_key,
                old_number,
                counter[counter_key],
            )
            self._write_template(self.template)
            return {
                "document_date": counter["document_date"],
                "document_number": counter[counter_key],
                "machine_serial": counter["machine_serial"],
                "machine_report": counter["machine_report"],
            }

        except Exception as e:
            logger.error("Error actualizando contador para %s: %s", document_type, str(e))
            raise
