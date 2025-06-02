#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright © 2024, Iron Graterol
Licensed under the GNU Affero General Public License, version 3 or later.

Clase base abstracta para todas las impresoras
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any

logger = logging.getLogger(__name__)


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
    def check_status(self) -> Dict[str, Any]:
        """
        Método abstracto para verificar el estado de la impresora
        Returns:
            Dict[str, Any]: Estado de la impresora
        """

    def __enter__(self):
        """Permite usar la impresora con context manager (with)"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Asegura que la impresora se desconecte al salir del context"""
        self.disconnect()
