#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Módulo para escanear puertos seriales en diferentes sistemas operativos."""

import sys
import glob
from typing import List, Dict
import logging
import serial
from serial.tools import list_ports

logger = logging.getLogger(__name__)


class WindowsSerialScanner:
    """Escáner de puertos seriales para sistemas Windows.

    Esta clase proporciona métodos para detectar y listar puertos COM
    disponibles en sistemas Windows.
    """

    COMMON_BAUDRATES = [1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200]

    @staticmethod
    def scan_ports() -> List[Dict[str, str]]:
        """Escanea los puertos COM disponibles en Windows.

        Returns:
            List[Dict[str, str]]: Lista de puertos encontrados con su información.
            Cada puerto es un diccionario con:
            - port: Nombre del puerto
            - description: Descripción del dispositivo
            - hardware_id: ID de hardware si está disponible
        """
        ports_comm = []
        try:
            for port_device in list_ports.comports():
                port_info = {
                    "port": port_device.device,
                    "description": port_device.description,
                    "hardware_id": port_device.hwid if hasattr(port_device, "hwid") else "N/A",
                }
                ports_comm.append(port_info)
                logger.debug("Puerto encontrado: %s", port_info)
        except Exception as e:
            logger.error("Error escaneando puertos Windows: %s", str(e))

        return ports_comm

    @staticmethod
    def check_port_availability(port_comm: str) -> bool:
        """Verifica si un puerto está disponible para usar.

        Args:
            port: Nombre del puerto a verificar

        Returns:
            bool: True si el puerto está disponible, False si está en uso
        """
        try:
            s = serial.Serial(port_comm)
            s.close()
            return True
        except Exception:
            return False

    @staticmethod
    def test_baudrates(port_comm: str) -> List[int]:
        """Prueba diferentes velocidades en el puerto.

        Args:
            port: Nombre del puerto a probar

        Returns:
            List[int]: Lista de baudrates que funcionaron correctamente
        """
        working_baudrates = []
        for rate in WindowsSerialScanner.COMMON_BAUDRATES:
            try:
                s = serial.Serial(port_comm, rate, timeout=0.5)
                s.close()
                working_baudrates.append(rate)
            except Exception:
                continue
        return working_baudrates

    @staticmethod
    def detect_device_type(port_comm: str) -> str:
        """Intenta detectar el tipo de dispositivo conectado.

        Args:
            port: Nombre del puerto a analizar

        Returns:
            str: Tipo de dispositivo detectado o 'Unknown'
        """
        try:
            s = serial.Serial(port_comm, 9600, timeout=1)
            # Aquí podrías agregar comandos específicos para detectar
            # diferentes tipos de dispositivos
            s.write(b"\x10\x04")  # Ejemplo: comando de status
            response = s.read(32)
            s.close()

            # Análisis básico de respuesta
            if response and response[0] == 0x1:
                return "Fiscal Printer"
            return "Generic Serial Device"
        except Exception:
            return "Unknown"


class LinuxSerialScanner:  # pylint: disable=R0903
    """Escáner de puertos seriales para sistemas Linux.

    Esta clase proporciona métodos para detectar y listar puertos seriales
    disponibles en sistemas Linux.
    """

    @staticmethod
    def scan_ports() -> List[Dict[str, str]]:
        """Escanea los puertos seriales disponibles en Linux.

        Returns:
            List[Dict[str, str]]: Lista de puertos encontrados con su información.
            Cada puerto es un diccionario con:
            - port: Nombre del puerto
            - description: Descripción del dispositivo
            - hardware_id: ID de hardware si está disponible
        """
        ports_comm = []
        try:
            # Buscar puertos USB-Serial
            for port_device in glob.glob("/dev/ttyUSB*") + glob.glob("/dev/ttyACM*"):
                try:
                    s = serial.Serial(port_device)
                    s.close()
                    port_info = {"port": port_device, "description": "USB-Serial Device", "hardware_id": "N/A"}
                    ports_comm.append(port_info)
                    logger.debug("Puerto encontrado: %s", port_info)
                except Exception:
                    continue
        except Exception as e:
            logger.error("Error escaneando puertos Linux: %s", str(e))

        return ports_comm


def get_serial_scanner():
    """Factory para obtener el escáner apropiado según el sistema operativo.

    Returns:
        Type[WindowsSerialScanner|LinuxSerialScanner]: Clase del escáner apropiado
    """
    if sys.platform.startswith("win"):
        return WindowsSerialScanner
    return LinuxSerialScanner


if __name__ == "__main__":
    # Configuración básica de logging para pruebas
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

    # Obtener el escáner apropiado y buscar puertos
    scanner = get_serial_scanner()
    ports = scanner.scan_ports()

    if ports:
        print("\nPuertos seriales encontrados:")
        print("-" * 50)
        for port in ports:
            print(f"Puerto: {port['port']}")
            print(f"Descripción: {port['description']}")
            print(f"Hardware ID: {port['hardware_id']}")
            print("-" * 50)
    else:
        print("\nNo se encontraron puertos seriales.")

    # Pruebas adicionales
    if ports:
        for port in ports:
            port_name = port["port"]
            print(f"\nPruebas adicionales para {port_name}:")
            print("-" * 50)

            # Verificar disponibilidad
            available = scanner.check_port_availability(port_name)
            print(f"Disponible: {'Sí' if available else 'No'}")

            if available:
                # Probar baudrates
                baudrates = scanner.test_baudrates(port_name)
                print(f"Baudrates soportados: {baudrates}")

                # Detectar tipo de dispositivo
                device_type = scanner.detect_device_type(port_name)
                print(f"Tipo de dispositivo: {device_type}")
