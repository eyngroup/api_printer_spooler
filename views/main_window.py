#!/usr/bin/env python
"""
Copyright © 2024, Iron Graterol
Licensed under the GNU Affero General Public License, version 3 or later.

Ventana principal de escritorio (ttkbootstrap): consola de logs, configuración
del servidor, impresoras (fiscal, ticket, matriz) y envío de comandos/reportes.
"""

import json
import logging
import os
import queue
import sys
import threading
import webbrowser
from datetime import datetime
from typing import Any

from tkinter import filedialog

import ttkbootstrap as tb
from jsonschema import ValidationError, validate
from ttkbootstrap import constants as tbc
from ttkbootstrap.dialogs import Messagebox

from handy.serial_scan import get_serial_scanner
from handy.tools import get_base_path
from handy.update_apply import launch_apply
from handy.updater import UpdateError, UpdateInfo, check_latest, download_and_stage, is_supported
from handy.version import __version__
from server.handlers import monitor_push
from server.handlers.job_store import backup_db, has_processing_jobs, restore_db
from server.config_loader import (
    CONFIG_SCHEMA,
    VALID_BARCODE_TYPES,
    VALID_FISCAL_PRINTERS,
    VALID_MATRIX_PAPER_TYPES,
    VALID_SERVER_MODES,
    ConfigManager,
    PAYMENT_CODES,
    _load_default_payment_labels,
    get_monitor_push_config,
    get_payment_labels,
    get_security_code,
)

logger = logging.getLogger(__name__)

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
                "include_item_discount": {"type": "boolean"},
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
    ("include_item_discount", "Incluir línea de descuento/recargo del ítem (PNP)"),
    ("include_payment_subtotal", "Incluir subtotal de pago"),
    ("include_delivery_comments", "Incluir comentarios de entrega"),
    ("include_delivery_barcode", "Incluir código de barra de entrega"),
    ("include_operator_mail", "Incluir correo del operador"),
    ("include_exchange_rate", "Incluir tasa de cambio"),
]

TICKET_FORMAT_FLAGS = [
    ("show_customer_address", "Mostrar dirección del cliente"),
    ("show_customer_phone", "Mostrar teléfono del cliente"),
    ("show_customer_email", "Mostrar email del cliente"),
    ("show_document_number", "Mostrar número de documento"),
    ("show_document_reference", "Mostrar referencia del documento"),
    ("show_document_date", "Mostrar fecha del documento"),
    ("show_document_name", "Mostrar nombre del documento"),
    ("show_document_cashier", "Mostrar cajero"),
    ("show_items_header", "Mostrar encabezado de ítems"),
    ("combine_item_ref", "Combinar referencia de ítem"),
    ("show_subtotal", "Mostrar subtotal"),
    ("show_delivery_comments", "Mostrar comentarios de entrega"),
]

MATRIX_FORMAT_FLAGS = [
    ("show_items_comment", "Mostrar comentarios de ítems"),
    ("show_payments", "Mostrar detalle de pagos"),
    ("show_delivery_comment", "Mostrar comentarios de entrega"),
]


def _fiscal_template_path() -> str:
    return os.path.join(get_base_path(), "templates", "template_fiscal_printer.json")


def _ticket_template_path() -> str:
    return os.path.join(get_base_path(), "templates", "template_ticket_simple.json")


def _matrix_template_path() -> str:
    return os.path.join(get_base_path(), "templates", "template_matriz_carta.json")


def _load_json_file(path: str) -> dict[str, Any]:
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.warning("No se pudo cargar %s: %s", path, str(e))
        return {}


def _save_json_file(path: str, data: dict[str, Any]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


class MainWindow:
    """Ventana principal de la aplicación de escritorio (Consola, Servidor, Impresoras, Comandos)."""

    def __init__(self, flask_app=None):
        self.flask_app = flask_app
        self._current_log_path = None
        self._ui_queue: queue.Queue[str] = queue.Queue()
        self._relock_callbacks: list[Any] = []

        self.root = tb.Window(
            title="API Printer Spooler",
            themename="darkly",
            size=(980, 720),
            on_close=self._on_close,
        )
        self._set_window_icon()

        # Barra superior con título y alternador de tema
        top_bar = tb.Frame(self.root)
        top_bar.pack(fill=tbc.X, padx=10, pady=(8, 2))

        tb.Label(top_bar, text="API Printer Spooler", font=("Segoe UI", 12, "bold")).pack(side=tbc.LEFT)

        self._is_dark_theme = True
        self.theme_btn = tb.Button(
            top_bar,
            text="☀️ Tema Claro",
            command=self._toggle_theme,
            bootstyle="secondary-outline",
            padding=(8, 3),
        )
        self.theme_btn.pack(side=tbc.RIGHT)

        self.notebook = tb.Notebook(self.root)
        notebook = self.notebook
        notebook.pack(fill=tbc.BOTH, expand=tbc.YES, padx=10, pady=5)

        # 1. Consola / Logs
        self.console_tab = tb.Frame(notebook)
        notebook.add(self.console_tab, text="Consola / Logs")

        # 2. Configuración del Servidor
        server_container = tb.Frame(notebook)
        notebook.add(server_container, text="Configuración del Servidor")
        self.server_scroll = tb.ScrolledFrame(server_container, autohide=True)

        # 3. Impresora Fiscal
        fiscal_container = tb.Frame(notebook)
        notebook.add(fiscal_container, text="Impresora Fiscal")
        self.fiscal_scroll = tb.ScrolledFrame(fiscal_container, autohide=True)

        # 4. Impresora Ticket
        ticket_container = tb.Frame(notebook)
        notebook.add(ticket_container, text="Impresora Ticket")
        self.ticket_scroll = tb.ScrolledFrame(ticket_container, autohide=True)

        # 5. Impresora Matrix
        matrix_container = tb.Frame(notebook)
        notebook.add(matrix_container, text="Impresora Matrix")
        self.matrix_scroll = tb.ScrolledFrame(matrix_container, autohide=True)

        # 6. Comandos
        commands_container = tb.Frame(notebook)
        notebook.add(commands_container, text="Comandos")
        self.commands_scroll = tb.ScrolledFrame(commands_container, autohide=True)

        # Construcción de pestañas
        self._build_console_tab()
        self._build_server_tab(self.server_scroll)
        self._build_fiscal_tab(self.fiscal_scroll)
        self._build_ticket_tab(self.ticket_scroll)
        self._build_matrix_tab(self.matrix_scroll)
        self._build_commands_tab(self.commands_scroll)

        # Bloqueo de seguridad en pestañas de configuración
        self._build_lock_overlay(server_container, "Configuración del Servidor", self.server_scroll.container)
        self._build_lock_overlay(fiscal_container, "Impresora Fiscal", self.fiscal_scroll.container)
        self._build_lock_overlay(ticket_container, "Impresora Ticket", self.ticket_scroll.container)
        self._build_lock_overlay(matrix_container, "Impresora Matrix", self.matrix_scroll.container)
        self._build_lock_overlay(commands_container, "Comandos", self.commands_scroll.container)

        self._schedule_log_tail()
        self._poll_ui_queue()

        self.root.bind("<Unmap>", self._on_minimize)
        self.root.withdraw()

    def _set_window_icon(self) -> None:
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
                    self._icon_photo_ref = photo
        except Exception as e:
            logger.warning("No se pudo establecer el ícono de la ventana: %s", str(e))

    def _toggle_theme(self) -> None:
        """Alterna entre tema oscuro (darkly) y claro (bootstrap-light)."""
        if self._is_dark_theme:
            self.root.style.theme_use("bootstrap-light")
            self.theme_btn.config(text="🌙 Tema Oscuro", bootstyle="primary-outline")
            self._is_dark_theme = False
        else:
            self.root.style.theme_use("darkly")
            self.theme_btn.config(text="☀️ Tema Claro", bootstyle="secondary-outline")
            self._is_dark_theme = True

    def _build_lock_overlay(self, parent, title: str, content) -> None:
        lock_frame = tb.Frame(parent)

        center = tb.Frame(lock_frame)
        center.place(relx=0.5, rely=0.35, anchor=tbc.CENTER)

        tb.Label(center, text=f"🔒 {title}", font=("Segoe UI", 14, "bold")).pack(pady=(0, 15))
        tb.Label(center, text="Esta sección requiere el código de seguridad configurado.").pack(pady=(0, 10))

        code_var = tb.StringVar()
        entry = tb.Entry(center, textvariable=code_var, show="*", width=24)
        entry.pack(pady=(0, 10))

        def unlock(event=None) -> None:
            if code_var.get() == get_security_code():
                lock_frame.pack_forget()
                content.pack(fill=tbc.BOTH, expand=tbc.YES)
                code_var.set("")
            else:
                Messagebox.show_error("Código de seguridad incorrecto.", title)
                code_var.set("")

        entry.bind("<Return>", unlock)
        tb.Button(center, text="Desbloquear", command=unlock, bootstyle="primary").pack()

        def relock() -> None:
            content.pack_forget()
            lock_frame.pack(fill=tbc.BOTH, expand=tbc.YES)
            code_var.set("")

        self._relock_callbacks.append(relock)
        relock()

    # ------------------------------------------------------------------
    # Ciclo de vida y cola de eventos UI (thread-safe)
    # ------------------------------------------------------------------
    def request_show(self) -> None:
        self._ui_queue.put("show")

    def request_hide(self) -> None:
        self._ui_queue.put("hide")

    def request_quit(self) -> None:
        self._ui_queue.put("quit")

    def show(self) -> None:
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def hide(self) -> None:
        self.root.withdraw()
        for callback in self._relock_callbacks:
            try:
                callback()
            except Exception as e:
                logger.debug("Error en callback de relock: %s", str(e))

    def mainloop(self) -> None:
        self.root.mainloop()

    def _poll_ui_queue(self) -> None:
        try:
            while True:
                msg = self._ui_queue.get_nowait()
                if msg == "show":
                    self.show()
                elif msg == "hide":
                    self.hide()
                elif msg == "quit":
                    self._quit_application()
                    return
        except queue.Empty:
            pass
        self.root.after(100, self._poll_ui_queue)

    def _on_close(self) -> bool:
        """
        Botón cerrar (X) de la ventana: oculta a la bandeja en lugar de salir.
        ttkbootstrap destruye la ventana tras este callback salvo que devuelva False; destruirla terminaba
        el mainloop y cerraba la aplicación completa. Solo "Salir" de la bandeja cierra la aplicación.
        """
        self.hide()
        return False

    def _on_minimize(self, event) -> None:
        if event.widget == self.root and self.root.state() == "iconic":
            self.hide()

    def _quit_application(self) -> None:
        try:
            self.root.destroy()
        except Exception as e:
            logger.debug("Error destruyendo root: %s", str(e))
        os._exit(0)

    # ------------------------------------------------------------------
    # 1. Pestaña: Consola / Logs
    # ------------------------------------------------------------------
    def _build_console_tab(self) -> None:
        controls = tb.Frame(self.console_tab)
        controls.pack(fill=tbc.X, padx=5, pady=5)

        tb.Label(controls, text="Nivel de log:").pack(side=tbc.LEFT, padx=(0, 5))
        self.log_level_filter = tb.StringVar(value="TODOS")
        level_combo = tb.Combobox(
            controls,
            textvariable=self.log_level_filter,
            values=["TODOS", "DEBUG", "INFO", "WARNING", "ERROR"],
            state="readonly",
            width=10,
        )
        level_combo.pack(side=tbc.LEFT, padx=(0, 10))
        level_combo.bind("<<ComboboxSelected>>", lambda e: self._filter_logs())

        self.auto_scroll = tb.BooleanVar(value=True)
        tb.Checkbutton(
            controls, text="Auto-scroll", variable=self.auto_scroll, bootstyle="round-toggle"
        ).pack(side=tbc.LEFT, padx=5)

        tb.Button(controls, text="Limpiar vista", command=self._clear_console, bootstyle="secondary").pack(
            side=tbc.RIGHT, padx=5
        )
        tb.Button(controls, text="Copiar logs", command=self._copy_logs, bootstyle="info").pack(
            side=tbc.RIGHT, padx=5
        )

        self.console_text = tb.Text(self.console_tab, wrap="none", font=("Consolas", 9))
        self.console_text.pack(fill=tbc.BOTH, expand=tbc.YES, padx=5, pady=(0, 5))

        self.console_text.tag_config("DEBUG", foreground="#6c757d")
        self.console_text.tag_config("INFO", foreground="#20c997")
        self.console_text.tag_config("WARNING", foreground="#ffc107")
        self.console_text.tag_config("ERROR", foreground="#dc3545")
        self.console_text.tag_config("DEFAULT", foreground="#f8f9fa")

    def _schedule_log_tail(self) -> None:
        self._tail_current_log()
        self.root.after(1000, self._schedule_log_tail)

    def _tail_current_log(self) -> None:
        config = ConfigManager.get_config()
        log_cfg = config.get("logging", {})
        log_file_base = log_cfg.get("log_file", "printer_service")
        today = datetime.now().strftime("%Y%m%d")
        log_path = os.path.join(get_base_path(), "logs", f"{log_file_base}-{today}.log")

        if not os.path.exists(log_path):
            return

        if self._current_log_path != log_path:
            self._current_log_path = log_path
            self._log_file_pos = 0
            self.console_text.delete("1.0", tbc.END)

        try:
            with open(log_path, "r", encoding="utf-8", errors="replace") as f:
                f.seek(self._log_file_pos)
                new_chunk = f.read()
                self._log_file_pos = f.tell()

            if new_chunk:
                for line in new_chunk.splitlines(keepends=True):
                    self._append_log_line(line)
                if self.auto_scroll.get():
                    self.console_text.see(tbc.END)
        except Exception as e:
            logger.debug("Error leyendo log: %s", str(e))

    def _append_log_line(self, line: str) -> None:
        filter_level = self.log_level_filter.get()
        tag = "DEFAULT"
        for level in ("ERROR", "WARNING", "INFO", "DEBUG"):
            if f"| {level} |" in line or f" {level} " in line:
                tag = level
                break

        if filter_level != "TODOS" and tag != filter_level and tag != "DEFAULT":
            return

        clean_line = line.replace('"', "").rstrip("\r\n") + "\n"
        self.console_text.insert(tbc.END, clean_line, tag)

    def _filter_logs(self) -> None:
        self.console_text.delete("1.0", tbc.END)
        self._log_file_pos = 0
        self._tail_current_log()

    def _clear_console(self) -> None:
        self.console_text.delete("1.0", tbc.END)

    def _copy_logs(self) -> None:
        try:
            content = self.console_text.get("1.0", tbc.END)
            self.root.clipboard_clear()
            self.root.clipboard_append(content)
            Messagebox.show_info("Logs copiados al portapapeles.", "Consola")
        except Exception as e:
            logger.error("Error al copiar logs: %s", str(e))

    # ------------------------------------------------------------------
    # 2. Pestaña: Configuración del Servidor (config.json)
    # ------------------------------------------------------------------
    def _build_server_tab(self, parent) -> None:
        config = ConfigManager.get_config()
        server_cfg = config.get("server", {})
        proxy_cfg = config.get("proxy", {})
        logging_cfg = config.get("logging", {})
        security_cfg = config.get("security", {})

        self.sv: dict[str, tb.Variable] = {}

        # --- Servidor ---
        box = tb.LabelFrame(parent, text="Servidor", padding=10)
        box.pack(fill=tbc.X, padx=10, pady=10)
        self._add_entry(self.sv, box, "Host", "server_host", server_cfg.get("server_host", "127.0.0.1"))
        self._add_entry(self.sv, box, "Puerto", "server_port", server_cfg.get("server_port", 5051))
        self._add_combobox(self.sv, box, "Modo", "server_mode", sorted(VALID_SERVER_MODES), server_cfg.get("server_mode", "SPOOLER"))
        self._add_checkbox(self.sv, box, "Modo Debug", "server_debug", server_cfg.get("server_debug", False))
        self._add_checkbox(
            self.sv, box, "Auto-detectar puerto serial al iniciar", "scan_serial_port", server_cfg.get("scan_serial_port", False)
        )
        self._add_checkbox(self.sv, box, "Abrir navegador al iniciar", "auto_browser", server_cfg.get("auto_browser", False))

        # --- CORS ---
        origins_box = tb.LabelFrame(parent, text="Orígenes Permitidos (CORS)", padding=10)
        origins_box.pack(fill=tbc.X, padx=10, pady=10)
        tb.Label(
            origins_box,
            text="Patrones regex de orígenes autorizados a llamar la API (Odoo, sistemas remotos).",
            wraplength=800,
        ).pack(anchor=tbc.W)

        self.origins_listbox = tb.Listbox(origins_box, height=5)
        self.origins_listbox.pack(fill=tbc.X, pady=5)
        for origin in server_cfg.get("allowed_origins", []):
            self.origins_listbox.insert(tbc.END, origin)

        origin_entry_frame = tb.Frame(origins_box)
        origin_entry_frame.pack(fill=tbc.X)
        self.new_origin_entry = tb.Entry(origin_entry_frame)
        self.new_origin_entry.pack(side=tbc.LEFT, fill=tbc.X, expand=tbc.YES, padx=(0, 5))
        tb.Button(origin_entry_frame, text="Agregar", command=self._add_origin, bootstyle="success").pack(
            side=tbc.LEFT, padx=2
        )
        tb.Button(origin_entry_frame, text="Quitar", command=self._remove_origin, bootstyle="danger").pack(
            side=tbc.LEFT, padx=2
        )

        # --- Proxy ---
        proxy_box = tb.LabelFrame(parent, text="Proxy", padding=10)
        proxy_box.pack(fill=tbc.X, padx=10, pady=10)
        self._add_checkbox(self.sv, proxy_box, "Habilitar Proxy", "proxy_enabled", proxy_cfg.get("proxy_enabled", False))
        self._add_entry(self.sv, proxy_box, "URL Destino", "proxy_target", proxy_cfg.get("proxy_target", ""))

        # --- Logging ---
        logging_box = tb.LabelFrame(parent, text="Logging", padding=10)
        logging_box.pack(fill=tbc.X, padx=10, pady=10)
        self._add_checkbox(self.sv, logging_box, "Mostrar logs en consola", "log_output", logging_cfg.get("log_output", True))
        self._add_entry(self.sv, logging_box, "Nombre de archivo", "log_file", logging_cfg.get("log_file", "printer_spooler"))
        self._add_combobox(
            self.sv,
            logging_box,
            "Nivel",
            "log_level",
            ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            logging_cfg.get("log_level", "INFO"),
        )
        self._add_entry(self.sv, logging_box, "Formato", "log_format", logging_cfg.get("log_format", "%(asctime)s | %(levelname)s | %(message)s"))
        self._add_entry(self.sv, logging_box, "Días de retención", "log_days", logging_cfg.get("log_days", 7))

        # --- Seguridad ---
        security_box = tb.LabelFrame(parent, text="Seguridad", padding=10)
        security_box.pack(fill=tbc.X, padx=10, pady=10)
        self._add_entry(self.sv, security_box, "Código de seguridad", "security_code", security_cfg.get("security_code", ""), show="*")

        # --- Monitor fiscal en Odoo (envío de lecturas) ---
        self._build_monitor_push_box(parent, config)

        # --- Actualizaciones (releases de GitHub) ---
        self._build_update_box(parent)

        # --- Base de Datos SQLite y Respaldos ---
        db_box = tb.LabelFrame(parent, text="Base de Datos SQLite y Respaldos", padding=10)
        db_box.pack(fill=tbc.X, padx=10, pady=10)
        tb.Label(
            db_box,
            text="Control de idempotencia y estado de trabajos de impresión (data/print_jobs.db).\n"
                 "Los respaldos se generan de forma atómica y en caliente en la carpeta backups/.",
            wraplength=800,
        ).pack(anchor=tbc.W, pady=(0, 10))

        db_btn_row = tb.Frame(db_box)
        db_btn_row.pack(fill=tbc.X)
        tb.Button(
            db_btn_row,
            text="Crear Respaldo de BD",
            command=self._on_backup_db,
            bootstyle="info-outline",
        ).pack(side=tbc.LEFT, padx=(0, 10))
        tb.Button(
            db_btn_row,
            text="Restaurar Respaldo...",
            command=self._on_restore_db,
            bootstyle="warning-outline",
        ).pack(side=tbc.LEFT)

        # --- Guardar ---
        save_row = tb.Frame(parent)
        save_row.pack(fill=tbc.X, padx=10, pady=15)
        tb.Button(
            save_row,
            text="Guardar Configuración del Servidor",
            command=self._save_server_config,
            bootstyle="success",
        ).pack(side=tbc.LEFT)

    def _build_monitor_push_box(self, parent, config: dict[str, Any]) -> None:
        """
        Sección de la pestaña Servidor para el envío de lecturas del monitor fiscal a Odoo: activación, URL,
        token (oculto), intervalo, sucursal, estado del último envío y botón "Enviar ahora".
        La pestaña ya está protegida por el código de seguridad.
        Args:
            parent: Contenedor de la pestaña
            config: Configuración vigente
        """
        push_cfg = get_monitor_push_config(config)
        box = tb.LabelFrame(parent, text="Monitor fiscal en Odoo", padding=10)
        box.pack(fill=tbc.X, padx=10, pady=10)
        tb.Label(
            box,
            text="Envía a Odoo las lecturas del monitor fiscal (cada intervalo y justo antes y después de cada Z). "
            "Solo impresoras TFHKA en modo SPOOLER. El token lo genera Odoo en el diario. "
            "URL: https://<dominio-odoo>/fiscal_printer/monitor/push",
            wraplength=800,
        ).pack(anchor=tbc.W, pady=(0, 6))
        self._add_checkbox(self.sv, box, "Habilitar envío a Odoo", "push_enabled", push_cfg["enabled"])
        self._add_entry(self.sv, box, "URL de Odoo", "push_url", push_cfg["url"])
        self._add_entry(self.sv, box, "Token", "push_token", push_cfg["token"], show="*")
        self._add_entry(self.sv, box, "Intervalo (minutos, mínimo 15)", "push_interval_minutes", push_cfg["interval_minutes"])
        self._add_entry(self.sv, box, "Código de sucursal", "push_branch_code", push_cfg["branch_code"])

        status_row = tb.Frame(box)
        status_row.pack(fill=tbc.X, pady=(8, 0))
        self.push_status_label = tb.Label(status_row, text=self._monitor_push_status_text(), wraplength=600)
        self.push_status_label.pack(side=tbc.LEFT, fill=tbc.X, expand=tbc.YES)
        self.push_send_button = tb.Button(
            status_row, text="Enviar ahora", command=self._on_monitor_push_send, bootstyle="info-outline"
        )
        self.push_send_button.pack(side=tbc.RIGHT, padx=(5, 0))
        tb.Button(
            status_row, text="Actualizar estado", command=self._refresh_monitor_push_status, bootstyle="secondary-outline"
        ).pack(side=tbc.RIGHT)

    # Primera consulta de versiones tras el arranque y luego una vez al día (milisegundos para Tk.after)
    UPDATE_FIRST_CHECK_MS = 15_000
    UPDATE_CHECK_EVERY_MS = 24 * 60 * 60 * 1000

    def _build_update_box(self, parent) -> None:
        """
        Sección de actualizaciones: versión instalada, última publicada en GitHub y botones "Buscar actualizaciones"
        y "Actualizar". Solo avisa; instalar es siempre una acción manual (pestaña protegida por el código de
        seguridad). Programa la consulta automática al arrancar y una vez al día.
        Args:
            parent: Contenedor de la pestaña
        """
        self._update_info: UpdateInfo | None = None
        box = tb.LabelFrame(parent, text="Actualizaciones", padding=10)
        box.pack(fill=tbc.X, padx=10, pady=10)
        tb.Label(box, text=f"Versión instalada: {__version__}").pack(anchor=tbc.W)
        self.update_status_label = tb.Label(box, text="Última versión publicada: sin consultar", wraplength=800)
        self.update_status_label.pack(anchor=tbc.W, pady=(4, 6))
        if not is_supported():
            tb.Label(
                box,
                text="La actualización automática está disponible solo en la aplicación compilada para Windows; "
                "con el código fuente actualice con git pull.",
                wraplength=800,
            ).pack(anchor=tbc.W, pady=(0, 6))

        row = tb.Frame(box)
        row.pack(fill=tbc.X)
        self.update_check_button = tb.Button(
            row, text="Buscar actualizaciones", command=self._start_update_check, bootstyle="secondary-outline"
        )
        self.update_check_button.pack(side=tbc.LEFT, padx=(0, 10))
        self.update_apply_button = tb.Button(
            row, text="Actualizar", command=self._on_update_apply, bootstyle="warning", state=tbc.DISABLED
        )
        self.update_apply_button.pack(side=tbc.LEFT)

        self.root.after(self.UPDATE_FIRST_CHECK_MS, self._scheduled_update_check)

    def _scheduled_update_check(self) -> None:
        """Consulta automática de versiones (al arrancar y cada 24 horas)."""
        self._start_update_check()
        self.root.after(self.UPDATE_CHECK_EVERY_MS, self._scheduled_update_check)

    def _start_update_check(self) -> None:
        """Consulta el último release en un hilo (la red puede tardar) y muestra el resultado al terminar."""
        result: dict[str, UpdateInfo] = {}
        self.update_check_button.configure(state=tbc.DISABLED)
        self.update_status_label.configure(text="Consultando la última versión publicada...")
        worker = threading.Thread(
            target=lambda: result.update(info=check_latest(__version__)), name="update-check", daemon=True
        )
        worker.start()
        self._wait_thread(worker, lambda: self._show_update_info(result.get("info")))

    def _wait_thread(self, worker: threading.Thread, on_done) -> None:
        """
        Espera (sin bloquear Tk) a que termine un hilo y luego ejecuta on_done en el hilo de la ventana.
        Args:
            worker: Hilo a esperar
            on_done: Función sin argumentos a ejecutar al terminar
        """
        if worker.is_alive():
            self.root.after(500, self._wait_thread, worker, on_done)
            return
        on_done()

    def _show_update_info(self, info: UpdateInfo | None) -> None:
        """
        Muestra el resultado de la consulta y habilita "Actualizar" solo si hay una versión nueva y la instalación
        puede autoactualizarse.
        Args:
            info: Resultado de check_latest (None si el hilo falló)
        """
        self._update_info = info
        self.update_check_button.configure(state=tbc.NORMAL)
        if info is None:
            text = "No se pudo consultar la última versión"
        elif info.error:
            text = f"No se pudo consultar la última versión: {info.error}"
        elif info.available:
            text = f"NUEVA VERSIÓN DISPONIBLE: {info.latest} (instalada {__version__})"
            logger.info("Actualización disponible: %s (instalada %s)", info.latest, __version__)
        else:
            text = info.message or f"Última versión publicada: {info.latest or '--'} (está al día)"
        self.update_status_label.configure(text=text)
        can_update = bool(info and info.available and not info.error and is_supported())
        self.update_apply_button.configure(state=tbc.NORMAL if can_update else tbc.DISABLED)

    def _on_update_apply(self) -> None:
        """
        Botón "Actualizar": nunca durante una impresión; pide confirmación, descarga y verifica el paquete en un hilo
        y, si todo está bien, lanza la versión nueva en modo --apply-update y cierra esta aplicación.
        """
        info = self._update_info
        if not (info and info.available and is_supported()):
            return
        if has_processing_jobs():
            Messagebox.show_warning("Hay una impresión en curso. Intente de nuevo al terminar.", "Actualizaciones")
            return
        answer = Messagebox.yesno(
            f"Se instalará la versión {info.latest} (instalada {__version__}).\n\n"
            "La aplicación se cerrará unos segundos y volverá a abrirse sola. Durante ese tiempo no se podrá imprimir.\n"
            "La configuración, los contadores y la base de datos no se modifican.\n\n¿Desea continuar?",
            "Actualizaciones",
            buttons=["Cancelar:secondary", "Actualizar:warning"],
        )
        if answer != "Actualizar":
            return

        result: dict[str, object] = {}

        def _download() -> None:
            """Descarga, verifica y prepara el paquete (en el hilo de trabajo)."""
            try:
                result["staged"] = download_and_stage(info, get_base_path())
            except UpdateError as e:
                result["error"] = str(e)
            except Exception as e:  # noqa: BLE001 - cualquier fallo se informa, la aplicación sigue igual
                result["error"] = f"Error inesperado: {e}"

        self.update_apply_button.configure(state=tbc.DISABLED)
        self.update_check_button.configure(state=tbc.DISABLED)
        self.update_status_label.configure(text=f"Descargando y verificando la versión {info.latest}...")
        worker = threading.Thread(target=_download, name="update-download", daemon=True)
        worker.start()
        self._wait_thread(worker, lambda: self._finish_update_apply(result))

    def _finish_update_apply(self, result: dict[str, object]) -> None:
        """
        Tras la descarga: si falló, informa y deja la aplicación igual; si el paquete está listo, lanza el actualizador
        (la versión nueva) y cierra esta aplicación para que pueda reemplazar sus archivos.
        Args:
            result: {"staged": Path} o {"error": str}
        """
        if "error" in result or "staged" not in result:
            message = str(result.get("error", "No se pudo preparar la actualización"))
            logger.error("Actualización cancelada: %s", message)
            self.update_status_label.configure(text=f"Actualización cancelada: {message}")
            self.update_check_button.configure(state=tbc.NORMAL)
            self.update_apply_button.configure(state=tbc.NORMAL)
            Messagebox.show_error(message, "Actualizaciones")
            return
        if has_processing_jobs():  # pudo empezar una impresión durante la descarga
            self.update_status_label.configure(text="Impresión en curso: pulse Actualizar de nuevo al terminar")
            self.update_check_button.configure(state=tbc.NORMAL)
            self.update_apply_button.configure(state=tbc.NORMAL)
            return
        try:
            launch_apply(result["staged"], get_base_path())
        except Exception as e:  # noqa: BLE001 - si no arranca el actualizador, la aplicación sigue funcionando
            logger.error("No se pudo iniciar el actualizador: %s", e)
            Messagebox.show_error(f"No se pudo iniciar el actualizador: {e}", "Actualizaciones")
            self.update_check_button.configure(state=tbc.NORMAL)
            self.update_apply_button.configure(state=tbc.NORMAL)
            return
        logger.info("Actualizador iniciado; cerrando la aplicación para aplicar la versión %s", self._update_info.latest)
        self._quit_application()

    @staticmethod
    def _monitor_push_status_text() -> str:
        """
        Texto del estado del envío: último intento, resultado, lecturas en cola y pausa por token rechazado.
        Returns:
            str: Estado legible para la ventana
        """
        status = monitor_push.get_status()
        parts = [
            f"Último intento: {status.get('last_attempt_at') or '--'}",
            f"Resultado: {status.get('last_result') or '--'}",
            f"En cola: {status.get('pending', 0)}",
        ]
        if status.get("paused"):
            parts.append("EN PAUSA: Odoo rechazó el token")
        return " · ".join(parts)

    def _refresh_monitor_push_status(self) -> None:
        """Actualiza la etiqueta de estado del envío a Odoo."""
        self.push_status_label.configure(text=self._monitor_push_status_text())

    def _on_monitor_push_send(self) -> None:
        """
        Botón "Enviar ahora": encola una lectura manual y vacía la cola en un hilo aparte (lectura de la máquina y
        petición a Odoo pueden tardar varios segundos) para no congelar la ventana. Usa la configuración guardada.
        """
        settings = get_monitor_push_config(ConfigManager.get_config())
        if not (settings["enabled"] and settings["url"] and settings["token"]):
            Messagebox.show_warning(
                "Habilite el envío y guarde la URL y el token antes de enviar.", "Monitor fiscal en Odoo"
            )
            return
        self.push_send_button.configure(state=tbc.DISABLED)
        self.push_status_label.configure(text="Enviando lectura a Odoo...")
        worker = threading.Thread(
            target=monitor_push.send_now, args=(ConfigManager.get_config(),), name="monitor-push-manual", daemon=True
        )
        worker.start()
        self._wait_monitor_push_send(worker)

    def _wait_monitor_push_send(self, worker: threading.Thread) -> None:
        """
        Espera (sin bloquear Tk) a que termine el envío manual y luego muestra el estado. Tk no es seguro entre
        hilos, por eso se consulta el hilo desde el bucle de la ventana con after() en lugar de actualizar desde él.
        Args:
            worker: Hilo del envío manual
        """
        if worker.is_alive():
            self.root.after(500, self._wait_monitor_push_send, worker)
            return
        self.push_send_button.configure(state=tbc.NORMAL)
        self._refresh_monitor_push_status()

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
        config = ConfigManager.get_config()
        try:
            new_config = json.loads(json.dumps(config))
            new_config["server"] = {
                "allowed_origins": list(self.origins_listbox.get(0, tbc.END)),
                "auto_browser": self.sv["auto_browser"].get(),
                "scan_serial_port": self.sv["scan_serial_port"].get(),
                "server_debug": self.sv["server_debug"].get(),
                "server_host": self.sv["server_host"].get(),
                "server_mode": self.sv["server_mode"].get(),
                "server_port": int(self.sv["server_port"].get()),
            }
            new_config["proxy"] = {
                "proxy_enabled": self.sv["proxy_enabled"].get(),
                "proxy_target": self.sv["proxy_target"].get(),
            }
            new_config["logging"] = {
                "log_output": self.sv["log_output"].get(),
                "log_file": self.sv["log_file"].get(),
                "log_level": self.sv["log_level"].get(),
                "log_format": self.sv["log_format"].get(),
                "log_days": int(self.sv["log_days"].get()),
            }
            new_config["security"] = {
                "security_code": self.sv["security_code"].get(),
            }
            new_config["monitor_push"] = {
                "enabled": self.sv["push_enabled"].get(),
                "url": self.sv["push_url"].get().strip(),
                "token": self.sv["push_token"].get().strip(),
                "interval_minutes": int(self.sv["push_interval_minutes"].get()),
                "branch_code": self.sv["push_branch_code"].get().strip(),
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

    def _on_backup_db(self) -> None:
        try:
            path = backup_db()
            Messagebox.show_info(
                f"Respaldo generado exitosamente:\n\n{path}",
                "Respaldo de Base de Datos",
            )
        except Exception as e:
            logger.error("Error al crear respaldo de BD: %s", str(e))
            Messagebox.show_error(f"Error al crear respaldo:\n{e}", "Error de Respaldo")

    def _on_restore_db(self) -> None:
        try:
            default_dir = os.path.join(get_base_path(), "backups")
            file_path = filedialog.askopenfilename(
                title="Seleccionar archivo de respaldo SQLite",
                initialdir=default_dir if os.path.exists(default_dir) else get_base_path(),
                filetypes=[("Base de Datos SQLite", "*.db"), ("Todos los archivos", "*.*")],
            )
            if not file_path:
                return

            confirm = Messagebox.yesno(
                f"¿Está seguro de que desea restaurar la base de datos desde:\n\n{file_path}?\n\n"
                "La base de datos actual será sobrescrita.",
                "Confirmar Restauración",
                buttons=["Cancelar:secondary", "Restaurar:danger"],
            )
            if confirm == "Restaurar":
                restore_db(file_path)
                Messagebox.show_info(
                    "Base de datos restaurada exitosamente.",
                    "Restauración Completada",
                )
        except Exception as e:
            logger.error("Error al restaurar respaldo de BD: %s", str(e))
            Messagebox.show_error(f"Error al restaurar base de datos:\n{e}", "Error de Restauración")

    # ------------------------------------------------------------------
    # 3. Pestaña: Impresora Fiscal
    # ------------------------------------------------------------------
    def _build_fiscal_tab(self, parent) -> None:
        config = ConfigManager.get_config()
        fiscal_cfg = config.get("printers", {}).get("fiscal", {})
        template = _load_json_file(_fiscal_template_path())
        fiscal_tmpl = template.get("fiscal", {})
        fmt = template.get("format", {})

        self.fv: dict[str, tb.Variable] = {}

        # --- Hardware Fiscal ---
        hw_box = tb.LabelFrame(parent, text="Configuración del Dispositivo Fiscal (config.json)", padding=10)
        hw_box.pack(fill=tbc.X, padx=10, pady=10)
        self._add_checkbox(self.fv, hw_box, "Impresora Fiscal Habilitada", "fiscal_enabled", fiscal_cfg.get("fiscal_enabled", False))
        self._add_combobox(
            self.fv, hw_box, "Modelo", "fiscal_name", sorted(VALID_FISCAL_PRINTERS), fiscal_cfg.get("fiscal_name", "TFHKA")
        )

        port_row = tb.Frame(hw_box)
        port_row.pack(fill=tbc.X, pady=3)
        tb.Label(port_row, text="Puerto", width=22).pack(side=tbc.LEFT)
        self.fv["fiscal_port"] = tb.StringVar(value=fiscal_cfg.get("fiscal_port", ""))
        self.fiscal_port_combo = tb.Combobox(port_row, textvariable=self.fv["fiscal_port"])
        self.fiscal_port_combo.pack(side=tbc.LEFT, fill=tbc.X, expand=tbc.YES, padx=(0, 5))
        tb.Button(port_row, text="Escanear Puertos", command=self._scan_fiscal_ports, bootstyle="info").pack(side=tbc.LEFT)

        self._add_entry(self.fv, hw_box, "Baudrate", "fiscal_baudrate", fiscal_cfg.get("fiscal_baudrate", 9600))
        self._add_entry(self.fv, hw_box, "Timeout (s)", "fiscal_timeout", fiscal_cfg.get("fiscal_timeout", 2))
        self._add_combobox(
            self.fv,
            hw_box,
            "Código de Barras",
            "fiscal_barcode_type",
            sorted(VALID_BARCODE_TYPES),
            fiscal_cfg.get("fiscal_barcode_type", "CODE128"),
        )

        # --- Medios de pago (etiquetas del monitor) ---
        self._build_payment_labels_box(parent, get_payment_labels(config))

        # --- Datos de la Impresora ---
        info_box = tb.LabelFrame(parent, text="Datos de la Impresora (Plantilla)", padding=10)
        info_box.pack(fill=tbc.X, padx=10, pady=10)
        self._add_entry(self.fv, info_box, "Modelo plantilla", "model", fiscal_tmpl.get("model", ""))
        self._add_entry(self.fv, info_box, "Serial", "serial", fiscal_tmpl.get("serial", ""))
        self._add_entry(self.fv, info_box, "Nombre de Nota", "name_note", fiscal_tmpl.get("name_note", ""))

        # --- Formato del Documento ---
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

        save_row = tb.Frame(parent)
        save_row.pack(fill=tbc.X, padx=10, pady=15)
        tb.Button(
            save_row,
            text="Guardar Configuración Fiscal",
            command=self._save_fiscal_config,
            bootstyle="success",
        ).pack(side=tbc.LEFT)

    def _build_payment_labels_box(self, parent, labels: dict[str, str]) -> None:
        """
        Sección "Medios de pago (etiquetas)": 24 entradas (código: nombre) en una grilla de 4 columnas.
        Args:
            parent: Contenedor de la pestaña fiscal
            labels: Etiquetas vigentes por código ("01".."24")
        """
        self.payment_label_vars: dict[str, tb.StringVar] = {}
        box = tb.LabelFrame(parent, text="Medios de pago (etiquetas)", padding=10)
        box.pack(fill=tbc.X, padx=10, pady=10)
        tb.Label(
            box,
            text="Los nombres deben coincidir con los programados en la impresora (comando D imprime la programación)",
            bootstyle="secondary",
            wraplength=800,
        ).pack(anchor=tbc.W, pady=(0, 8))
        grid = tb.Frame(box)
        grid.pack(fill=tbc.X)
        columns = 4
        for index, code in enumerate(PAYMENT_CODES):
            row, col = divmod(index, columns)
            cell = tb.Frame(grid)
            cell.grid(row=row, column=col, sticky=tbc.EW, padx=4, pady=2)
            grid.columnconfigure(col, weight=1)
            tb.Label(cell, text=f"{code}:", width=3).pack(side=tbc.LEFT)
            var = tb.StringVar(value=labels.get(code, ""))
            self.payment_label_vars[code] = var
            tb.Entry(cell, textvariable=var, width=16).pack(side=tbc.LEFT, fill=tbc.X, expand=tbc.YES)

    def _collect_payment_labels(self) -> dict[str, str]:
        """
        Etiquetas de pago a guardar en la configuración: solo las que difieren de las de fábrica, para que
        las instalaciones sigan heredando los cambios futuros de los valores por defecto.
        Returns:
            dict[str, str]: {código: etiqueta} con las diferencias (puede incluir cadenas vacías)
        """
        defaults = _load_default_payment_labels()
        current = {code: var.get().strip() for code, var in self.payment_label_vars.items()}
        return {code: label for code, label in current.items() if label != defaults.get(code, "")}

    def _scan_fiscal_ports(self) -> None:
        try:
            scanner = get_serial_scanner()
            ports = scanner.scan_ports()
            values = [p["port"] for p in ports]
            self.fiscal_port_combo["values"] = values
            if not values:
                Messagebox.show_info("No se encontraron puertos seriales disponibles.", "Escaneo de Puertos")
        except Exception as e:
            Messagebox.show_error(f"Error escaneando puertos: {e}", "Escaneo de Puertos")

    def _update_address_lines_note(self) -> None:
        try:
            lines = self.fv["partner_address_lines"].get()
        except Exception:
            lines = 1
        remaining = 9 - lines
        self.address_lines_note.config(
            text=(
                f"Con {lines} línea(s) de dirección activa(s), quedan aproximadamente {remaining} índices "
                "(i00-i09) disponibles para teléfono, email y metadatos en impresoras TFHKA."
            )
        )

    def _save_fiscal_config(self) -> None:
        config = ConfigManager.get_config()
        try:
            new_config = json.loads(json.dumps(config))
            new_config["printers"]["fiscal"] = {
                "fiscal_enabled": self.fv["fiscal_enabled"].get(),
                "fiscal_name": self.fv["fiscal_name"].get(),
                "fiscal_port": self.fv["fiscal_port"].get(),
                "fiscal_baudrate": int(self.fv["fiscal_baudrate"].get()),
                "fiscal_timeout": int(self.fv["fiscal_timeout"].get()),
                "fiscal_barcode_type": self.fv["fiscal_barcode_type"].get(),
            }
            payment_labels = self._collect_payment_labels()
            if payment_labels:
                new_config["printers"]["fiscal"]["payment_labels"] = payment_labels
        except (ValueError, KeyError) as e:
            Messagebox.show_error(f"Valor inválido de hardware: {e}", "Impresora Fiscal")
            return

        try:
            validate(new_config, CONFIG_SCHEMA)
        except ValidationError as e:
            Messagebox.show_error(f"Configuración inválida: {e.message}", "Impresora Fiscal")
            return

        # Plantilla fiscal
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
            Messagebox.show_error(f"Plantilla inválida: {e.message}", "Impresora Fiscal")
            return

        try:
            ConfigManager.save_config(new_config)
            ConfigManager.reload_config()
            if self.flask_app is not None:
                self.flask_app.config.update(new_config)
            _save_json_file(_fiscal_template_path(), new_template)

            from server.handlers.printer_manager import PrinterManager
            fiscal_name = new_config.get("printers", {}).get("fiscal", {}).get("fiscal_name", "")
            PrinterManager.remove_printer(fiscal_name.strip().lower())
        except Exception as e:
            Messagebox.show_error(f"Error al guardar configuración fiscal: {e}", "Impresora Fiscal")
            return

        Messagebox.show_info("Configuración y plantilla fiscal guardadas correctamente.", "Impresora Fiscal")

    # ------------------------------------------------------------------
    # 4. Pestaña: Impresora Ticket
    # ------------------------------------------------------------------
    def _build_ticket_tab(self, parent) -> None:
        config = ConfigManager.get_config()
        ticket_cfg = config.get("printers", {}).get("ticket", {})
        template = _load_json_file(_ticket_template_path())
        hdr = template.get("header", {})
        ftr = template.get("footer", {})
        fmt = template.get("format", {})

        self.tv: dict[str, tb.Variable] = {}

        # --- Hardware Ticket ---
        hw_box = tb.LabelFrame(parent, text="Configuración del Dispositivo Ticket (config.json)", padding=10)
        hw_box.pack(fill=tbc.X, padx=10, pady=10)
        self._add_checkbox(self.tv, hw_box, "Impresora Ticket Habilitada", "ticket_enabled", ticket_cfg.get("ticket_enabled", False))
        self._add_entry(self.tv, hw_box, "Nombre", "ticket_name", ticket_cfg.get("ticket_name", "PDF"))
        self._add_entry(self.tv, hw_box, "Puerto / Destino", "ticket_port", ticket_cfg.get("ticket_port", "PDF"))
        self._add_combobox(self.tv, hw_box, "Papel", "ticket_paper", ["80mm", "58mm"], ticket_cfg.get("ticket_paper", "80mm"))
        self._add_entry(self.tv, hw_box, "Plantilla", "ticket_template", ticket_cfg.get("ticket_template", "template_ticket_simple.json"))
        self._add_entry(self.tv, hw_box, "Archivo de Salida", "ticket_file", ticket_cfg.get("ticket_file", "docs/ticket_output.txt"))
        self._add_checkbox(self.tv, hw_box, "Impresión Directa", "ticket_direct", ticket_cfg.get("ticket_direct", False))
        self._add_checkbox(self.tv, hw_box, "Usar ESC/POS", "ticket_use_escpos", ticket_cfg.get("ticket_use_escpos", False))
        self._add_checkbox(self.tv, hw_box, "Código de Barras Habilitado", "barcode_enabled", ticket_cfg.get("barcode_enabled", False))
        self._add_combobox(
            self.tv,
            hw_box,
            "Tipo de Código de Barras",
            "barcode_type",
            sorted(VALID_BARCODE_TYPES),
            ticket_cfg.get("barcode_type", "BARCODE"),
        )
        self._add_checkbox(self.tv, hw_box, "Logo Habilitado", "logo_enabled", ticket_cfg.get("logo_enabled", False))
        self._add_entry(self.tv, hw_box, "Ancho de Logo (px)", "logo_width", ticket_cfg.get("logo_width", 480))
        self._add_entry(self.tv, hw_box, "Alto de Logo (px)", "logo_height", ticket_cfg.get("logo_height", 160))

        # --- Encabezado y Pie de Página (Plantilla) ---
        text_box = tb.LabelFrame(parent, text="Encabezado y Pie de Ticket (template_ticket_simple.json)", padding=10)
        text_box.pack(fill=tbc.X, padx=10, pady=10)
        self._add_entry(self.tv, text_box, "Título", "ticket_header_title", hdr.get("title", ""))
        self._add_entry(self.tv, text_box, "Subtítulo / RIF", "ticket_header_subtitle", hdr.get("subtitle", ""))
        self._add_entry(self.tv, text_box, "Empresa", "ticket_header_company", hdr.get("company", ""))
        self._add_entry(self.tv, text_box, "Dirección", "ticket_header_address", hdr.get("address", ""))
        self._add_entry(self.tv, text_box, "Teléfono", "ticket_header_phone", hdr.get("phone", ""))
        self._add_entry(self.tv, text_box, "Tipo de Documento", "ticket_header_type", hdr.get("type", ""))
        self._add_entry(self.tv, text_box, "Etiqueta Número", "ticket_header_name", hdr.get("name", ""))
        self._add_entry(self.tv, text_box, "Mensaje de Pie", "ticket_footer_message", ftr.get("message", ""))
        self._add_entry(self.tv, text_box, "Texto Legal", "ticket_footer_legal", ftr.get("legal", ""))

        # --- Formato del Ticket ---
        format_box = tb.LabelFrame(parent, text="Formato del Ticket (Plantilla)", padding=10)
        format_box.pack(fill=tbc.X, padx=10, pady=10)
        self._add_entry(self.tv, format_box, "Ancho en caracteres", "ticket_format_width", fmt.get("width", 64))
        self._add_entry(self.tv, format_box, "Separador", "ticket_format_separator", fmt.get("separator", "-"))
        self._add_combobox(self.tv, format_box, "Fuente", "ticket_format_font", ["A", "B"], fmt.get("font", "B"))
        self._add_entry(self.tv, format_box, "Ancho desc. ítem", "ticket_format_desc_width", fmt.get("width_item_description", 15))
        self._add_entry(self.tv, format_box, "Espacio libre", "ticket_format_free_space", fmt.get("width_free_space", 15))

        grid = tb.Frame(format_box)
        grid.pack(fill=tbc.X, pady=5)
        for index, (key, label) in enumerate(TICKET_FORMAT_FLAGS):
            var = tb.BooleanVar(value=bool(fmt.get(key, False)))
            self.tv[f"fmt_{key}"] = var
            row, col = divmod(index, 2)
            tb.Checkbutton(grid, text=label, variable=var, bootstyle="round-toggle").grid(
                row=row, column=col, sticky=tbc.W, padx=10, pady=4
            )

        save_row = tb.Frame(parent)
        save_row.pack(fill=tbc.X, padx=10, pady=15)
        tb.Button(
            save_row,
            text="Guardar Configuración Ticket",
            command=self._save_ticket_config,
            bootstyle="success",
        ).pack(side=tbc.LEFT)

    def _save_ticket_config(self) -> None:
        config = ConfigManager.get_config()
        try:
            new_config = json.loads(json.dumps(config))
            new_config["printers"]["ticket"] = {
                "ticket_enabled": self.tv["ticket_enabled"].get(),
                "ticket_name": self.tv["ticket_name"].get(),
                "ticket_port": self.tv["ticket_port"].get(),
                "ticket_paper": self.tv["ticket_paper"].get(),
                "ticket_template": self.tv["ticket_template"].get(),
                "ticket_file": self.tv["ticket_file"].get(),
                "ticket_direct": self.tv["ticket_direct"].get(),
                "ticket_use_escpos": self.tv["ticket_use_escpos"].get(),
                "barcode_enabled": self.tv["barcode_enabled"].get(),
                "barcode_type": self.tv["barcode_type"].get(),
                "logo_enabled": self.tv["logo_enabled"].get(),
                "logo_width": int(self.tv["logo_width"].get()),
                "logo_height": int(self.tv["logo_height"].get()),
            }
        except (ValueError, KeyError) as e:
            Messagebox.show_error(f"Valor inválido de hardware: {e}", "Impresora Ticket")
            return

        try:
            validate(new_config, CONFIG_SCHEMA)
        except ValidationError as e:
            Messagebox.show_error(f"Configuración inválida: {e.message}", "Impresora Ticket")
            return

        # Actualizar plantilla ticket
        template = _load_json_file(_ticket_template_path())
        template["header"] = {
            "title": self.tv["ticket_header_title"].get(),
            "subtitle": self.tv["ticket_header_subtitle"].get(),
            "company": self.tv["ticket_header_company"].get(),
            "address": self.tv["ticket_header_address"].get(),
            "phone": self.tv["ticket_header_phone"].get(),
            "type": self.tv["ticket_header_type"].get(),
            "name": self.tv["ticket_header_name"].get(),
        }
        template["footer"] = {
            "message": self.tv["ticket_footer_message"].get(),
            "legal": self.tv["ticket_footer_legal"].get(),
        }
        fmt = template.setdefault("format", {})
        try:
            fmt["width"] = int(self.tv["ticket_format_width"].get())
            fmt["separator"] = self.tv["ticket_format_separator"].get()
            fmt["font"] = self.tv["ticket_format_font"].get()
            fmt["width_item_description"] = int(self.tv["ticket_format_desc_width"].get())
            fmt["width_free_space"] = int(self.tv["ticket_format_free_space"].get())
            for key, _ in TICKET_FORMAT_FLAGS:
                fmt[key] = self.tv[f"fmt_{key}"].get()
        except ValueError as e:
            Messagebox.show_error(f"Formato numérico inválido en plantilla ticket: {e}", "Impresora Ticket")
            return

        try:
            ConfigManager.save_config(new_config)
            ConfigManager.reload_config()
            if self.flask_app is not None:
                self.flask_app.config.update(new_config)
            _save_json_file(_ticket_template_path(), template)
        except Exception as e:
            Messagebox.show_error(f"Error al guardar configuración ticket: {e}", "Impresora Ticket")
            return

        Messagebox.show_info("Configuración y plantilla de ticket guardadas correctamente.", "Impresora Ticket")

    # ------------------------------------------------------------------
    # 5. Pestaña: Impresora Matrix
    # ------------------------------------------------------------------
    def _build_matrix_tab(self, parent) -> None:
        config = ConfigManager.get_config()
        matrix_cfg = config.get("printers", {}).get("matrix", {})
        template = _load_json_file(_matrix_template_path())
        hdr = template.get("header", {})
        ftr = template.get("footer", {})
        fmt = template.get("format", {})

        self.mv: dict[str, tb.Variable] = {}

        # --- Hardware Matrix ---
        hw_box = tb.LabelFrame(parent, text="Configuración del Dispositivo Matriz (config.json)", padding=10)
        hw_box.pack(fill=tbc.X, padx=10, pady=10)
        self._add_checkbox(self.mv, hw_box, "Impresora Matriz Habilitada", "matrix_enabled", matrix_cfg.get("matrix_enabled", False))
        self._add_entry(self.mv, hw_box, "Nombre", "matrix_name", matrix_cfg.get("matrix_name", "LX-350"))
        self._add_entry(self.mv, hw_box, "Puerto / Destino", "matrix_port", matrix_cfg.get("matrix_port", "EPSON LX-350"))
        self._add_combobox(
            self.mv,
            hw_box,
            "Papel",
            "matrix_paper",
            sorted(VALID_MATRIX_PAPER_TYPES),
            matrix_cfg.get("matrix_paper", "MEDIA_CARTA"),
        )
        self._add_entry(self.mv, hw_box, "Plantilla", "matrix_template", matrix_cfg.get("matrix_template", "template_matriz_carta.json"))
        self._add_entry(self.mv, hw_box, "Archivo de Salida", "matrix_file", matrix_cfg.get("matrix_file", "docs/print_output.txt"))
        self._add_checkbox(self.mv, hw_box, "Impresión Directa", "matrix_direct", matrix_cfg.get("matrix_direct", False))
        self._add_checkbox(self.mv, hw_box, "Usar ESC/P", "matrix_use_escp", matrix_cfg.get("matrix_use_escp", False))

        # --- Encabezado y Pie de Matriz ---
        text_box = tb.LabelFrame(parent, text="Encabezado y Pie de Matriz (template_matriz_carta.json)", padding=10)
        text_box.pack(fill=tbc.X, padx=10, pady=10)
        self._add_entry(self.mv, text_box, "Título", "matrix_header_title", hdr.get("title", ""))
        self._add_entry(self.mv, text_box, "Subtítulo / RIF", "matrix_header_subtitle", hdr.get("subtitle", ""))
        self._add_entry(self.mv, text_box, "Empresa", "matrix_header_company", hdr.get("company", ""))
        self._add_entry(self.mv, text_box, "Dirección", "matrix_header_address", hdr.get("address", ""))
        self._add_entry(self.mv, text_box, "Teléfono", "matrix_header_phone", hdr.get("phone", ""))
        self._add_entry(self.mv, text_box, "Tipo de Documento", "matrix_header_type", hdr.get("type", ""))
        self._add_entry(self.mv, text_box, "Mensaje de Pie", "matrix_footer_message", ftr.get("message", ""))
        self._add_entry(self.mv, text_box, "Texto Legal", "matrix_footer_legal", ftr.get("legal", ""))

        # --- Formato de Matriz ---
        format_box = tb.LabelFrame(parent, text="Formato de Matriz (Plantilla)", padding=10)
        format_box.pack(fill=tbc.X, padx=10, pady=10)
        self._add_entry(self.mv, format_box, "Ancho de página", "matrix_format_page_width", fmt.get("page_width", 80))
        self._add_entry(self.mv, format_box, "Margen izquierdo", "matrix_format_margin_left", fmt.get("margin_left", 5))
        self._add_entry(self.mv, format_box, "Margen superior", "matrix_format_margin_top", fmt.get("margin_top", 3))
        self._add_entry(self.mv, format_box, "Margen inferior", "matrix_format_margin_bottom", fmt.get("margin_bottom", 3))
        self._add_entry(self.mv, format_box, "Separador", "matrix_format_separator", fmt.get("separator", "="))

        grid = tb.Frame(format_box)
        grid.pack(fill=tbc.X, pady=5)
        for index, (key, label) in enumerate(MATRIX_FORMAT_FLAGS):
            var = tb.BooleanVar(value=bool(fmt.get(key, False)))
            self.mv[f"fmt_{key}"] = var
            row, col = divmod(index, 2)
            tb.Checkbutton(grid, text=label, variable=var, bootstyle="round-toggle").grid(
                row=row, column=col, sticky=tbc.W, padx=10, pady=4
            )

        save_row = tb.Frame(parent)
        save_row.pack(fill=tbc.X, padx=10, pady=15)
        tb.Button(
            save_row,
            text="Guardar Configuración Matrix",
            command=self._save_matrix_config,
            bootstyle="success",
        ).pack(side=tbc.LEFT)

    def _save_matrix_config(self) -> None:
        config = ConfigManager.get_config()
        try:
            new_config = json.loads(json.dumps(config))
            new_config["printers"]["matrix"] = {
                "matrix_enabled": self.mv["matrix_enabled"].get(),
                "matrix_name": self.mv["matrix_name"].get(),
                "matrix_port": self.mv["matrix_port"].get(),
                "matrix_paper": self.mv["matrix_paper"].get(),
                "matrix_template": self.mv["matrix_template"].get(),
                "matrix_file": self.mv["matrix_file"].get(),
                "matrix_direct": self.mv["matrix_direct"].get(),
                "matrix_use_escp": self.mv["matrix_use_escp"].get(),
            }
        except (ValueError, KeyError) as e:
            Messagebox.show_error(f"Valor inválido de hardware: {e}", "Impresora Matrix")
            return

        try:
            validate(new_config, CONFIG_SCHEMA)
        except ValidationError as e:
            Messagebox.show_error(f"Configuración inválida: {e.message}", "Impresora Matrix")
            return

        # Actualizar plantilla matriz
        template = _load_json_file(_matrix_template_path())
        template["header"] = {
            **template.get("header", {}),
            "title": self.mv["matrix_header_title"].get(),
            "subtitle": self.mv["matrix_header_subtitle"].get(),
            "company": self.mv["matrix_header_company"].get(),
            "address": self.mv["matrix_header_address"].get(),
            "phone": self.mv["matrix_header_phone"].get(),
            "type": self.mv["matrix_header_type"].get(),
        }
        template["footer"] = {
            "message": self.mv["matrix_footer_message"].get(),
            "legal": self.mv["matrix_footer_legal"].get(),
        }
        fmt = template.setdefault("format", {})
        try:
            fmt["page_width"] = int(self.mv["matrix_format_page_width"].get())
            fmt["margin_left"] = int(self.mv["matrix_format_margin_left"].get())
            fmt["margin_top"] = int(self.mv["matrix_format_margin_top"].get())
            fmt["margin_bottom"] = int(self.mv["matrix_format_margin_bottom"].get())
            fmt["separator"] = self.mv["matrix_format_separator"].get()
            for key, _ in MATRIX_FORMAT_FLAGS:
                fmt[key] = self.mv[f"fmt_{key}"].get()
        except ValueError as e:
            Messagebox.show_error(f"Formato numérico inválido en plantilla matriz: {e}", "Impresora Matrix")
            return

        try:
            ConfigManager.save_config(new_config)
            ConfigManager.reload_config()
            if self.flask_app is not None:
                self.flask_app.config.update(new_config)
            _save_json_file(_matrix_template_path(), template)
        except Exception as e:
            Messagebox.show_error(f"Error al guardar configuración matriz: {e}", "Impresora Matrix")
            return

        Messagebox.show_info("Configuración y plantilla de matriz guardadas correctamente.", "Impresora Matrix")

    # ------------------------------------------------------------------
    # 6. Pestaña: Comandos
    # ------------------------------------------------------------------
    def _build_commands_tab(self, parent) -> None:
        # --- Comandos Fiscales Directos ---
        cmd_frame = tb.LabelFrame(parent, text="Comandos Fiscales Directos", bootstyle="secondary", padding=10)
        cmd_frame.pack(fill=tbc.X, padx=10, pady=10)

        tb.Label(
            cmd_frame,
            text='Pega un JSON con la estructura {"commands": ["CMD1", "CMD2"]} y presiona Enviar.',
            wraplength=800,
        ).pack(anchor=tbc.W, pady=(0, 5))

        self.commands_text = tb.Text(cmd_frame, height=12)
        self.commands_text.pack(fill=tbc.X, pady=5)
        self.commands_text.insert("1.0", '{\n    "commands": [\n        "S1",\n        "I0X"\n    ]\n}')

        cmd_btn_frame = tb.Frame(cmd_frame)
        cmd_btn_frame.pack(fill=tbc.X, pady=(0, 5))
        tb.Button(cmd_btn_frame, text="Enviar Comandos", command=self._send_commands, bootstyle="warning").pack(
            side=tbc.LEFT
        )

        # --- Reportes Fiscales ---
        reports_frame = tb.LabelFrame(parent, text="Reportes Fiscales", bootstyle="secondary", padding=10)
        reports_frame.pack(fill=tbc.X, padx=10, pady=10)

        tb.Label(
            reports_frame,
            text="Impresión de reportes X (lectura) y Z (cierre diario).",
            wraplength=800,
        ).pack(anchor=tbc.W, pady=(0, 5))

        reports_btn_row = tb.Frame(reports_frame)
        reports_btn_row.pack(fill=tbc.X, pady=5)
        tb.Button(
            reports_btn_row, text="Imprimir Reporte X", command=lambda: self._print_report("X"), bootstyle="primary"
        ).pack(side=tbc.LEFT, padx=(0, 10))
        tb.Button(
            reports_btn_row, text="Imprimir Reporte Z", command=lambda: self._print_report("Z"), bootstyle="danger"
        ).pack(side=tbc.LEFT)

        # --- Reloj de la impresora ---
        clock_frame = tb.LabelFrame(parent, text="Reloj de la Impresora", bootstyle="secondary", padding=10)
        clock_frame.pack(fill=tbc.X, padx=10, pady=10)

        tb.Label(
            clock_frame,
            text=(
                "Ajusta la fecha y hora de la máquina con las del servidor. La máquina solo lo permite "
                "justo después de un cierre Z (también se hace automáticamente al emitir el Z)."
            ),
            wraplength=800,
        ).pack(anchor=tbc.W, pady=(0, 5))
        tb.Button(
            clock_frame, text="Ajustar reloj de la impresora", command=self._sync_printer_clock, bootstyle="info"
        ).pack(anchor=tbc.W, pady=5)

    def _sync_printer_clock(self) -> None:
        """Solicita al servidor el ajuste forzado del reloj de la impresora y muestra el resultado."""
        title = "Reloj de la Impresora"
        try:
            import requests

            config = ConfigManager.get_config()
            port = config.get("server", {}).get("server_port", 5051)
            resp = requests.post(f"http://127.0.0.1:{port}/api/fiscal/clock", json={"force": True}, timeout=30)
            res_json = resp.json()
            data = res_json.get("data") or {}
            status = data.get("status")
            if status == "adjusted":
                Messagebox.show_info(f"Reloj ajustado. Diferencia previa: {data.get('drift_before')} s", title)
            elif status == "in_sync":
                Messagebox.show_info(f"El reloj ya está en hora (diferencia: {data.get('drift_seconds')} s).", title)
            elif status == "rejected":
                Messagebox.show_error(
                    f"{data.get('message')}\nRealice el ajuste justo después del cierre Z.", title
                )
            else:
                Messagebox.show_error(f"No se pudo ajustar el reloj:\n{res_json.get('message')}", title)
        except Exception as e:  # noqa: BLE001 - cualquier fallo se muestra al usuario en un diálogo
            Messagebox.show_error(f"Error al ajustar el reloj: {e}", title)

    def _send_commands(self) -> None:
        try:
            raw = self.commands_text.get("1.0", tbc.END).strip()
            data = json.loads(raw)
            commands = data.get("commands", [])
            if not isinstance(commands, list) or not commands:
                Messagebox.show_error("El JSON debe contener una lista no vacía en 'commands'.", "Comandos")
                return

            import requests
            config = ConfigManager.get_config()
            port = config.get("server", {}).get("server_port", 5051)
            resp = requests.post(f"http://127.0.0.1:{port}/api/fiscal/command", json={"commands": commands}, timeout=15)
            res_json = resp.json()
            if res_json.get("status"):
                Messagebox.show_info(f"Comandos enviados con éxito:\n{json.dumps(res_json.get('data'), indent=2)}", "Comandos")
            else:
                Messagebox.show_error(f"Falla al ejecutar comandos:\n{res_json.get('message')}", "Comandos")
        except Exception as e:
            Messagebox.show_error(f"Error al enviar comandos: {e}", "Comandos")

    def _print_report(self, report_type: str) -> None:
        try:
            import requests
            config = ConfigManager.get_config()
            port = config.get("server", {}).get("server_port", 5051)
            endpoint = "report_x" if report_type == "X" else "report_z"
            resp = requests.post(f"http://127.0.0.1:{port}/api/{endpoint}", timeout=20)
            res_json = resp.json()
            if res_json.get("status"):
                Messagebox.show_info(f"Reporte {report_type} ejecutado correctamente.", "Reportes Fiscales")
            else:
                Messagebox.show_error(f"Error al imprimir reporte {report_type}:\n{res_json.get('message')}", "Reportes Fiscales")
        except Exception as e:
            Messagebox.show_error(f"Error al solicitar reporte {report_type}: {e}", "Reportes Fiscales")

    # ------------------------------------------------------------------
    # Helpers para construcción de widgets
    # ------------------------------------------------------------------
    def _add_entry(self, store: dict, parent, label: str, key: str, value: Any, show: str = None) -> None:
        row = tb.Frame(parent)
        row.pack(fill=tbc.X, pady=3)
        tb.Label(row, text=label, width=22).pack(side=tbc.LEFT)
        var = tb.StringVar(value=str(value) if value is not None else "")
        store[key] = var
        entry_kwargs = {"show": show} if show else {}
        tb.Entry(row, textvariable=var, **entry_kwargs).pack(side=tbc.LEFT, fill=tbc.X, expand=tbc.YES)

    def _add_checkbox(self, store: dict, parent, label: str, key: str, value: bool) -> None:
        var = tb.BooleanVar(value=bool(value))
        store[key] = var
        tb.Checkbutton(parent, text=label, variable=var, bootstyle="round-toggle").pack(anchor=tbc.W, pady=3)

    def _add_combobox(self, store: dict, parent, label: str, key: str, values: list[str], value: Any) -> None:
        row = tb.Frame(parent)
        row.pack(fill=tbc.X, pady=3)
        tb.Label(row, text=label, width=22).pack(side=tbc.LEFT)
        var = tb.StringVar(value=str(value) if value is not None else "")
        store[key] = var
        tb.Combobox(row, textvariable=var, values=values, state="readonly").pack(
            side=tbc.LEFT, fill=tbc.X, expand=tbc.YES
        )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
    window = MainWindow()
    window.show()
    window.mainloop()
