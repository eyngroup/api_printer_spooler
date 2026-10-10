// Variables globales
let requestsChart = null;
let requestData = {
    labels: [],
    datasets: [{
        label: 'Peticiones por Minuto',
        data: [],
        backgroundColor: 'rgba(75, 192, 192, 0.6)',
        borderColor: 'rgb(75, 192, 192)',
        borderWidth: 1
    }]
};

// Inicialización
// Panel de solo lectura: las acciones (reportes X/Z, comandos, configuración) están en la ventana de escritorio
document.addEventListener('DOMContentLoaded', function () {
    initializeChart();
    updateDashboard();
    // Actualizar cada 5 segundos
    setInterval(updateDashboard, 5000);
});

// Inicializar gráfico
function initializeChart() {
    const ctx = document.getElementById('requestsChart').getContext('2d');
    requestsChart = new Chart(ctx, {
        type: 'bar',
        data: requestData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {precision: 0}
                },
                x: {
                    ticks: {maxTicksLimit: 12}
                }
            },
            plugins: {
                legend: {display: false}
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

        // Estado de impresoras (solo configuración)
        const printers = data.config.printers || {};

        // Asigna texto a un elemento (o '--' si no hay valor); el 0 es un valor válido (p. ej. 0 errores)
        const updateElement = (id, value) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = (value === undefined || value === null || value === '') ? '--' : value;
            }
        };

        // Cada impresora: indicador (habilitada/deshabilitada), nombre y puerto configurados (solo configuración)
        const updatePrinter = (type) => {
            const config = printers[type] || {};
            updatePrinterStatus(`${type}Status`, Boolean(config[`${type}_enabled`]));
            updateElement(`${type}Name`, config[`${type}_name`]);
            updateElement(`${type}Port`, config[`${type}_port`]);
        };

        // Configuración del servidor
        const serverConfig = data.config.server || {};
        const loggingConfig = data.config.logging || {};

        updatePrinter('matrix');
        updatePrinter('ticket');
        updatePrinter('fiscal');

        updateElement('serverMode', serverConfig.server_mode);
        updateElement('serverPort', serverConfig.server_port);
        updateElement('serverUrl', `${window.location.protocol}//${serverConfig.server_host}:${serverConfig.server_port}`);
        updateElement('logLevel', loggingConfig.log_level);
        updateElement('serverUptime', formatUptime(data.uptime));

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
        updateChart(data.stats?.requests_per_minute || []);

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

// Actualizar estado del servidor
function updateServerStatus(isRunning) {
    const element = document.getElementById('serverStatus');
    if (element) {
        element.className = `status-indicator me-2 ${isRunning ? 'active' : 'inactive'}`;
    }
}

// Formatear tiempo activo
function formatUptime(seconds) {
    // Sin dato: '--'; 0 segundos es válido (servidor recién iniciado) y se muestra como 0h 0m
    if (seconds === undefined || seconds === null) return '--';

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

// Actualizar gráfico: barras de peticiones por minuto (últimos 60 minutos) con la serie que entrega el servidor
function updateChart(series) {
    requestData.labels = series.map(item => item.minute);
    requestData.datasets[0].data = series.map(item => item.count);
    requestsChart.update();
}
