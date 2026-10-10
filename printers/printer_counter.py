#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright © 2024, Iron Graterol
Licensed under the GNU Affero General Public License, version 3 or later.

Clase para gestionar el contador fiscal emulado de las impresoras no fiscales.
Los contadores viven en SQLite (tabla counters de data/print_jobs.db); la sección "counter" del
template JSON solo se lee una vez como semilla de la migración inicial y ya no se escribe.
"""

import datetime
import json
import logging
import threading
from typing import ClassVar

from server.handlers import job_store

logger = logging.getLogger(__name__)


class FiscalCounter:  # pylint: disable=R0903
    """
    Clase para gestionar el contador fiscal emulado (matriz y ticket) guardado en SQLite.
    Métodos:
    - reserve_counter: Calcula el siguiente número sin persistirlo.
    - commit_counter: Persiste los valores previamente reservados (nunca retrocede un número confirmado).

    Atributos de clase:
    - LOCK: cerrojo reentrante compartido por todas las instancias (cada petición crea la suya) para
      serializar la secuencia reservar -> imprimir -> confirmar.

    La clave de la impresora ("matrix" o "ticket") identifica su fila en la tabla counters. Si la fila no
    existe se siembra una única vez desde la sección "counter" del template JSON (o con ceros); después el
    JSON deja de ser la fuente, no se escribe y se conserva como respaldo.
    """

    LOCK = threading.RLock()

    COUNTER_MAPPING: ClassVar[dict[str, str]] = {
        "invoice": "document_invoice",
        "credit": "document_credit",
        "debit": "document_debit",
        "note": "document_note",
    }

    def __init__(self, template_file: str, printer_key: str) -> None:
        """
        Inicializa la clase con el template de la impresora (solo como semilla) y su clave de contador.
        Args:
            template_file: Ruta al template JSON; se lee únicamente para sembrar el contador la primera vez.
            printer_key: Clave de la impresora en la tabla counters ("matrix" o "ticket").
        """
        self.template_file = template_file
        self.printer_key = printer_key

    def _default_counter(self) -> dict[str, str]:
        """
        Valores iniciales cuando no hay sección counter utilizable en el template.
        Returns:
            dict[str, str]: Contador en cero con la fecha de hoy
        """
        return {
            "document_date": datetime.date.today().strftime("%Y-%m-%d"),  # noqa: DTZ011 - fecha local
            "document_invoice": "00000000",
            "document_credit": "00000000",
            "document_debit": "00000000",
            "document_note": "00000000",
            "machine_report": "0001",
            "machine_serial": "Z1B1234567",
        }

    def _seed_counter(self) -> dict[str, str]:
        """
        Obtiene los valores de siembra: la sección counter del template si es válida, si no los valores por defecto.
        Solo LEE el template (nunca lo escribe). Un template ausente, ilegible o con la sección incompleta no
        impide sembrar: se usan los valores por defecto.
        Returns:
            dict[str, str]: Valores iniciales del contador
        """
        defaults = self._default_counter()
        try:
            with open(self.template_file, "r", encoding="utf-8") as file:
                counter = json.load(file)["counter"]
            seed = {field: str(counter[field]) for field in job_store.COUNTER_FIELDS}
            for field in (*self.COUNTER_MAPPING.values(), "machine_report"):
                int(seed[field])
            datetime.date.fromisoformat(seed["document_date"])
        except (OSError, ValueError, KeyError, TypeError) as e:
            logger.warning(
                "Sin sección counter válida en %s (%s): el contador %s inicia con valores por defecto",
                self.template_file,
                str(e),
                self.printer_key,
            )
            return defaults
        logger.info("Migrando contador '%s' desde el template %s", self.printer_key, self.template_file)
        return seed

    def _load_counter(self) -> dict[str, str]:
        """
        Lee el contador vigente de SQLite, sembrándolo desde el template la primera vez.
        Returns:
            dict[str, str]: Valores actuales del contador
        """
        return job_store.load_counter(self.printer_key, self._seed_counter)

    def reserve_counter(self, document_type: str = "invoice") -> dict[str, str]:
        """
        Calcula los valores del siguiente documento SIN persistirlos.
        Relee el contador de SQLite bajo el cerrojo, porque otra petición pudo confirmar un número
        desde que se construyó esta instancia. Aplica el cambio de día del reporte y el número de 8 dígitos.
        Args:
            document_type: Tipo de documento ('invoice', 'credit', 'debit', 'note')
        Returns:
            Dict[str, str]: document_date, document_number, machine_serial y machine_report
        """
        with self.LOCK:
            counter = self._load_counter()
            fecha_hoy = datetime.date.today().strftime("%Y-%m-%d")  # noqa: DTZ011 - fecha local
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
        Persiste en SQLite los valores obtenidos con reserve_counter, en una sola transacción.
        Un número ya confirmado nunca se repite ni disminuye: si el guardado es mayor o igual al reservado
        se lanza CounterRegressionError y no se modifica nada.
        Args:
            document_type: Tipo de documento ('invoice', 'credit', 'debit', 'note')
            reserved: Diccionario devuelto por reserve_counter
        """
        try:
            with self.LOCK:
                counter_key = self.COUNTER_MAPPING.get(document_type, "document_invoice")
                self._load_counter()  # Garantiza que la fila exista (migración) antes de confirmar
                job_store.commit_counter_row(self.printer_key, counter_key, reserved)
                logger.info("Contador %s confirmado: %s", counter_key, reserved["document_number"])
        except Exception as e:
            logger.error("Error confirmando contador para %s: %s", document_type, str(e))
            raise
