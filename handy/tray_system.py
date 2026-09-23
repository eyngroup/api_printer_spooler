#!/usr/bin/env python
"""
Copyright © 2024, Iron Graterol
Licensed under the GNU Affero General Public License, version 3 or later.

Gestión del ícono en la bandeja del sistema
"""

# Librerías estándar
import logging
import os
import threading

# Librerías de terceros
import pystray
from flask import request
from PIL import Image

# Módulos locales
from handy.tools import get_base_path

# Configuración del logging
logger = logging.getLogger(__name__)


class TrayManager:
    """Gestiona el ícono y menú en la bandeja del sistema."""

    def __init__(self, app, base_path: str, main_window=None) -> None:
        """Inicializa el administrador de la bandeja del sistema.
        Args:
            app: Instancia de la aplicación Flask
            base_path: Ruta base de la aplicación
            main_window: Instancia de views.main_window.MainWindow. Sus métodos
                request_show()/request_hide()/request_quit() son thread-safe y
                son la única forma correcta de interactuar con ella desde acá,
                ya que este código corre en el hilo de pystray, no en el de Tk.
        """
        self.app = app
        self.logger: logging.Logger = logging.getLogger(__name__)
        self.base_path: str = base_path
        self.icon: pystray.Icon | None = None
        self.main_window = main_window

    def create_menu(self) -> pystray.Menu:
        """Crea el menú contextual del ícono.
        Returns:
            Menu configurado para el ícono de la bandeja
        """
        return pystray.Menu(
            pystray.MenuItem("Abrir Panel", self.show_panel, default=True),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Salir", self.stop),
        )

    def show_panel(self) -> None:
        """Solicita mostrar la ventana principal (Consola, Configuración, Fiscal).
        Args:
            icon: Ícono de la bandeja
            item: Ítem del menú seleccionado
        """
        if self.main_window:
            self.main_window.request_show()

    def stop(self) -> None:
        """Detiene la aplicación y limpia los recursos.
        Args:
            icon: Ícono de la bandeja
            item: Ítem del menú seleccionado
        """
        try:
            if self.icon:
                self.icon.stop()

            if self.main_window:
                self.main_window.request_quit()

            if self.app:
                try:
                    func = request.environ.get("werkzeug.server.shutdown")
                    if func is None:
                        self.app.shutdown()
                    else:
                        func()
                except Exception:
                    os._exit(0)

            os._exit(0)
        except Exception as e:
            logger.error("Error al detener la aplicación: %s", str(e))
            os._exit(1)

    def run(self) -> None:
        """Inicia el ícono en la bandeja del sistema."""
        try:
            icon_path = os.path.join(get_base_path(), "resources", "printer_fiscal.ico")
            if not os.path.exists(icon_path):
                logger.error("No se pudo encontrar el ícono en: %s", icon_path)
                return

            image = Image.open(icon_path)
            self.icon = pystray.Icon("API Printer Server", image, "API Printer Server", self.create_menu())

            threading.Thread(target=self.icon.run, daemon=True).start()
            logger.info("System tray iniciado correctamente")
        except Exception as e:
            logger.error("Error al iniciar system tray: %s", str(e))
