#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright © 2024, Iron Graterol
Licensed under the GNU Affero General Public License, version 3 or later.

Módulo para escanear puertos seriales en diferentes sistemas operativos.
"""

import sys
import glob
from typing import List, Dict
import logging
import serial
from serial.tools import list_ports

from controllers.pfhka import FiscalPrinterHka
from controllers.pfpnp import FiscalPrinterPnp

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

    COMMON_BAUDRATES = [1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200]

    @staticmethod
    def check_port_availability(port_comm: str) -> bool:
        """Verifica si un puerto está disponible para usar.

        Args:
            port_comm: Nombre del puerto a verificar

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


# VID:PID de convertidores/puertos USB conocidos para impresoras fiscales, en orden de prioridad.
KNOWN_FISCAL_USB_IDS: tuple[tuple[int, int], ...] = (
    (0x28E9, 0x018A),  # GigaDevice GD32 CDC-ACM: USB nativo de la TFHKA HKA80 (verificado)
    (0x067B, 0x2303),  # Prolific PL2303
    (0x067B, 0x23A3),  # Prolific PL2303GC
    (0x1A86, 0x7523),  # CH340
    (0x0403, 0x6001),  # FTDI FT232
    (0x0403, 0x6015),  # FTDI FT231X
    (0x10C4, 0xEA60),  # Silicon Labs CP210x
)


def _is_bluetooth_port(port_info) -> bool:
    """Indica si el puerto es un COM de Bluetooth (nunca debe sondearse)."""
    text = f"{getattr(port_info, 'description', '')} {getattr(port_info, 'hwid', '')}".lower()
    return "bluetooth" in text or "bthenum" in text


def _rank_candidates(current_port: str | None) -> list[tuple[str, str]]:
    """Lista los puertos candidatos ordenados por prioridad.

    Orden: (0) puerto configurado, (1) VID:PID conocidos según ``KNOWN_FISCAL_USB_IDS``, (2) otros puertos USB.
    Se excluyen los puertos Bluetooth y los que no tienen VID (no USB), salvo el puerto configurado.

    Returns:
        list[tuple[str, str]]: Pares (dispositivo, descripción legible con vid:pid) en orden de prueba.
    """
    ranked: list[tuple[int, int, str, str]] = []
    seen_current = False
    for index, info in enumerate(list_ports.comports()):
        device = info.device
        if _is_bluetooth_port(info):
            continue
        vid, pid = getattr(info, "vid", None), getattr(info, "pid", None)
        label = (
            f"{vid:04x}:{pid:04x} {info.description}" if vid is not None and pid is not None else str(info.description)
        )
        if current_port and device == current_port:
            ranked.append((0, index, device, label))
            seen_current = True
        elif vid is None:
            continue
        elif (vid, pid) in KNOWN_FISCAL_USB_IDS:
            ranked.append((1 + KNOWN_FISCAL_USB_IDS.index((vid, pid)) / 100, index, device, label))
        else:
            ranked.append((2, index, device, label))
    if current_port and not seen_current:
        # El puerto configurado se prueba aunque no aparezca listado (p. ej. puerto virtual).
        ranked.append((0, -1, current_port, "configurado"))
    ranked.sort(key=lambda item: (item[0], item[1]))
    return [(device, label) for _, _, device, label in ranked]


def _probe_fiscal_port(printer_type: str, port: str, baudrate: int, timeout: float) -> bool:
    """Confirma con una consulta de solo lectura que una impresora fiscal responde en el puerto.

    - TFHKA: ENQ (estado). Confirmada si devuelve un ``status_code`` distinto de 0 (los errores de CTS, timeout o LRC
      devuelven 0).
    - PNP: comando 8|V (estado). Confirmada si devuelve un diccionario con ``status_code``.
      TODO: la confirmación PNP aún no está verificada en hardware real.

    No se envía ningún otro comando. Cualquier excepción cuenta como no confirmada.
    """
    printer = None
    try:
        if printer_type == "tfhka":
            printer = FiscalPrinterHka(port, baudrate, timeout)
        elif printer_type == "pnp":
            printer = FiscalPrinterPnp(port, baudrate, timeout)
        else:
            return False
        if not printer.open_port():
            return False
        status = printer.get_status()
        if not isinstance(status, dict):
            return False
        if printer_type == "tfhka":
            return bool(status.get("status_code"))
        return "status_code" in status
    except Exception as exc:  # noqa: BLE001 - cualquier fallo del sondeo descarta el candidato y se prueba el siguiente
        logger.debug("Fallo sondeando %s: %s", port, exc)
        return False
    finally:
        if printer is not None:
            try:
                printer.close_port()
            except Exception as exc:  # noqa: BLE001 - un fallo al cerrar no debe interrumpir la detección
                logger.debug("No se pudo cerrar %s tras el sondeo: %s", port, exc)


def find_fiscal_port(
    printer_type: str, current_port: str | None, baudrate: int = 9600, timeout: float = 1.0
) -> str | None:
    """Encuentra el puerto serial de la impresora fiscal confirmándolo con un handshake de solo lectura.

    Multiplataforma (Windows/Linux): usa ``serial.tools.list_ports.comports()``. Los candidatos se prueban por
    prioridad (ver ``_rank_candidates``) y se devuelve el primero confirmado.

    Args:
        printer_type: ``"tfhka"`` o ``"pnp"`` (sin distinguir mayúsculas).
        current_port: Puerto configurado actualmente, si existe.
        baudrate: Velocidad del puerto.
        timeout: Tiempo de espera de lectura.

    Returns:
        str | None: Puerto confirmado, o None si ninguno respondió.
    """
    kind = (printer_type or "").strip().lower()
    candidates = _rank_candidates(current_port)
    if not candidates:
        logger.warning("No hay puertos seriales candidatos para la impresora fiscal.")
        return None
    for device, label in candidates:
        logger.info("Sondeando %s (%s) como impresora %s...", device, label, kind)
        if _probe_fiscal_port(kind, device, baudrate, timeout):
            logger.info("Impresora fiscal %s confirmada en %s (%s).", kind, device, label)
            return device
        logger.info("Sin respuesta de impresora fiscal en %s (%s).", device, label)
    logger.warning(
        "No se confirmó ninguna impresora fiscal. Puertos probados: %s",
        ", ".join(f"{d} ({lbl})" for d, lbl in candidates),
    )
    return None
