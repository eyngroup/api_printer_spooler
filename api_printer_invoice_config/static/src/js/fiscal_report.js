/** @odoo-module */

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";

class PrinterResponseDialog extends Component {}
PrinterResponseDialog.template = "api_printer_invoice.PrinterResponseDialog";
PrinterResponseDialog.components = { Dialog };

class FiscalReportAction extends Component {
    setup() {
        this.notification = useService("notification");
        this.rpc = useService("rpc");
        this.action = useService("action");
        this.dialog = useService("dialog");
        this.executeReport();
    }

    async executeReport() {
        try {
            const config = await this.rpc("/web/session/get_session_info");
            const url = `${config.aps_ip || 'http://localhost'}:${config.aps_port || '5051'}`;
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