#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright © 2024, Iron Graterol
Licensed under the GNU Affero General Public License, version 3 or later.

Gestión del ícono en la bandeja del sistema
"""

# Librerías estándar
import os
import threading
import queue
from datetime import datetime
import logging
import tkinter as tk
from tkinter import scrolledtext

# Librerías de terceros
import pystray
from PIL import Image
from flask import request

# Módulos locales
from server.config_loader import ConfigManager
from handy.tools import get_base_path

# Configuración del logging
logger = logging.getLogger(__name__)


class LogViewer:
    """Clase para mostrar y gestionar la ventana de logs del sistema."""

    def __init__(self, log_dir: str) -> None:
        """Inicializa el visor de logs.
        Args:
            log_dir: Ruta al directorio de logs
        """
        logger.debug(log_dir)
        self.root: tk.Tk | None = None
        self.text_area: scrolledtext.ScrolledText | None = None
        self.log_dir: str = os.path.join(get_base_path(), "logs")
        self.config: dict = ConfigManager.get_config()
        self.queue: queue.Queue = queue.Queue()
        self.is_running: bool = False
        self.tk_thread: threading.Thread | None = None

    def start_tk_thread(self) -> None:
        """Inicia el thread dedicado para la interfaz Tkinter."""
        if self.tk_thread is None:
            self.tk_thread = threading.Thread(target=self._tk_mainloop, daemon=True)
            self.tk_thread.start()

    def _tk_mainloop(self) -> None:
        """Ejecuta el loop principal de Tkinter en un thread separado."""
        self.create_window()
        self.root.mainloop()

    def create_window(self) -> None:
        """Crea y configura la ventana principal y sus widgets."""
        try:
            self.root = tk.Tk()
            self.root.title("API Printer Server - Logs")
            self.root.geometry("800x600")
            self.is_running = True

            self.root.configure(bg="#f0f0f0")  # Configurar colores y estilos
            button_style = {
                "bg": "#2196F3",  # Azul material design
                "fg": "white",
                "font": ("Segoe UI", 9),
                "relief": "flat",
                "padx": 15,
                "pady": 5,
                "cursor": "hand2",  # Cursor tipo mano
            }

            icon_path = os.path.join(get_base_path(), "resources", "printer_fiscal.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)

            main_frame = tk.Frame(self.root, bg="#f0f0f0")
            main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            self.text_area = scrolledtext.ScrolledText(
                main_frame,
                wrap=tk.WORD,
                font=("Consolas", 10),
                bg="white",
                fg="#333333",
                selectbackground="#0078D7",
                selectforeground="white",
                padx=5,
                pady=5,
            )  # Configurar área de texto con mejor apariencia
            self.text_area.pack(fill=tk.BOTH, expand=True)
            self.text_area.config(state="disabled")

            # Frame para botones con mejor espaciado
            button_frame = tk.Frame(main_frame, bg="#f0f0f0")
            button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

            refresh_button = tk.Button(
                button_frame, text="Actualizar", command=lambda: self.queue.put("update"), **button_style
            )
            refresh_button.pack(side=tk.LEFT, padx=5)

            copy_button = tk.Button(button_frame, text="Copiar", command=lambda: self.queue.put("copy"), **button_style)
            copy_button.pack(side=tk.LEFT, padx=5)

            close_button = tk.Button(
                button_frame, text="Cerrar", command=lambda: self.queue.put("hide"), **button_style
            )
            close_button.pack(side=tk.RIGHT, padx=5)

            # Eventos hover para botones
            for button in [refresh_button, copy_button, close_button]:
                button.bind("<Enter>", lambda e, b=button: b.configure(bg="#1976D2"))
                button.bind("<Leave>", lambda e, b=button: b.configure(bg="#2196F3"))

            self.root.protocol("WM_DELETE_WINDOW", lambda: self.queue.put("hide"))

            # Centrar la ventana
            self.root.update_idletasks()
            width = self.root.winfo_width()
            height = self.root.winfo_height()
            x = (self.root.winfo_screenwidth() // 2) - (width // 2)
            y = (self.root.winfo_screenheight() // 2) - (height // 2)
            self.root.geometry(f"{width}x{height}+{x}+{y}")

            self.root.withdraw()
            self.process_queue()

        except Exception as e:
            logger.error("Error al crear ventana de logs: %s", str(e))

    def process_queue(self) -> None:
        """Procesa las tareas pendientes en la cola de eventos."""
        if not self.root:
            return

        try:
            while self.queue.qsize():
                task = self.queue.get_nowait()
                if task == "update":
                    self._update_logs()
                elif task == "show":
                    self.root.deiconify()
                    self.root.lift()
                    self.root.focus_force()
                elif task == "hide":
                    self.root.withdraw()
                elif task == "copy":
                    self._copy_logs()
                elif task == "destroy":
                    self.root.quit()
                    return

            self.root.after(100, self.process_queue)
        except Exception as e:
            logger.error("Error procesando cola: %s", str(e))

    def _copy_logs(self) -> None:
        """Copia el contenido actual de los logs al portapapeles."""
        try:
            content = self.text_area.get(1.0, tk.END)
            self.root.clipboard_clear()
            self.root.clipboard_append(content)
            logger.info("Contenido de logs copiado al portapapeles")
        except Exception as e:
            logger.error("Error al copiar logs: %s", str(e))

    def show(self) -> None:
        """Muestra la ventana de logs y actualiza su contenido."""
        if self.tk_thread is None:
            self.start_tk_thread()
        self.queue.put("show")
        self.queue.put("update")

    def hide(self) -> None:
        """Oculta la ventana de logs."""
        self.queue.put("hide")

    def destroy(self) -> None:
        """Destruye la ventana y limpia los recursos."""
        if self.root:
            self.queue.put("destroy")
            if self.tk_thread:
                self.tk_thread.join(timeout=1.0)

    def _update_logs(self) -> None:
        """Actualiza el contenido del área de texto con los logs más recientes."""
        try:
            if not self.root or not self.text_area or not self.config:
                logger.error("No se pueden mostrar los logs: ventana no inicializada")
                return

            self.text_area.config(state="normal")  # Habilitar para actualizar
            self.text_area.delete(1.0, tk.END)
            current_date = datetime.now().strftime("%Y%m%d")
            log_file_name = self.config.get("logging", {}).get("log_file", "api_service")
            log_file = os.path.join(self.log_dir, f"{log_file_name}-{current_date}.log")
            logger.debug("Leer archivo de logs: %s", log_file)

            if os.path.exists(log_file):
                try:
                    with open(log_file, "r", encoding="utf-8") as f:
                        logs = f.read()
                        if logs.strip():
                            self.text_area.insert(tk.END, logs)
                            self.text_area.see(tk.END)
                            logger.info("Logs actualizados correctamente")
                        else:
                            self.text_area.insert(tk.END, "El archivo de logs está vacío.")
                except Exception as e:
                    error_msg = f"Error al leer logs: {str(e)}"
                    self.text_area.insert(tk.END, error_msg)
                    logger.error(error_msg)
            else:
                error_msg = f"No se encontró el archivo de logs para hoy: {log_file}"
                self.text_area.insert(tk.END, error_msg)
                logger.warning(error_msg)

            self.text_area.config(state="disabled")  # Deshabilitar después de actualizar

        except Exception as e:
            logger.error("Error al actualizar logs: %s", str(e))


class TrayManager:
    """Gestiona el ícono y menú en la bandeja del sistema."""

    def __init__(self, app, base_path: str) -> None:
        """Inicializa el administrador de la bandeja del sistema.
        Args:
            app: Instancia de la aplicación Flask
            base_path: Ruta base de la aplicación
        """
        self.app = app
        self.logger: logging.Logger = logging.getLogger(__name__)
        self.base_path: str = base_path
        self.icon: pystray.Icon | None = None
        self.log_viewer: LogViewer = LogViewer(os.path.join(get_base_path(), "logs"))

    def create_menu(self) -> pystray.Menu:
        """Crea el menú contextual del ícono.
        Returns:
            Menu configurado para el ícono de la bandeja
        """
        return pystray.Menu(
            pystray.MenuItem("Ver Logs", self.show_logs, default=True),
            pystray.MenuItem("Ver Estado", self.show_status),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Salir", self.stop),
        )

    def show_logs(self) -> None:
        """Muestra la ventana de logs.
        Args:
            icon: Ícono de la bandeja
            item: Ítem del menú seleccionado
        """
        self.log_viewer.show()

    def show_status(self) -> None:
        """Abre el navegador con la página de estado.
        Args:
            icon: Ícono de la bandeja
            item: Ítem del menú seleccionado
        """
        try:
            import webbrowser

            config = self.app.config
            host = config.get("server", {}).get("server_host", "0.0.0.0")
            if host == "0.0.0.0":
                host = "localhost"
            port = config.get("server", {}).get("server_port", 5050)
            webbrowser.open(f"http://{host}:{port}")
        except Exception as e:
            logger.error("Error al mostrar estado: %s", str(e))

    def stop(self) -> None:
        """Detiene la aplicación y limpia los recursos.
        Args:
            icon: Ícono de la bandeja
            item: Ítem del menú seleccionado
        """
        try:
            if self.icon:
                self.icon.stop()

            if self.log_viewer:
                self.log_viewer.destroy()

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
