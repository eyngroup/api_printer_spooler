// Estado global de la configuración
let currentConfig = null;
let originalConfig = null;

// Inicialización
document.addEventListener('DOMContentLoaded', function() {
    loadConfiguration();
    setupEventListeners();
});

// Cargar configuración
async function loadConfiguration() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        
        // Extraer la configuración del estado
        currentConfig = {
            server: data.config.server,
            proxy: data.config.proxy,
            printers: data.config.printers,
            logging: data.config.logging,
            security: data.config.security
        };
        
        originalConfig = JSON.parse(JSON.stringify(currentConfig));
        
        populateForm(currentConfig);
    } catch (error) {
        console.error('Error cargando configuración:', error);
        showNotification('Error', 'No se pudo cargar la configuración', 'error');
    }
}

// Poblar el formulario con los datos
function populateForm(config) {
    // Servidor
    if (config.server) {
        setFormValue('serverHost', config.server.server_host);
        setFormValue('serverPort', config.server.server_port);
        setFormValue('serverDebug', config.server.server_debug);
        setFormValue('serverMode', config.server.server_mode);
    }

    // Proxy
    if (config.proxy) {
        setFormValue('proxyEnabled', config.proxy.proxy_enabled);
        setFormValue('proxyTargetUrl', config.proxy.proxy_target);
    }

    // Impresoras
    if (config.printers) {
        // Ticket
        if (config.printers.ticket) {
            setFormValue('ticketEnabled', config.printers.ticket.ticket_enabled);
            setFormValue('ticketName', config.printers.ticket.ticket_name);
            setFormValue('ticketPrinterName', config.printers.ticket.ticket_port);
            setFormValue('ticketPaperSize', config.printers.ticket.ticket_paper);
            setFormValue('ticketTemplate', config.printers.ticket.ticket_template);
            setFormValue('ticketBarcodeEnabled', config.printers.ticket.barcode_enabled);
            setFormValue('ticketBarcodeType', config.printers.ticket.barcode_type);
            setFormValue('ticketLogoEnabled', config.printers.ticket.logo_enabled);
            setFormValue('ticketLogoWidth', config.printers.ticket.logo_width);
            setFormValue('ticketLogoHeight', config.printers.ticket.logo_height);
        }

        // Matrix
        if (config.printers.matrix) {
            setFormValue('matrixEnabled', config.printers.matrix.matrix_enabled);
            setFormValue('matrixName', config.printers.matrix.matrix_name);
            setFormValue('matrixPrinterName', config.printers.matrix.matrix_port);
            setFormValue('matrixDirectPrint', config.printers.matrix.matrix_direct);
            setFormValue('matrixOutputFile', config.printers.matrix.matrix_file);
            setFormValue('matrixPaperSize', config.printers.matrix.matrix_paper);
            setFormValue('matrixTemplate', config.printers.matrix.matrix_template);
            setFormValue('matrixUseEscp', config.printers.matrix.matrix_use_escp);
        }

        // Fiscal
        if (config.printers.fiscal) {
            setFormValue('fiscalEnabled', config.printers.fiscal.fiscal_enabled);
            setFormValue('fiscalName', config.printers.fiscal.fiscal_name);
            setFormValue('fiscalPort', config.printers.fiscal.fiscal_port);
            setFormValue('fiscalBaudrate', config.printers.fiscal.fiscal_baudrate);
            setFormValue('fiscalTimeout', config.printers.fiscal.fiscal_timeout);
        }
    }

    // Logging
    if (config.logging) {
        setFormValue('logOutput', config.logging.log_output);
        setFormValue('logLevel', config.logging.log_level);
        setFormValue('logFile', config.logging.log_file);
        setFormValue('logFormat', config.logging.log_format);
        setFormValue('logDays', config.logging.log_days);
    }

    // Security
    if (config.security) {
        setFormValue('securityCode', config.security.security_code);
    }
}

// Configurar event listeners
function setupEventListeners() {
    // Navegación de secciones
    document.querySelectorAll('.config-sections .list-group-item').forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Actualizar menú
            document.querySelectorAll('.config-sections .list-group-item').forEach(i => 
                i.classList.remove('active'));
            this.classList.add('active');
            
            // Ocultar todas las secciones
            document.querySelectorAll('.config-section').forEach(section => {
                section.style.display = 'none';
            });
            
            // Mostrar la sección seleccionada
            const sectionId = this.getAttribute('href').substring(1);
            const selectedSection = document.getElementById(sectionId);
            if (selectedSection) {
                selectedSection.style.display = 'block';
            }
        });
    });

    // Mostrar la primera sección por defecto
    const firstSection = document.querySelector('.config-sections .list-group-item');
    if (firstSection) {
        firstSection.click();
    }

    // Botones de acción
    document.getElementById('btnRestore').addEventListener('click', restoreValues);
    document.getElementById('btnPreview').addEventListener('click', showJsonPreview);
    document.getElementById('btnSave').addEventListener('click', saveConfiguration);

    // Detectar cambios en campos
    document.getElementById('configForm').addEventListener('change', function(e) {
        const input = e.target;
        markFieldAsModified(input);
        updateConfigValue(input);
    });
}

// Mostrar sección específica
function showSection(sectionId) {
    document.querySelectorAll('.config-section').forEach(section => {
        section.style.display = section.id === sectionId ? 'block' : 'none';
    });
}

// Marcar campo como modificado
function markFieldAsModified(input) {
    input.classList.add('field-modified');
}

// Actualizar valor en el objeto de configuración
function updateConfigValue(input) {
    const path = input.name.split('.');
    let current = currentConfig;
    
    for (let i = 0; i < path.length - 1; i++) {
        if (!current[path[i]]) {
            current[path[i]] = {};
        }
        current = current[path[i]];
    }
    
    const value = input.type === 'checkbox' ? input.checked : 
                  input.type === 'number' ? Number(input.value) : 
                  input.value;
                  
    current[path[path.length - 1]] = value;
}

// Restaurar valores originales
function restoreValues() {
    if (confirm('¿Estás seguro de que deseas restaurar todos los valores a su estado original?')) {
        currentConfig = JSON.parse(JSON.stringify(originalConfig));
        populateForm(currentConfig);
        document.querySelectorAll('.field-modified').forEach(field => {
            field.classList.remove('field-modified');
        });
    }
}

// Mostrar vista previa JSON
function showJsonPreview() {
    const jsonPreview = document.getElementById('jsonPreview');
    jsonPreview.textContent = JSON.stringify(currentConfig, null, 2);
    
    const modal = new bootstrap.Modal(document.getElementById('jsonPreviewModal'));
    modal.show();
}

// Guardar configuración
async function saveConfiguration() {
    try {
        const response = await fetch('/api/config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(currentConfig)
        });

        const data = await response.json();
        
        if (data.status === 'success') {
            showNotification('Éxito', 'Configuración guardada correctamente', 'success');
            
            // Actualizar estado original
            originalConfig = JSON.parse(JSON.stringify(currentConfig));
            
            // Actualizar UI
            document.querySelectorAll('.field-modified').forEach(field => {
                field.classList.remove('field-modified');
                field.classList.add('field-saved');
                setTimeout(() => field.classList.remove('field-saved'), 1000);
            });

            // Recargar la página después de 1 segundo para reflejar los cambios
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            throw new Error(data.message || 'Error desconocido al guardar la configuración');
        }
    } catch (error) {
        console.error('Error guardando configuración:', error);
        showNotification('Error', error.message || 'No se pudo guardar la configuración', 'error');
    }
}

// Utilidades
function setFormValue(id, value) {
    const element = document.getElementById(id);
    if (element) {
        if (element.type === 'checkbox') {
            element.checked = value;
        } else {
            element.value = value;
        }
    }
}

function showNotification(title, message, type = 'info') {
    const container = document.createElement('div');
    container.className = `alert alert-${type === 'error' ? 'danger' : 'success'} alert-dismissible fade show position-fixed top-0 end-0 m-3`;
    container.innerHTML = `
        <strong>${title}:</strong> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(container);
    setTimeout(() => container.remove(), 5000);
}
