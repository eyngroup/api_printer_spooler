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
import threading
from typing import ClassVar, Dict

logger = logging.getLogger(__name__)


class FiscalCounter:  # pylint: disable=R0903
    """
    Clase para gestionar el contador fiscal usando un archivo JSON.
    Métodos:
    - update_counter: Actualiza los contadores y devuelve los datos actualizados.
    - reserve_counter: Calcula el siguiente número sin escribirlo en disco.
    - commit_counter: Persiste en disco los valores previamente reservados.

    Atributos de clase:
    - LOCK: cerrojo reentrante compartido por todas las instancias (cada petición crea la suya) para
      serializar la secuencia reservar -> imprimir -> confirmar.
    """

    LOCK = threading.RLock()

    COUNTER_MAPPING: ClassVar[dict[str, str]] = {
        "invoice": "document_invoice",
        "credit": "document_credit",
        "debit": "document_debit",
        "note": "document_note",
    }

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

    def reserve_counter(self, document_type: str = "invoice") -> dict[str, str]:
        """
        Calcula los valores del siguiente documento SIN escribirlos en disco.
        Relee el template del disco bajo el cerrojo, porque otra petición pudo confirmar un número
        desde que se construyó esta instancia. Aplica la misma lógica que update_counter (cambio de
        día del reporte y número de 8 dígitos).
        Args:
            document_type: Tipo de documento ('invoice', 'credit', 'debit', 'note')
        Returns:
            Dict[str, str]: Mismos datos que devuelve update_counter
        """
        with self.LOCK:
            self.template = self._read_template()
            counter = self.template["counter"]
            fecha_hoy = datetime.date.today().strftime("%Y-%m-%d")  # noqa: DTZ011 - fecha local, igual que update_counter
            counter_key = self.COUNTER_MAPPING.get(document_type, "document_invoice")

            if counter["document_date"] != fecha_hoy:
                machine_report = str(int(counter["machine_report"]) + 1).zfill(4)
            else:
                machine_report = counter["machine_report"].zfill(4)

            return {
                "document_date": fecha_hoy,
                "document_number": str(int(counter[counter_key]) + 1).zfill(8),
                "machine_serial": counter["machine_serial"],
                "machine_report": machine_report,
            }

    def commit_counter(self, document_type: str, reserved: dict[str, str]) -> None:
        """
        Persiste en disco los valores obtenidos con reserve_counter.
        Relee el template bajo el cerrojo antes de escribir para no pisar cambios ajenos.
        Args:
            document_type: Tipo de documento ('invoice', 'credit', 'debit', 'note')
            reserved: Diccionario devuelto por reserve_counter
        """
        try:
            with self.LOCK:
                self.template = self._read_template()
                counter = self.template["counter"]
                counter_key = self.COUNTER_MAPPING.get(document_type, "document_invoice")

                counter["document_date"] = reserved["document_date"]
                counter["machine_report"] = reserved["machine_report"]
                counter[counter_key] = reserved["document_number"]
                self._write_template(self.template)
                logger.info("Contador %s confirmado: %s", counter_key, reserved["document_number"])
        except Exception as e:
            logger.error("Error confirmando contador para %s: %s", document_type, str(e))
            raise
