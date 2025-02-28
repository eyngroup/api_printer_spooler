// Variables globales
let requestsChart = null;
let requestData = {
    labels: [],
    datasets: [{
        label: 'Peticiones por Minuto',
        data: [],
        borderColor: 'rgb(75, 192, 192)',
        tension: 0.1
    }]
};

// Variables globales para el modal de seguridad
let securityModal = null;
let pendingAction = null;

// Inicialización
document.addEventListener('DOMContentLoaded', function() {
    initializeChart();
    updateDashboard();
    // Actualizar cada 5 segundos
    setInterval(updateDashboard, 5000);
    
    // Inicializar modal de seguridad
    securityModal = new bootstrap.Modal(document.getElementById('securityCodeModal'));
    
    // Event listeners para botones de reporte
    document.getElementById('printReportX').addEventListener('click', () => {
        pendingAction = printReportX;
        showSecurityModal('Imprimir Reporte X');
    });
    
    document.getElementById('printReportZ').addEventListener('click', () => {
        pendingAction = printReportZ;
        showSecurityModal('Imprimir Reporte Z');
    });
    
    // Event listener para el botón de configuración
    document.getElementById('configEditorBtn').addEventListener('click', () => {
        pendingAction = openConfigEditor;
        showSecurityModal('Acceder al Editor de Configuración');
    });
    
    // Event listener para el botón de confirmar código
    document.getElementById('confirmSecurityCode').addEventListener('click', validateSecurityCode);
    
    // Limpiar código cuando se cierra el modal
    document.getElementById('securityCodeModal').addEventListener('hidden.bs.modal', () => {
        document.getElementById('securityCode').value = '';
        document.getElementById('securityCode').classList.remove('is-invalid');
        document.getElementById('securityCodeModalLabel').textContent = 'Código de Seguridad';
    });
});

// Inicializar gráfico
function initializeChart() {
    const ctx = document.getElementById('requestsChart').getContext('2d');
    requestsChart = new Chart(ctx, {
        type: 'line',
        data: requestData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// Actualizar dashboard
async function updateDashboard() {
    try {
        const response = await fetch('/api/status');
        console.log('Status response:', response.status);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Dashboard data:', data);
        
        if (!data || !data.config) {
            throw new Error('Datos de configuración no válidos');
        }
        
        // Limpiar notificación de error si existe
        clearNotification();
        
        // Actualizar estado del servidor
        updateServerStatus(data.status === 'running');
        document.getElementById('lastUpdate').textContent = new Date().toLocaleString();
        
        // Actualizar estado de impresoras
        const printers = data.config.printers || {};
        
        // Actualizar cada impresora y su estado
        const updatePrinter = (type, statusId, displayName) => {
            const config = printers[type];
            const enabled = config ? config[`${type}_enabled`] : false;
            const name = config ? config[`${type}_name`] : '';
            
            updatePrinterStatus(statusId, enabled);
            updatePrinterName(statusId, displayName, name);
        };
        
        updatePrinter('matrix', 'matrixStatus', 'Impresora Matricial');
        updatePrinter('ticket', 'ticketStatus', 'Impresora de Tickets');
        updatePrinter('fiscal', 'fiscalStatus', 'Impresora Fiscal');
        
        // Actualizar configuración actual
        const serverConfig = data.config.server || {};
        const loggingConfig = data.config.logging || {};
        
        // Determinar el puerto activo de la impresora
        let activePort = '--';
        if (printers.matrix?.matrix_enabled) {
            activePort = printers.matrix.matrix_port;
        } else if (printers.ticket?.ticket_enabled) {
            activePort = printers.ticket.ticket_port;
        } else if (printers.fiscal?.fiscal_enabled) {
            activePort = printers.fiscal.fiscal_port;
        }
        
        // Actualizar campos de configuración
        const updateElement = (id, value) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value || '--';
            }
        };
        
        updateElement('serverPort', serverConfig.server_port);
        updateElement('serverUrl', `${window.location.protocol}//${serverConfig.server_host}:${serverConfig.server_port}`);
        updateElement('apiPath', '/api');
        updateElement('logLevel', loggingConfig.log_level);
        updateElement('activePrinterPort', activePort);
        
        // Actualizar estadísticas
        updateElement('requestCount', data.stats?.requests_total);
        updateElement('uptime', formatUptime(data.uptime));
        updateElement('errorCount', data.stats?.error_count);
        
        // Actualizar últimos errores si hay alguno
        if (data.stats?.last_errors && data.stats.last_errors.length > 0) {
            const lastError = data.stats.last_errors[data.stats.last_errors.length - 1];
            showNotification('Error', lastError.message, 'error');
        }
        
        // Actualizar gráfico
        updateChart(data.stats?.requests_total || 0);
        
    } catch (error) {
        console.error('Error completo:', error);
        showNotification('Error', `Error actualizando dashboard: ${error.message}`, 'error');
    }
}

// Actualizar estado de impresora
function updatePrinterStatus(elementId, isEnabled) {
    const element = document.getElementById(elementId);
    if (element) {
        element.className = `status-indicator me-2 ${isEnabled ? 'active' : 'inactive'}`;
    }
}

// Actualizar nombre de impresora
function updatePrinterName(elementId, defaultName, printerName) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    const label = element.nextElementSibling;
    if (label) {
        label.textContent = printerName ? `${defaultName} (${printerName})` : defaultName;
    }
}

// Actualizar estado del servidor
function updateServerStatus(isRunning) {
    const element = document.getElementById('serverStatus');
    if (element) {
        element.className = `status-indicator me-2 ${isRunning ? 'active' : 'inactive'}`;
    }
}

// Formatear tiempo activo
function formatUptime(seconds) {
    if (!seconds) return '--';
    
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours}h ${minutes}m`;
}

// Mostrar notificación
function showNotification(title, message, type = 'info') {
    clearNotification(); // Limpiar notificaciones anteriores
    
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 end-0 m-3`;
    toast.setAttribute('role', 'alert');
    toast.style.zIndex = '9999';
    toast.innerHTML = `
        <strong>${title}:</strong> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    document.body.appendChild(toast);
    
    // Remover después de 5 segundos
    setTimeout(() => {
        if (toast && toast.parentElement) {
            toast.remove();
        }
    }, 5000);
}

// Limpiar notificación
function clearNotification() {
    const existingAlerts = document.querySelectorAll('.alert');
    existingAlerts.forEach(alert => {
        if (alert && alert.parentElement) {
            alert.remove();
        }
    });
}

// Actualizar gráfico
function updateChart(requestsPerMinute) {
    const now = new Date();
    const timeLabel = now.toLocaleTimeString();
    
    requestData.labels.push(timeLabel);
    requestData.datasets[0].data.push(requestsPerMinute);
    
    // Mantener solo los últimos 10 puntos
    if (requestData.labels.length > 10) {
        requestData.labels.shift();
        requestData.datasets[0].data.shift();
    }
    
    requestsChart.update();
}

// Mostrar modal de seguridad
function showSecurityModal(action) {
    document.getElementById('securityCode').classList.remove('is-invalid');
    document.getElementById('securityCodeModalLabel').textContent = action;
    securityModal.show();
}

// Validar código de seguridad
async function validateSecurityCode() {
    const securityCode = document.getElementById('securityCode').value;
    const securityInput = document.getElementById('securityCode');
    
    try {
        const response = await fetch('/api/auth/validate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ security_code: securityCode })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            securityModal.hide();
            if (pendingAction) {
                pendingAction();
                pendingAction = null;
            }
        } else {
            securityInput.classList.add('is-invalid');
            showNotification('Error', data.message || 'Código de seguridad incorrecto', 'error');
        }
    } catch (error) {
        console.error('Error validando código:', error);
        showNotification('Error', 'Error al validar el código de seguridad', 'error');
    }
}

// Abrir editor de configuración
function openConfigEditor() {
    window.location.href = '/config-editor.html';
}

// Imprimir Reporte X
async function printReportX() {
    try {
        const response = await fetch('/api/report_x', {
            method: 'GET'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showNotification('Éxito', 'Reporte X enviado a la impresora', 'success');
        } else {
            throw new Error(data.message || 'Error al imprimir reporte X');
        }
    } catch (error) {
        console.error('Error imprimiendo reporte X:', error);
        showNotification('Error', error.message, 'error');
    }
}

// Imprimir Reporte Z
async function printReportZ() {
    try {
        const response = await fetch('/api/report_z', {
            method: 'GET'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showNotification('Éxito', 'Reporte Z enviado a la impresora', 'success');
        } else {
            throw new Error(data.message || 'Error al imprimir reporte Z');
        }
    } catch (error) {
        console.error('Error imprimiendo reporte Z:', error);
        showNotification('Error', error.message, 'error');
    }
}

// Funciones para los botones de acción
async function checkPrinterStatus() {
    // TODO: Implementar verificación de estado de impresora
    alert('Función de verificación de estado en desarrollo');
}
