#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright © 2024, Iron Graterol
Licensed under the GNU Affero General Public License, version 3 or later.

Clase base abstracta para todas las impresoras
"""

import json
import logging
import os
from abc import ABC, abstractmethod
from typing import Dict, Any

logger = logging.getLogger(__name__)


class FiscalPrinterMixin:
    """Mixin con lógica común para impresoras fiscales."""

    def _load_config(self, file_name: str, local_path: str) -> Dict[str, Any]:
        """
        Carga un archivo de configuración JSON desde el directorio especificado.
        Args:
            file_name (str): Nombre del archivo de configuración
            local_path (str): Directorio donde se encuentra el archivo
        Returns:
            Dict[str, Any]: Configuración cargada del archivo JSON
        """
        try:
            from handy.tools import get_base_path

            config_path = os.path.join(get_base_path(), local_path, file_name)
            if not os.path.exists(config_path):
                logger.warning("Archivo de configuración no encontrado: %s", config_path)
                return {}

            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning("Error cargando configuración %s: %s", file_name, str(e))
            return {}

    def format_status_message(self, status: Dict[str, Any]) -> tuple[str, str]:
        """
        Formatea el mensaje de status para logging/respuesta.
        Args:
            status: Dict con datos de status de la impresora.
        Returns:
            Tupla (status_message, error_message).
        """
        return (status.get("status", "unknown"), status.get("error", "none"))


class BasePrinter(ABC):
    """Clase base abstracta para todas las impresoras"""

    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa la impresora con su configuración
        Args:
            config: Diccionario con la configuración de la impresora
        """
        self.config = config
        self.name = config.get(f"{self.__class__.__name__.lower().replace('printer', '')}_name", "Unknown")
        self.connection = config.get("connection", {})
        self.template = config.get("template")
        self.is_connected = False

    @abstractmethod
    def connect(self) -> bool:
        """Método abstracto para establecer conexión con la impresora  Returns:bool"""

    @abstractmethod
    def disconnect(self) -> None:
        """Método abstracto para cerrar la conexión con la impresora"""

    @abstractmethod
    def print_document(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Método abstracto para imprimir un documento
        Args:
            data: Diccionario con los datos del documento a imprimir
        Returns:
            Dict[str, Any]: Resultado de la impresión
        """

    @abstractmethod
    def check_status(self) -> bool | Dict[str, Any]:
        """
        Método abstracto para verificar el estado de la impresora
        Returns:
            bool | Dict[str, Any]: Estado de la impresora (bool para HKA, Dict para otros)
        """

    def __enter__(self):
        """Permite usar la impresora con context manager (with)"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Asegura que la impresora se desconecte al salir del context"""
        self.disconnect()
