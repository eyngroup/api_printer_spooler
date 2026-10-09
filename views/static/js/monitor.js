// Monitor fiscal (solo lectura): consulta GET /api/monitor una vez al cargar y al pulsar "Actualizar".
// Todo el DOM se construye con createElement/textContent: nunca se inserta texto del servidor como HTML.

const MONITOR_DRIFT_LIMIT_SECONDS = 120;
const MONITOR_DIVISA_CODES = ['20', '21', '22', '23', '24'];

// Formatea montos como Bs venezolanos: miles con "." y decimales con ","
function formatBs(value) {
    const number = Number(value);
    if (!isFinite(number)) return '--';
    const fixed = Math.abs(number).toFixed(2);
    const parts = fixed.split('.');
    const integer = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, '.');
    return (number < 0 ? '-' : '') + integer + ',' + parts[1];
}

// Crea un elemento con texto y clases opcionales
function el(tag, text, className) {
    const node = document.createElement(tag);
    if (text !== undefined && text !== null) node.textContent = String(text);
    if (className) node.className = className;
    return node;
}

// Agrega una celda a una fila
function addCell(row, text, className, tag) {
    const cell = el(tag || 'td', text, className);
    row.appendChild(cell);
    return cell;
}

// Tabla pequeña con encabezados
function buildTable(headers, numericFrom) {
    const table = el('table', null, 'table table-sm table-striped mb-0');
    const thead = el('thead');
    const row = el('tr');
    headers.forEach(function (h, i) {
        addCell(row, h, i >= numericFrom ? 'num' : '', 'th');
    });
    thead.appendChild(row);
    table.appendChild(thead);
    table.appendChild(el('tbody'));
    return table;
}

// Convierte "YYMMDD" a "DD/MM/20YY" y "HHMM" a "HH:MM"; devuelve el original si no encaja
function formatMachineDate(value) {
    const text = String(value || '');
    if (/^\d{6}$/.test(text)) return text.slice(4, 6) + '/' + text.slice(2, 4) + '/20' + text.slice(0, 2);
    return text || '--';
}

function formatMachineTime(value) {
    const text = String(value || '');
    if (/^\d{4}$/.test(text)) return text.slice(0, 2) + ':' + text.slice(2, 4);
    return text || '--';
}

// Lista de pares etiqueta/valor
function buildDefinitionList(pairs) {
    const dl = el('dl', null, 'row mb-0');
    pairs.forEach(function (pair) {
        dl.appendChild(el('dt', pair[0], 'col-6 col-md-5'));
        dl.appendChild(el('dd', pair[1], 'col-6 col-md-7'));
    });
    return dl;
}

function clearNode(node) {
    while (node.firstChild) node.removeChild(node.firstChild);
}

// Etiqueta de tasa para encabezados: usa el porcentaje de la máquina o "Tasa N"
function rateLabel(index, rates) {
    const rate = rates && rates[index - 1];
    if (rate && rate.percent !== undefined && rate.percent !== null) {
        return String(Number(rate.percent)).replace('.', ',') + '%';
    }
    return 'Tasa ' + index;
}

function renderPreZ(container, data) {
    clearNode(container);
    const counters = data.counters || {};
    const rates = (data.machine && data.machine.rates) || [];
    const preZ = data.pre_z || {};

    const summary = el('div', null, 'mb-3');
    summary.appendChild(el('span', 'Próximo Z: ', 'text-muted'));
    summary.appendChild(el('strong', counters.next_z !== undefined ? counters.next_z : '--'));
    summary.appendChild(el('span', '  |  Último Z: ', 'text-muted ms-3'));
    summary.appendChild(el('strong', formatMachineDate(counters.last_z_date) + ' ' + formatMachineTime(counters.last_z_time)));
    container.appendChild(summary);

    const headers = ['', 'Exento'];
    for (let i = 1; i <= 3; i++) {
        headers.push('Base ' + rateLabel(i, rates));
        headers.push('IVA ' + rateLabel(i, rates));
    }
    headers.push('Total');
    const table = buildTable(headers, 1);
    const body = table.querySelector('tbody');
    [['Ventas', preZ.sales], ['Notas de crédito', preZ.credit], ['Notas de débito', preZ.debit]].forEach(function (entry) {
        const block = entry[1] || {};
        const row = el('tr');
        addCell(row, entry[0], 'fw-semibold');
        addCell(row, formatBs(block.exento), 'num');
        for (let i = 1; i <= 3; i++) {
            const rate = (block.rates || []).find(function (r) { return r.rate_index === i; }) || {};
            addCell(row, formatBs(rate.base), 'num');
            addCell(row, formatBs(rate.tax), 'num');
        }
        addCell(row, formatBs(block.total), 'num fw-semibold');
        body.appendChild(row);
    });
    const wrapper = el('div', null, 'table-responsive');
    wrapper.appendChild(table);
    container.appendChild(wrapper);

    const net = el('div', null, 'alert alert-success d-flex justify-content-between align-items-center mt-3 mb-0');
    net.appendChild(el('span', 'Neto del día'));
    net.appendChild(el('span', 'Bs ' + formatBs(preZ.net_sales), 'net-total'));
    container.appendChild(net);
}

function describeDocument(doc) {
    if (!doc) return '--';
    if (typeof doc !== 'object') return String(doc);
    return '#' + (doc.number !== undefined ? doc.number : '--') + ' — ' +
        formatMachineDate(doc.date) + ' ' + formatMachineTime(doc.time);
}

function renderCounters(container, data) {
    clearNode(container);
    const c = data.counters || {};
    const today = c.today || {};
    container.appendChild(buildDefinitionList([
        ['Última factura', describeDocument(c.last_invoice)],
        ['Última nota de crédito', describeDocument(c.last_credit_note)],
        ['Última nota de débito', describeDocument(c.last_debit_note)],
        ['Último doc. no fiscal', describeDocument(c.last_non_fiscal)],
    ]));
    container.appendChild(el('h3', 'Documentos del día', 'h6 mt-3'));
    container.appendChild(buildDefinitionList([
        ['Facturas', today.invoices],
        ['Notas de crédito', today.credit_notes],
        ['Notas de débito', today.debit_notes],
        ['No fiscales', today.non_fiscal],
    ]));
    container.appendChild(el('h3', 'Cierres', 'h6 mt-3'));
    container.appendChild(buildDefinitionList([['Cierres Z realizados', c.z_closures]]));
}

function renderPayments(container, data) {
    clearNode(container);
    const payments = (data.payments || []).filter(function (p) { return Number(p.amount) > 0; });
    if (payments.length === 0) {
        container.appendChild(el('p', 'Sin pagos registrados hoy.', 'text-muted'));
    } else {
        const table = buildTable(['Medio de pago', 'Monto'], 1);
        const body = table.querySelector('tbody');
        payments.forEach(function (p) {
            const code = String(p.code);
            const row = el('tr');
            const cell = addCell(row, 'Código ' + code);
            if (p.divisa || MONITOR_DIVISA_CODES.indexOf(code) !== -1) {
                cell.appendChild(el('span', 'Divisa', 'badge bg-info text-dark ms-2'));
            }
            addCell(row, formatBs(p.amount), 'num');
            body.appendChild(row);
        });
        container.appendChild(table);
    }
    container.appendChild(buildDefinitionList([
        ['Total moneda nacional', formatBs(data.payments_total)],
        ['Total divisa', formatBs(data.divisa_total)],
    ]));
}

function renderMachine(container, data) {
    clearNode(container);
    const m = data.machine || {};
    const memory = m.audit_memory || {};
    const row = el('div', null, 'row g-3');
    const left = el('div', null, 'col-lg-6');
    const right = el('div', null, 'col-lg-6');

    left.appendChild(buildDefinitionList([
        ['Modelo', m.model],
        ['Serial', m.serial],
        ['País', m.country],
        ['Fecha/hora de la máquina', m.datetime],
        ['Documentos en auditoría', memory.documents],
    ]));

    const capacity = Number(memory.capacity_mb);
    const free = Number(memory.free_mb);
    if (capacity > 0 && isFinite(free)) {
        const used = Math.min(100, Math.max(0, ((capacity - free) / capacity) * 100));
        left.appendChild(el('div', 'Memoria de auditoría: ' + used.toFixed(1).replace('.', ',') +
            '% usada (' + free + ' MB libres de ' + capacity + ' MB)', 'mt-3 small'));
        const progress = el('div', null, 'progress');
        const bar = el('div', null, 'progress-bar' + (used >= 90 ? ' bg-danger' : used >= 75 ? ' bg-warning' : ''));
        bar.style.width = used.toFixed(1) + '%';
        bar.setAttribute('role', 'progressbar');
        bar.setAttribute('aria-valuenow', used.toFixed(1));
        bar.setAttribute('aria-valuemin', '0');
        bar.setAttribute('aria-valuemax', '100');
        progress.appendChild(bar);
        left.appendChild(progress);
    }

    right.appendChild(el('h3', 'Tasas', 'h6'));
    const rates = m.rates || [];
    if (rates.length) {
        const table = buildTable(['Nombre', 'Porcentaje', 'Tipo'], 1);
        const body = table.querySelector('tbody');
        rates.forEach(function (r) {
            const tr = el('tr');
            addCell(tr, r.name);
            addCell(tr, String(r.percent).replace('.', ',') + '%', 'num');
            addCell(tr, r.type, 'num');
            body.appendChild(tr);
        });
        right.appendChild(table);
    }
    right.appendChild(el('h3', 'Flags configurados', 'h6 mt-3'));
    const flags = m.flags || {};
    const flagKeys = Object.keys(flags).sort(function (a, b) { return Number(a) - Number(b); });
    const flagBox = el('div');
    flagKeys.forEach(function (key) {
        flagBox.appendChild(el('span', key + ' = ' + flags[key], 'badge bg-light text-dark border me-1 mb-1'));
    });
    right.appendChild(flagBox);

    row.appendChild(left);
    row.appendChild(right);
    container.appendChild(row);

    const drift = Number(m.time_drift_seconds);
    if (isFinite(drift) && Math.abs(drift) > MONITOR_DRIFT_LIMIT_SECONDS) {
        const minutes = Math.round(Math.abs(drift) / 60);
        container.appendChild(el('div', 'El reloj de la máquina difiere ' + minutes + ' min del servidor',
            'alert alert-warning mt-3 mb-0'));
    }
}

function showMonitorMessage(text, kind) {
    const box = document.getElementById('monitorMessage');
    clearNode(box);
    if (text) box.appendChild(el('div', text, 'alert alert-' + kind));
}

function renderMonitor(data) {
    const cards = document.getElementById('monitorCards');
    const badge = document.getElementById('monitorStaleBadge');
    const readAt = document.getElementById('monitorReadAt');

    if (data.read_at) {
        const date = new Date(data.read_at);
        readAt.textContent = isNaN(date.getTime()) ? String(data.read_at) : date.toLocaleString('es-VE');
    }

    if (data.available === false) {
        cards.classList.add('d-none');
        badge.classList.add('d-none');
        showMonitorMessage(data.reason || 'El monitor fiscal no está disponible.', 'info');
        return;
    }

    if (data.stale) {
        badge.textContent = data.error ? 'Desactualizado' : 'Datos en caché';
        badge.classList.remove('d-none');
    } else {
        badge.classList.add('d-none');
    }
    // Motivo/error informativo cuando los datos no son recientes
    showMonitorMessage(data.stale ? (data.reason || data.error || '') : '', 'warning');

    renderPreZ(document.getElementById('monitorPreZ'), data);
    renderCounters(document.getElementById('monitorCounters'), data);
    renderPayments(document.getElementById('monitorPayments'), data);
    renderMachine(document.getElementById('monitorMachine'), data);
    cards.classList.remove('d-none');
}

// Solo GET: es una lectura de la máquina, no una acción sobre la impresora
async function loadMonitor(refresh) {
    const button = document.getElementById('monitorRefresh');
    button.disabled = true;
    try {
        const response = await fetch('/api/monitor' + (refresh ? '?refresh=1' : ''));
        const data = await response.json();
        renderMonitor(data);
    } catch (error) {
        console.error('Error al cargar el monitor fiscal:', error);
        showMonitorMessage('No se pudo consultar el monitor fiscal.', 'danger');
    } finally {
        button.disabled = false;
    }
}

document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('monitorRefresh').addEventListener('click', function () { loadMonitor(true); });
    loadMonitor(false);
});
