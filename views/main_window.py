#!/usr/bin/env python
"""
Copyright © 2024, Iron Graterol
Licensed under the GNU Affero General Public License, version 3 or later.

Ventana principal de escritorio (ttkbootstrap): consola de logs, configuración
del servidor, configuración fiscal y envío de comandos directos a la impresora.
Reemplaza el editor de configuración web (config-editor.html) y el visor de
logs de Tkinter clásico (LogViewer en handy/tray_system.py).
"""

import json
import logging
import os
import queue
import sys
import webbrowser
from datetime import datetime
from typing import Any

import ttkbootstrap as tb
from jsonschema import ValidationError, validate
from ttkbootstrap import constants as tbc
from ttkbootstrap.dialogs import Messagebox

from handy.serial_scan import get_serial_scanner
from handy.tools import get_base_path
from server.config_loader import (
    CONFIG_SCHEMA,
    VALID_BARCODE_TYPES,
    VALID_FISCAL_PRINTERS,
    VALID_SERVER_MODES,
    ConfigManager,
    get_security_code,
)

logger = logging.getLogger(__name__)

# La plantilla fiscal no tiene jsonschema propio hoy (a diferencia de config.json).
# Se define aquí para que la GUI sea la única vía de edición y no permita guardar
# valores fuera de rango (p.ej. partner_address_lines fuera de 1-3).
FISCAL_TEMPLATE_SCHEMA = {
    "type": "object",
    "properties": {
        "fiscal": {
            "type": "object",
            "properties": {
                "model": {"type": "string"},
                "serial": {"type": "string"},
                "name_note": {"type": "string"},
            },
        },
        "format": {
            "type": "object",
            "properties": {
                "include_partner_address": {"type": "boolean"},
                "partner_address_lines": {"type": "integer", "minimum": 1, "maximum": 3},
                "include_partner_phone": {"type": "boolean"},
                "include_partner_email": {"type": "boolean"},
                "include_document_number": {"type": "boolean"},
                "include_document_reference": {"type": "boolean"},
                "include_document_date": {"type": "boolean"},
                "include_document_name": {"type": "boolean"},
                "include_document_cashier": {"type": "boolean"},
                "include_item_reference": {"type": "boolean"},
                "include_item_comment": {"type": "boolean"},
                "include_payment_subtotal": {"type": "boolean"},
                "include_delivery_comments": {"type": "boolean"},
                "include_delivery_barcode": {"type": "boolean"},
                "include_operator_mail": {"type": "boolean"},
                "include_exchange_rate": {"type": "boolean"},
            },
        },
    },
    "required": ["fiscal", "format"],
}

# (clave, etiqueta) — orden en que se dibujan los checkboxes de formato
FORMAT_FLAGS = [
    ("include_partner_address", "Incluir dirección del cliente"),
    ("include_partner_phone", "Incluir teléfono del cliente"),
    ("include_partner_email", "Incluir email del cliente"),
    ("include_document_number", "Incluir número de documento"),
    ("include_document_reference", "Incluir referencia de documento"),
    ("include_document_date", "Incluir fecha de documento"),
    ("include_document_name", "Incluir nombre de documento"),
    ("include_document_cashier", "Incluir cajero"),
    ("include_item_reference", "Incluir referencia de ítem"),
    ("include_item_comment", "Incluir comentario de ítem"),
    ("include_payment_subtotal", "Incluir subtotal de pago"),
    ("include_delivery_comments", "Incluir comentarios de entrega"),
    ("include_delivery_barcode", "Incluir código de barra de entrega"),
    ("include_operator_mail", "Incluir correo del operador"),
    ("include_exchange_rate", "Incluir tasa de cambio"),
]


def _template_path() -> str:
    return os.path.join(get_base_path(), "templates", "template_fiscal_printer.json")


def _load_template() -> dict[str, Any]:
    try:
        with open(_template_path(), encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.warning("No se pudo cargar template_fiscal_printer.json: %s", str(e))
        return {"fiscal": {}, "format": {}}


class MainWindow:
    """Ventana principal de la aplicación de escritorio (Consola, Servidor, Fiscal)."""

    def __init__(self, flask_app=None):
        """
        Args:
            flask_app: instancia Flask opcional. Cuando se provee (Fase 2), al guardar
                la configuración del servidor también se actualiza current_app.config
                para que el proceso en curso use los valores nuevos sin reiniciar.
        """
        self.flask_app = flask_app
        self._current_log_path = None

        # Cola thread-safe: pystray corre en su propio hilo y nunca debe tocar
        # widgets Tk directamente. request_show()/request_hide()/request_quit()
        # son las únicas formas seguras de pedirle algo a la ventana desde fuera
        # del hilo principal (ver handy/tray_system.py).
        self._ui_queue: queue.Queue[str] = queue.Queue()

        # Funciones "relock" registradas por _build_lock_overlay — hide() las
        # invoca para que las pestañas protegidas vuelvan a pedir el código
        # cada vez que la ventana se oculta (cerrar a bandeja o minimizar).
        # Sin esto, el código solo se pide una vez por ejecución del programa.
        self._relock_callbacks: list[Any] = []

        self.root = tb.Window(
            title="API Printer Spooler",
            themename="darkly",
            size=(950, 700),
            on_close=self._on_close,
        )
        self._set_window_icon()

        self.notebook = tb.Notebook(self.root)
        notebook = self.notebook
        notebook.pack(fill=tbc.BOTH, expand=tbc.YES, padx=10, pady=10)

        self.console_tab = tb.Frame(notebook)
        notebook.add(self.console_tab, text="Consola / Logs")

        # Configuración del Servidor y Configuración Fiscal quedan detrás de un
        # candado (código de seguridad) — ver _build_lock_overlay. El contenido
        # real se construye igual que antes, solo que no se empaqueta hasta
        # desbloquear la pestaña.
        server_container = tb.Frame(notebook)
        notebook.add(server_container, text="Configuración del Servidor")
        self.server_scroll = tb.ScrolledFrame(server_container, autohide=True)

        fiscal_container = tb.Frame(notebook)
        notebook.add(fiscal_container, text="Configuración Fiscal")
        self.fiscal_scroll = tb.ScrolledFrame(fiscal_container, autohide=True)

        self._build_console_tab()
        self._build_server_tab(self.server_scroll)
        self._build_fiscal_tab(self.fiscal_scroll)

        self._build_lock_overlay(server_container, "Configuración del Servidor", self.server_scroll.container)
        self._build_lock_overlay(fiscal_container, "Configuración Fiscal", self.fiscal_scroll.container)

        self._schedule_log_tail()
        self._poll_ui_queue()

        # Minimizar (icono de Windows, no el botón X) debe ocultar por completo,
        # igual que "Cerrar" — la app vive en la bandeja del sistema, nunca debe
        # dejar un ícono en la barra de tareas.
        self.root.bind("<Unmap>", self._on_minimize)

        # Arranca oculta: solo se muestra vía el ícono de la bandeja (TrayManager),
        # igual que el comportamiento previo de LogViewer.
        self.root.withdraw()

    def _set_window_icon(self) -> None:
        """Ícono de la ventana/exe (printer_fiscal.ico en Windows, .png en otros)."""
        try:
            if sys.platform.startswith("win"):
                icon_path = os.path.join(get_base_path(), "resources", "printer_fiscal.ico")
                if os.path.exists(icon_path):
                    self.root.iconbitmap(icon_path)
            else:
                icon_path = os.path.join(get_base_path(), "resources", "printer_fiscal.png")
                if os.path.exists(icon_path):
                    photo = tb.PhotoImage(file=icon_path)
                    self.root.iconphoto(True, photo)
                    self._icon_photo_ref = photo  # evita garbage collection de la imagen
        except Exception as e:
            logger.warning("No se pudo establecer el ícono de la ventana: %s", str(e))

    def _build_lock_overlay(self, parent, title: str, content) -> None:
        """Pantalla de candado que cubre `content` hasta que se ingrese el código
        de seguridad correcto. `content` no se empaqueta hasta desbloquear."""
        lock_frame = tb.Frame(parent)

        center = tb.Frame(lock_frame)
        center.place(relx=0.5, rely=0.35, anchor=tbc.CENTER)

        tb.Label(center, text=f"🔒 {title}", font=("Segoe UI", 14, "bold")).pack(pady=(0, 15))
        tb.Label(center, text="Esta sección requiere el código de seguridad configurado.").pack(pady=(0, 10))

        code_var = tb.StringVar()
        entry = tb.Entry(center, textvariable=code_var, show="*", width=24)
        entry.pack(pady=(0, 10))

        def unlock(event=None) -> None:  # pylint: disable=unused-argument
            if code_var.get() == get_security_code():
                lock_frame.pack_forget()
                content.pack(fill=tbc.BOTH, expand=tbc.YES)
                code_var.set("")
            else:
                Messagebox.show_error("Código de seguridad incorrecto.", title)
                code_var.set("")

        def relock() -> None:
            """Vuelve a cubrir `content` con el candado. Se llama cada vez que la
            ventana se oculta, para que el desbloqueo no sea válido "para siempre"
            durante toda la ejecución del programa."""
            content.pack_forget()
            lock_frame.pack(fill=tbc.BOTH, expand=tbc.YES)
            code_var.set("")

        entry.bind("<Return>", unlock)
        tb.Button(center, text="Desbloquear", command=unlock, bootstyle="success").pack()

        lock_frame.pack(fill=tbc.BOTH, expand=tbc.YES)
        self._relock_callbacks.append(relock)

    # ------------------------------------------------------------------
    # Ciclo de vida de la ventana
    # ------------------------------------------------------------------
    def show(self) -> None:
        """Muestra la ventana. Solo seguro de llamar desde el hilo de Tk
        (callbacks de widgets, o el propio _poll_ui_queue). Código externo
        (p.ej. TrayManager) debe usar request_show()."""
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def hide(self) -> None:
        """Oculta la ventana sin destruirla. Mismas reglas de hilo que show().
        Re-bloquea las pestañas protegidas: el código de seguridad solo vale
        mientras la ventana está a la vista, no "para siempre" durante toda la
        ejecución del programa."""
        for relock in self._relock_callbacks:
            relock()
        self.notebook.select(0)  # volver a "Consola / Logs" al ocultar
        self.root.withdraw()

    def _on_close(self) -> bool:
        """Callback del botón X (WM_DELETE_WINDOW). ttkbootstrap destruye la ventana
        después de este callback A MENOS que retorne exactamente False — por eso
        el return es obligatorio, no cosmético: sin él, cerrar la ventana mata
        toda la app (Flask incluido) en vez de solo ocultarla a la bandeja."""
        self.hide()
        return False

    def _on_minimize(self, event) -> None:
        """La app vive en la bandeja del sistema: minimizar (el botón _ de Windows,
        no el X) no debe dejar un ícono en la barra de tareas. Se intercepta el
        evento de iconificación y se oculta por completo (mismo efecto que Cerrar)."""
        if event.widget is self.root and self.root.state() == "iconic":
            self.root.withdraw()

    def request_show(self) -> None:
        """Thread-safe: encola una petición para mostrar la ventana. Usar desde
        el hilo de pystray (TrayManager) o desde el hilo de Flask."""
        self._ui_queue.put("show")

    def request_hide(self) -> None:
        """Thread-safe: encola una petición para ocultar la ventana."""
        self._ui_queue.put("hide")

    def request_quit(self) -> None:
        """Thread-safe: encola una petición para terminar el mainloop de Tk."""
        self._ui_queue.put("quit")

    def _poll_ui_queue(self) -> None:
        """Corre en el hilo de Tk vía root.after: procesa peticiones encoladas
        desde otros hilos sin tocar widgets fuera de este hilo."""
        try:
            while True:
                task = self._ui_queue.get_nowait()
                if task == "show":
                    self.show()
                elif task == "hide":
                    self.hide()
                elif task == "quit":
                    self.root.quit()
                    return
        except queue.Empty:
            pass
        self.root.after(100, self._poll_ui_queue)

    def mainloop(self) -> None:
        self.root.mainloop()

    # ------------------------------------------------------------------
    # Pestaña 1: Consola / Logs + Comandos Fiscales
    # ------------------------------------------------------------------
    def _build_console_tab(self) -> None:
        frame = self.console_tab

        status_bar = tb.Frame(frame)
        status_bar.pack(fill=tbc.X, padx=5, pady=(5, 0))

        self.status_label = tb.Label(status_bar, text="Modo: -- | Impresora: --")
        self.status_label.pack(side=tbc.LEFT, padx=5)

        tb.Button(status_bar, text="Actualizar", command=self._update_status_and_logs, bootstyle="info").pack(
            side=tbc.RIGHT, padx=5
        )
        tb.Button(status_bar, text="Copiar Logs", command=self._copy_logs, bootstyle="secondary").pack(
            side=tbc.RIGHT, padx=5
        )

        self.log_text = tb.ScrolledText(frame, height=20, autohide=True)
        self.log_text.pack(fill=tbc.BOTH, expand=tbc.YES, padx=5, pady=5)
        self.log_text.text.config(state="disabled")

        # Reportes Fiscales y Comandos Fiscales Directos viven en la pestaña
        # "Configuración Fiscal" (protegida por código de seguridad).
        dashboard_row = tb.Frame(frame)
        dashboard_row.pack(fill=tbc.X, padx=5, pady=5)
        tb.Button(dashboard_row, text="Abrir Dashboard Web", command=self._open_dashboard, bootstyle="info").pack(
            side=tbc.LEFT
        )

    def _open_dashboard(self) -> None:
        config = ConfigManager.get_config()
        server_cfg = config.get("server", {})
        host = server_cfg.get("server_host", "127.0.0.1")
        if host == "0.0.0.0":
            host = "localhost"
        port = server_cfg.get("server_port", 5051)
        webbrowser.open(f"http://{host}:{port}/")

    def _update_status_and_logs(self) -> None:
        self._update_status_label()
        self._tail_log(force=True)

    def _update_status_label(self) -> None:
        try:
            config = ConfigManager.get_config()
            server_mode = config.get("server", {}).get("server_mode", "--")
            fiscal = config.get("printers", {}).get("fiscal", {})
            fiscal_name = fiscal.get("fiscal_name", "--") if fiscal.get("fiscal_enabled") else "Deshabilitada"
            self.status_label.config(text=f"Modo: {server_mode} | Impresora: {fiscal_name}")
        except Exception as e:
            logger.error("Error actualizando estado en consola: %s", str(e))

    def _schedule_log_tail(self) -> None:
        self._update_status_label()
        self._tail_log()
        self.root.after(3000, self._schedule_log_tail)

    def _tail_log(self, force: bool = False) -> None:
        try:
            config = ConfigManager.get_config()
            log_dir = os.path.join(get_base_path(), "logs")
            log_file_name = config.get("logging", {}).get("log_file", "printer_spooler")
            current_date = datetime.now().strftime("%Y%m%d")
            log_path = os.path.join(log_dir, f"{log_file_name}-{current_date}.log")

            if not os.path.exists(log_path):
                return

            # Releer completo si se forzó o si rotó el archivo (cambio de fecha)
            if force or log_path != self._current_log_path:
                self._current_log_path = log_path
                with open(log_path, encoding="utf-8") as f:
                    content = f.read()
                self.log_text.text.config(state="normal")
                self.log_text.text.delete("1.0", tbc.END)
                self.log_text.text.insert(tbc.END, content)
                self.log_text.text.see(tbc.END)
                self.log_text.text.config(state="disabled")
        except Exception as e:
            logger.error("Error actualizando consola de logs: %s", str(e))

    def _copy_logs(self) -> None:
        try:
            content = self.log_text.text.get("1.0", tbc.END)
            self.root.clipboard_clear()
            self.root.clipboard_append(content)
        except Exception as e:
            logger.error("Error al copiar logs: %s", str(e))

    @staticmethod
    def _get_ready_fiscal_printer():
        """Obtiene la impresora fiscal activa y lista para operar, o lanza ValueError
        con un mensaje apto para mostrar directamente en un Messagebox."""
        # Import diferido: evita que main_window dependa de pyserial al solo abrir la GUI
        from server.handlers.printer_manager import PrinterManager

        config = ConfigManager.get_config()
        fiscal_config = config.get("printers", {}).get("fiscal", {})

        if not fiscal_config.get("fiscal_enabled", False):
            raise ValueError("La impresora fiscal no está habilitada en la configuración.")

        try:
            printer = PrinterManager.get_printer(fiscal_config.get("fiscal_name", "").strip().lower(), fiscal_config)
        except Exception as e:
            raise ValueError(f"No se pudo obtener la impresora fiscal: {e}") from e

        if not printer.check_status():
            raise ValueError("La impresora fiscal no está lista.")

        return printer

    @staticmethod
    def _confirm(message: str, title: str) -> bool:
        """Diálogo de confirmación con botones fijos en español (no depende del
        locale del sistema, a diferencia de los botones localizados por defecto)."""
        result = Messagebox.yesno(message, title, buttons=["No", "Sí"], localize=False)
        return result == "Sí"

    def _print_report(self, report_type: str) -> None:
        title = f"Reporte {report_type}"
        if not self._confirm(
            f"¿Está seguro que desea imprimir el {title}? Esta acción es irreversible sobre la impresora fiscal.",
            title,
        ):
            return
        try:
            printer = self._get_ready_fiscal_printer()
        except ValueError as e:
            Messagebox.show_error(str(e), title)
            return

        method_name = f"report_{report_type.lower()}"
        if not hasattr(printer, method_name):
            Messagebox.show_error(f"Esta impresora no soporta reportes {report_type}.", title)
            return

        try:
            result = getattr(printer, method_name)()
        except Exception as e:
            Messagebox.show_error(f"Error al imprimir {title.lower()}: {e}", title)
            return

        if result:
            Messagebox.show_info(f"{title} impreso correctamente.", title)
        else:
            Messagebox.show_error(f"Error al imprimir {title.lower()}.", title)

    def _send_commands(self) -> None:
        raw = self.commands_text.get("1.0", tbc.END).strip()
        if not raw:
            Messagebox.show_warning("El JSON de comandos está vacío.", "Comandos")
            return

        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as e:
            Messagebox.show_error(f"JSON inválido: {e}", "Comandos")
            return

        commands = payload.get("commands") if isinstance(payload, dict) else payload
        if not isinstance(commands, list) or not commands:
            Messagebox.show_error("'commands' debe ser una lista no vacía.", "Comandos")
            return

        if not self._confirm(
            f"¿Está seguro que desea enviar {len(commands)} comando(s) a la impresora fiscal? "
            "Esta acción es irreversible.",
            "Comandos",
        ):
            return

        try:
            printer = self._get_ready_fiscal_printer()
        except ValueError as e:
            Messagebox.show_error(str(e), "Comandos")
            return

        results = [{"command": cmd, "success": printer.send_command(cmd)} for cmd in commands]
        summary = "\n".join(f"{r['command']}: {'OK' if r['success'] else 'FALLÓ'}" for r in results)
        Messagebox.show_info(summary, "Resultado de comandos")

    # ------------------------------------------------------------------
    # Pestaña 2: Configuración del Servidor (config.json)
    # ------------------------------------------------------------------
    def _build_server_tab(self, parent) -> None:
        config = ConfigManager.get_config()
        server_cfg = config.get("server", {})
        proxy_cfg = config.get("proxy", {})
        fiscal_cfg = config.get("printers", {}).get("fiscal", {})
        logging_cfg = config.get("logging", {})
        security_cfg = config.get("security", {})

        self.sv: dict[str, tb.Variable] = {}

        # --- Servidor ---
        box = tb.LabelFrame(parent, text="Servidor", padding=10)
        box.pack(fill=tbc.X, padx=10, pady=10)

        self._add_entry(box, "Host", "server_host", server_cfg.get("server_host", "127.0.0.1"))
        self._add_entry(box, "Puerto", "server_port", server_cfg.get("server_port", 5051))
        self._add_combobox(box, "Modo", "server_mode", sorted(VALID_SERVER_MODES), server_cfg.get("server_mode", "SPOOLER"))
        self._add_checkbox(box, "Modo Debug", "server_debug", server_cfg.get("server_debug", False))
        self._add_checkbox(
            box, "Auto-detectar puerto serial al iniciar", "scan_serial_port", server_cfg.get("scan_serial_port", False)
        )
        self._add_checkbox(box, "Abrir navegador al iniciar", "auto_browser", server_cfg.get("auto_browser", False))

        # --- Orígenes permitidos (CORS) ---
        origins_box = tb.LabelFrame(parent, text="Orígenes Permitidos (CORS)", padding=10)
        origins_box.pack(fill=tbc.X, padx=10, pady=10)

        tb.Label(
            origins_box,
            text="Patrones regex de orígenes autorizados a llamar la API (Odoo, otros sistemas remotos).",
            wraplength=800,
        ).pack(anchor=tbc.W)

        self.origins_listbox = tb.Listbox(origins_box, height=6)
        self.origins_listbox.pack(fill=tbc.X, pady=5)
        for origin in server_cfg.get("allowed_origins", []):
            self.origins_listbox.insert(tbc.END, origin)

        origin_entry_frame = tb.Frame(origins_box)
        origin_entry_frame.pack(fill=tbc.X)
        self.new_origin_entry = tb.Entry(origin_entry_frame)
        self.new_origin_entry.pack(side=tbc.LEFT, fill=tbc.X, expand=tbc.YES, padx=(0, 5))
        tb.Button(
            origin_entry_frame, text="Agregar", command=self._add_origin, bootstyle="success", padding=(10, 6)
        ).pack(side=tbc.LEFT, padx=2)
        tb.Button(
            origin_entry_frame,
            text="Quitar seleccionado",
            command=self._remove_origin,
            bootstyle="danger",
            padding=(10, 6),
        ).pack(side=tbc.LEFT, padx=2)

        # --- Proxy ---
        proxy_box = tb.LabelFrame(parent, text="Proxy", padding=10)
        proxy_box.pack(fill=tbc.X, padx=10, pady=10)
        self._add_checkbox(proxy_box, "Habilitar Proxy", "proxy_enabled", proxy_cfg.get("proxy_enabled", False))
        self._add_entry(proxy_box, "URL Destino", "proxy_target", proxy_cfg.get("proxy_target", ""))

        # --- Impresora Fiscal ---
        fiscal_box = tb.LabelFrame(parent, text="Impresora Fiscal", padding=10)
        fiscal_box.pack(fill=tbc.X, padx=10, pady=10)
        self._add_checkbox(fiscal_box, "Habilitada", "fiscal_enabled", fiscal_cfg.get("fiscal_enabled", False))
        self._add_combobox(
            fiscal_box, "Modelo", "fiscal_name", sorted(VALID_FISCAL_PRINTERS), fiscal_cfg.get("fiscal_name", "TFHKA")
        )

        port_row = tb.Frame(fiscal_box)
        port_row.pack(fill=tbc.X, pady=3)
        tb.Label(port_row, text="Puerto", width=18).pack(side=tbc.LEFT)
        self.sv["fiscal_port"] = tb.StringVar(value=fiscal_cfg.get("fiscal_port", ""))
        self.fiscal_port_combo = tb.Combobox(port_row, textvariable=self.sv["fiscal_port"])
        self.fiscal_port_combo.pack(side=tbc.LEFT, fill=tbc.X, expand=tbc.YES, padx=(0, 5))
        tb.Button(port_row, text="Escanear Puertos", command=self._scan_serial_ports, bootstyle="info").pack(
            side=tbc.LEFT
        )

        self._add_entry(fiscal_box, "Baudrate", "fiscal_baudrate", fiscal_cfg.get("fiscal_baudrate", 9600))
        self._add_entry(fiscal_box, "Timeout (s)", "fiscal_timeout", fiscal_cfg.get("fiscal_timeout", 2))
        self._add_combobox(
            fiscal_box,
            "Tipo de Código de Barras",
            "fiscal_barcode_type",
            sorted(VALID_BARCODE_TYPES),
            fiscal_cfg.get("fiscal_barcode_type", "CODE128"),
        )

        # --- Logging ---
        logging_box = tb.LabelFrame(parent, text="Logging", padding=10)
        logging_box.pack(fill=tbc.X, padx=10, pady=10)
        self._add_checkbox(logging_box, "Mostrar logs en consola", "log_output", logging_cfg.get("log_output", True))
        self._add_entry(logging_box, "Nombre de archivo", "log_file", logging_cfg.get("log_file", "printer_spooler"))
        self._add_combobox(
            logging_box,
            "Nivel",
            "log_level",
            ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            logging_cfg.get("log_level", "INFO"),
        )
        self._add_entry(logging_box, "Formato", "log_format", logging_cfg.get("log_format", "%(asctime)s | %(levelname)s | %(message)s"))
        self._add_entry(logging_box, "Días de retención", "log_days", logging_cfg.get("log_days", 7))

        # --- Seguridad ---
        security_box = tb.LabelFrame(parent, text="Seguridad", padding=10)
        security_box.pack(fill=tbc.X, padx=10, pady=10)
        self._add_entry(security_box, "Código de seguridad", "security_code", security_cfg.get("security_code", ""), show="*")

        # --- Guardar ---
        save_row = tb.Frame(parent)
        save_row.pack(fill=tbc.X, padx=10, pady=15)
        tb.Button(save_row, text="Guardar Configuración del Servidor", command=self._save_server_config, bootstyle="success").pack(
            side=tbc.LEFT
        )

    def _scan_serial_ports(self) -> None:
        try:
            scanner = get_serial_scanner()
            ports = scanner.scan_ports()
            values = [p["port"] for p in ports]
            self.fiscal_port_combo["values"] = values
            if not values:
                Messagebox.show_info("No se encontraron puertos seriales disponibles.", "Escaneo de Puertos")
        except Exception as e:
            Messagebox.show_error(f"Error escaneando puertos: {e}", "Escaneo de Puertos")

    def _add_entry(self, parent, label: str, key: str, value: Any, show: str = None) -> None:
        row = tb.Frame(parent)
        row.pack(fill=tbc.X, pady=3)
        tb.Label(row, text=label, width=18).pack(side=tbc.LEFT)
        var = tb.StringVar(value=str(value) if value is not None else "")
        self.sv[key] = var
        entry_kwargs = {"show": show} if show else {}
        tb.Entry(row, textvariable=var, **entry_kwargs).pack(side=tbc.LEFT, fill=tbc.X, expand=tbc.YES)

    def _add_checkbox(self, parent, label: str, key: str, value: bool) -> None:
        var = tb.BooleanVar(value=bool(value))
        self.sv[key] = var
        tb.Checkbutton(parent, text=label, variable=var, bootstyle="round-toggle").pack(anchor=tbc.W, pady=3)

    def _add_combobox(self, parent, label: str, key: str, values: list[str], value: Any) -> None:
        row = tb.Frame(parent)
        row.pack(fill=tbc.X, pady=3)
        tb.Label(row, text=label, width=18).pack(side=tbc.LEFT)
        var = tb.StringVar(value=str(value) if value is not None else "")
        self.sv[key] = var
        tb.Combobox(row, textvariable=var, values=values, state="readonly").pack(
            side=tbc.LEFT, fill=tbc.X, expand=tbc.YES
        )

    def _add_origin(self) -> None:
        value = self.new_origin_entry.get().strip()
        if value:
            self.origins_listbox.insert(tbc.END, value)
            self.new_origin_entry.delete(0, tbc.END)

    def _remove_origin(self) -> None:
        selection = self.origins_listbox.curselection()
        for index in reversed(selection):
            self.origins_listbox.delete(index)

    def _save_server_config(self) -> None:
        try:
            new_config = {
                "server": {
                    "allowed_origins": list(self.origins_listbox.get(0, tbc.END)),
                    "auto_browser": self.sv["auto_browser"].get(),
                    "scan_serial_port": self.sv["scan_serial_port"].get(),
                    "server_debug": self.sv["server_debug"].get(),
                    "server_host": self.sv["server_host"].get(),
                    "server_mode": self.sv["server_mode"].get(),
                    "server_port": int(self.sv["server_port"].get()),
                },
                "proxy": {
                    "proxy_enabled": self.sv["proxy_enabled"].get(),
                    "proxy_target": self.sv["proxy_target"].get(),
                },
                "printers": {
                    "fiscal": {
                        "fiscal_enabled": self.sv["fiscal_enabled"].get(),
                        "fiscal_name": self.sv["fiscal_name"].get(),
                        "fiscal_port": self.sv["fiscal_port"].get(),
                        "fiscal_baudrate": int(self.sv["fiscal_baudrate"].get()),
                        "fiscal_timeout": int(self.sv["fiscal_timeout"].get()),
                        "fiscal_barcode_type": self.sv["fiscal_barcode_type"].get(),
                    }
                },
                "logging": {
                    "log_output": self.sv["log_output"].get(),
                    "log_file": self.sv["log_file"].get(),
                    "log_level": self.sv["log_level"].get(),
                    "log_format": self.sv["log_format"].get(),
                    "log_days": int(self.sv["log_days"].get()),
                },
                "security": {
                    "security_code": self.sv["security_code"].get(),
                },
            }
        except (ValueError, KeyError) as e:
            Messagebox.show_error(f"Valor inválido en el formulario: {e}", "Configuración del Servidor")
            return

        try:
            validate(new_config, CONFIG_SCHEMA)
        except ValidationError as e:
            Messagebox.show_error(f"Configuración inválida: {e.message}", "Configuración del Servidor")
            return

        try:
            ConfigManager.save_config(new_config)
            ConfigManager.reload_config()
            if self.flask_app is not None:
                self.flask_app.config.update(new_config)
        except Exception as e:
            Messagebox.show_error(f"No se pudo guardar la configuración: {e}", "Configuración del Servidor")
            return

        Messagebox.show_info("Configuración del servidor guardada correctamente.", "Configuración del Servidor")

    # ------------------------------------------------------------------
    # Pestaña 3: Configuración Fiscal (template_fiscal_printer.json)
    # ------------------------------------------------------------------
    def _build_fiscal_tab(self, parent) -> None:
        template = _load_template()
        fiscal = template.get("fiscal", {})
        fmt = template.get("format", {})

        self.fv: dict[str, tb.Variable] = {}

        info_box = tb.LabelFrame(parent, text="Datos de la Impresora", padding=10)
        info_box.pack(fill=tbc.X, padx=10, pady=10)
        self._add_fiscal_entry(info_box, "Modelo", "model", fiscal.get("model", ""))
        self._add_fiscal_entry(info_box, "Serial", "serial", fiscal.get("serial", ""))
        self._add_fiscal_entry(info_box, "Nombre de Nota", "name_note", fiscal.get("name_note", ""))

        format_box = tb.LabelFrame(parent, text="Formato del Documento", padding=10)
        format_box.pack(fill=tbc.X, padx=10, pady=10)

        lines_row = tb.Frame(format_box)
        lines_row.pack(fill=tbc.X, pady=(0, 10))
        tb.Label(lines_row, text="Líneas de dirección del cliente (1-3)").pack(side=tbc.LEFT)
        self.fv["partner_address_lines"] = tb.IntVar(value=int(fmt.get("partner_address_lines", 1)))
        spin = tb.Spinbox(
            lines_row, from_=1, to=3, textvariable=self.fv["partner_address_lines"], width=5,
            command=self._update_address_lines_note,
        )
        spin.pack(side=tbc.LEFT, padx=10)
        self.address_lines_note = tb.Label(format_box, bootstyle="warning", wraplength=800)
        self.address_lines_note.pack(anchor=tbc.W, pady=(0, 10))
        self._update_address_lines_note()

        grid = tb.Frame(format_box)
        grid.pack(fill=tbc.X)
        for index, (key, label) in enumerate(FORMAT_FLAGS):
            var = tb.BooleanVar(value=bool(fmt.get(key, False)))
            self.fv[key] = var
            row, col = divmod(index, 2)
            tb.Checkbutton(grid, text=label, variable=var, bootstyle="round-toggle").grid(
                row=row, column=col, sticky=tbc.W, padx=10, pady=4
            )

        # --- Reportes Fiscales y Comandos Fiscales Directos ---
        # Viven aquí (no en Consola) porque esta pestaña ya está protegida por
        # código de seguridad y estas acciones son sensibles/irreversibles.
        reports_frame = tb.LabelFrame(parent, text="Reportes Fiscales", bootstyle="secondary", padding=10)
        reports_frame.pack(fill=tbc.X, padx=10, pady=10)
        reports_btn_row = tb.Frame(reports_frame)
        reports_btn_row.pack(fill=tbc.X)
        tb.Button(
            reports_btn_row, text="Imprimir Reporte X", command=lambda: self._print_report("X"), bootstyle="primary"
        ).pack(side=tbc.LEFT, padx=(0, 5))
        tb.Button(
            reports_btn_row, text="Imprimir Reporte Z", command=lambda: self._print_report("Z"), bootstyle="primary"
        ).pack(side=tbc.LEFT)

        cmd_frame = tb.LabelFrame(parent, text="Comandos Fiscales Directos", bootstyle="secondary", padding=10)
        cmd_frame.pack(fill=tbc.X, padx=10, pady=10)

        tb.Label(
            cmd_frame,
            text='Pega un JSON con la forma {"commands": ["CMD1", "CMD2"]} y presiona Enviar. '
            "Ya no se lee handy/commands.json automáticamente.",
            wraplength=800,
        ).pack(anchor=tbc.W, pady=(0, 5))

        self.commands_text = tb.Text(cmd_frame, height=14)
        self.commands_text.pack(fill=tbc.X, pady=5)
        self.commands_text.insert("1.0", '{\n    "commands": [\n        "S1",\n        "I0X"\n    ]\n}')

        cmd_btn_frame = tb.Frame(cmd_frame)
        cmd_btn_frame.pack(fill=tbc.X, pady=(0, 5))
        tb.Button(cmd_btn_frame, text="Enviar Comandos", command=self._send_commands, bootstyle="warning").pack(
            side=tbc.LEFT
        )

        save_row = tb.Frame(parent)
        save_row.pack(fill=tbc.X, padx=10, pady=15)
        tb.Button(save_row, text="Guardar Plantilla Fiscal", command=self._save_fiscal_template, bootstyle="success").pack(
            side=tbc.LEFT
        )

    def _add_fiscal_entry(self, parent, label: str, key: str, value: Any) -> None:
        row = tb.Frame(parent)
        row.pack(fill=tbc.X, pady=3)
        tb.Label(row, text=label, width=18).pack(side=tbc.LEFT)
        var = tb.StringVar(value=str(value) if value is not None else "")
        self.fv[key] = var
        tb.Entry(row, textvariable=var).pack(side=tbc.LEFT, fill=tbc.X, expand=tbc.YES)

    def _update_address_lines_note(self) -> None:
        try:
            lines = self.fv["partner_address_lines"].get()
        except Exception:
            lines = 1
        remaining = 9 - lines  # TFHKA usa índices i00-i09; más líneas de dirección dejan menos espacio
        self.address_lines_note.config(
            text=(
                f"Con {lines} línea(s) de dirección activa(s), quedan aproximadamente {remaining} índices "
                "(i00-i09) disponibles para teléfono, email y metadatos del documento en impresoras TFHKA."
            )
        )

    def _save_fiscal_template(self) -> None:
        new_template = {
            "fiscal": {
                "model": self.fv["model"].get(),
                "serial": self.fv["serial"].get(),
                "name_note": self.fv["name_note"].get(),
            },
            "format": {
                "partner_address_lines": self.fv["partner_address_lines"].get(),
                **{key: self.fv[key].get() for key, _ in FORMAT_FLAGS if key != "partner_address_lines"},
            },
        }

        try:
            validate(new_template, FISCAL_TEMPLATE_SCHEMA)
        except ValidationError as e:
            Messagebox.show_error(f"Plantilla inválida: {e.message}", "Configuración Fiscal")
            return

        try:
            with open(_template_path(), "w", encoding="utf-8") as f:
                json.dump(new_template, f, indent=4, ensure_ascii=False)
        except Exception as e:
            Messagebox.show_error(f"No se pudo guardar la plantilla fiscal: {e}", "Configuración Fiscal")
            return

        # Fuerza a recrear la instancia de impresora para que recoja la plantilla nueva
        try:
            from server.handlers.printer_manager import PrinterManager

            fiscal_name = ConfigManager.get_config().get("printers", {}).get("fiscal", {}).get("fiscal_name", "")
            PrinterManager.remove_printer(fiscal_name.strip().lower())
        except Exception as e:
            logger.warning("No se pudo invalidar la instancia de impresora tras guardar plantilla: %s", str(e))

        Messagebox.show_info("Plantilla fiscal guardada correctamente.", "Configuración Fiscal")


if __name__ == "__main__":
    # Punto de entrada para probar la GUI de forma aislada, sin arrancar Flask
    # ni el system tray. Uso: uv run python -m views.main_window
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
    window = MainWindow()
    window.mainloop()
