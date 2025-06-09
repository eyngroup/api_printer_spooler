let lastUpdate = null;

async function fetchStatus() {
    try {
        const response = await fetch('/api/status');
        if (!response.ok) throw new Error('Network response was not ok');
        return await response.json();
    } catch (error) {
        console.error('Error fetching status:', error);
        return null;
    }
}

function updateStatusBadge(status) {
    const badge = document.getElementById('serverStatus');
    badge.className = 'status-badge ' + (status === 'running' ? 'online' : 'offline');
    badge.querySelector('.text').textContent = status;
}

function updateServerInfo(data) {
    document.getElementById('startTime').textContent = data.start_time;
    document.getElementById('uptime').textContent = data.uptime;
    document.getElementById('printerMode').textContent = data.printer_mode;
    document.getElementById('currentHandler').textContent = data.current_handler;
}

function formatStatusValue(value) {
    if (typeof value === 'boolean') {
        return value ? 'Yes' : 'No';
    }
    return value;
}

function updatePrinterStatus(status) {
    const container = document.getElementById('statusDetails');
    container.innerHTML = '';

    if (typeof status === 'object' && status !== null) {
        Object.entries(status).forEach(([key, value]) => {
            if (typeof value === 'object' && value !== null) {
                // Crear una subsección para objetos anidados
                const section = document.createElement('div');
                section.className = 'status-section';
                section.innerHTML = `<h3>${key}</h3>`;
                
                Object.entries(value).forEach(([subKey, subValue]) => {
                    const item = document.createElement('div');
                    item.className = 'status-item';
                    item.innerHTML = `
                        <span class="key">${subKey}:</span>
                        <span class="value">${formatStatusValue(subValue)}</span>
                    `;
                    section.appendChild(item);
                });
                
                container.appendChild(section);
            } else {
                const item = document.createElement('div');
                item.className = 'status-item';
                item.innerHTML = `
                    <span class="key">${key}:</span>
                    <span class="value">${formatStatusValue(value)}</span>
                `;
                container.appendChild(item);
            }
        });
    } else {
        container.innerHTML = '<p>No status information available</p>';
    }
}

async function refreshStatus() {
    const data = await fetchStatus();
    if (data) {
        updateStatusBadge(data.server_status);
        updateServerInfo(data);
        updatePrinterStatus(data.printer_status);
        lastUpdate = new Date();
        
        // Actualizar tiempo de última actualización
        const footer = document.querySelector('footer p');
        footer.textContent = `Last updated: ${lastUpdate.toLocaleString()}`;
    } else {
        updateStatusBadge('offline');
    }
}

// Actualizar estado cada 30 segundos
setInterval(refreshStatus, 30000);

// Actualizar estado inicial
document.addEventListener('DOMContentLoaded', refreshStatus);
