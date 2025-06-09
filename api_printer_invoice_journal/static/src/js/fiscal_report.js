/** @odoo-module */

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";

class PrinterResponseDialog extends Component {
    setup() {
        this.close = () => this.props.close();
    }
}
PrinterResponseDialog.template = "api_printer_invoice.PrinterResponseDialog";
PrinterResponseDialog.components = { Dialog };

class FiscalReportAction extends Component {
    setup() {
        this.notification = useService("notification");
        this.rpc = useService("rpc");
        this.action = useService("action");
        this.dialog = useService("dialog");
        this.orm = useService("orm");
        this.executeReport();
    }

    async executeReport() {
        try {
            // Obtener la configuración del diario seleccionado
            const journal = await this.orm.read(
                "account.journal",
                [this.props.action.params.journal_id],
                ["aps_ip", "aps_port"]
            );

            if (!journal.length || !journal[0].aps_ip || !journal[0].aps_port) {
                throw new Error("Configuración de impresora no encontrada en el diario");
            }

            const url = `${journal[0].aps_ip}:${journal[0].aps_port}`;
            const reportType = this.props.action.params.report_type;

            var xhr = new XMLHttpRequest();
            xhr.open("GET", `${url}/api/report_${reportType}`, true);
            xhr.send();

            xhr.onload = () => {
                let response;
                try {
                    response = JSON.parse(xhr.responseText);
                } catch (e) {
                    console.error('Error parsing response:', xhr.responseText);
                    this.showDialog('Error', 'Error al procesar la respuesta del servidor');
                    return;
                }

                const title = response.status === true ? 'Éxito' : 'Error';
                this.showDialog(title, response.message || 'Error desconocido');
                
                // Regresar al menú anterior
                this.action.doAction({ type: 'ir.actions.act_window_close' });
            };

            xhr.onerror = () => {
                console.error("Error de conexión al servidor");
                this.showDialog(
                    'Error de Conexión',
                    "Error al conectar con el servidor. Compruebe que el servicio está activo."
                );
                // Regresar al menú anterior en caso de error
                this.action.doAction({ type: 'ir.actions.act_window_close' });
            };
        } catch (error) {
            console.error("Error:", error);
            this.showDialog(
                'Error',
                "Error al intentar conectar con el servidor, ¿está activo el servicio?"
            );
            // Regresar al menú anterior en caso de error
            this.action.doAction({ type: 'ir.actions.act_window_close' });
        }
    }

    showDialog(title, message) {
        this.dialog.add(PrinterResponseDialog, {
            title,
            message,
            size: 'medium'
        });
    }
}

FiscalReportAction.template = "api_printer_invoice.FiscalReportAction";

registry.category("actions").add("fiscal_report", FiscalReportAction);

export default FiscalReportAction;