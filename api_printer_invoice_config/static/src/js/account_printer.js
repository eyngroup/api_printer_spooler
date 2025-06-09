/** @odoo-module **/

import { registry } from "@web/core/registry";

async function PrinterInvoiceAPI(parent, { params }) {
    try {
        var xhr = new XMLHttpRequest();
        xhr.open("POST", params.url, true);
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.send(JSON.stringify(params.data));

        xhr.onload = function () {
            let response;
            try {
                response = JSON.parse(xhr.responseText);
            } catch (e) {
                console.error(`Error ${xhr.status}: ${xhr.statusText}`);
                alert(`Error de conexión: ${xhr.statusText}`);
                return;
            }

            if (response.status === true) {
                parent.services.orm.call(
                    "account.move",
                    "update_printer_response",
                    [[params.invoice_id], response.data]
                ).then(() => {
                    parent.services.action.doAction({
                        type: 'ir.actions.client',
                        tag: 'reload',
                    });

                    const successMessage = `
                        ${response.message}
                        
                        Detalles del documento:
                        - Fecha: ${response.data.document_date}
                        - Número: ${response.data.document_number}
                        - Reporte: ${response.data.machine_report}
                        - Serial: ${response.data.machine_serial}
                    `;

                    alert(successMessage);
                });
            } else {
                // Caso de error con información de la impresora
                if (response.data && (response.data.Estado || response.data.Error)) {
                    const errorMessage = `
${response.message}

Estado de la Impresora:
- Estado: ${response.data.Estado}
- Error: ${response.data.Error}`;
                    alert(errorMessage);
                } else {
                    // Otros errores
                    alert(response.message || "Error al procesar el documento");
                }
            }
        };

        xhr.onerror = function () {
            console.error("Error de conexión al servidor");
            alert("Error al conectar con el servidor. Compruebe que el servicio está activo.");
        };
    } catch (error) {
        console.error("Error:", error);
        alert("Error al intentar conectar con el servidor, ¿está activo el servicio?");
    }
}

registry.category("actions").add("PrinterInvoiceAPI", PrinterInvoiceAPI);