document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('dateRangeForm');
    const tabInput = document.getElementById('tab');

    // Update hidden tab input when form is submitted
    form.addEventListener('submit', function(e) {
        const activeTab = document.querySelector('.nav-link.active');
        if (activeTab) {
            tabInput.value = activeTab.id.replace('-tab', '');
        }
    });

    // Load report data when tab is changed
    document.querySelectorAll('.nav-link').forEach(tab => {
        tab.addEventListener('click', function() {
            const reportType = this.id.replace('-tab', '');
            loadReportData(reportType);
        });
    });

    // Load initial report data
    const initialReportType = document.querySelector('.tab-pane.active [data-report-type]').dataset.reportType;
    loadReportData(initialReportType);

    function loadReportData(reportType) {
        const startDate = document.getElementById('start_date').value;
        const endDate = document.getElementById('end_date').value;
        const url = `?report_type=${reportType}&start_date=${startDate}&end_date=${endDate}`;
        fetch(url)
            .then(response => response.json())
            .then(data => {
                const tableContainer = document.getElementById(`${reportType}_table`);
                tableContainer.innerHTML = createTable(data, reportType);
                addDetailClickListeners(reportType);
            })
            .catch(error => {
                console.error('Error loading report data:', error);
            });
    }

    function createTable(data, reportType) {
        if (!data || data.length === 0) {
            return '<p>No data available for this report.</p>';
        }
    
        let html = '<table class="table"><thead><tr>';
        const headers = getHeaders(reportType);
        headers.forEach(header => {
            html += `<th>${header}</th>`;
        });
        html += '</tr></thead><tbody>';
        data.forEach(item => {
            html += '<tr>';
            headers.forEach(header => {
                const key = getKey(header, reportType);
                if (header === 'Número de Procedimientos') {
                    html += `<td><a href="#" class="detail-link" data-id="${item[getIdKey(reportType)]}" data-type="${reportType}">${item[key]}</a></td>`;
                } else if (header === 'Costo Total') {
                    html += `<td>₡${parseFloat(item[key]).toFixed(2)}</td>`;
                } else {
                    html += `<td>${item[key] || 'N/A'}</td>`;
                }
            });
            html += '</tr>';
        });
        html += '</tbody></table>';
        html += `<div id="${reportType}_detail" class="mt-4" style="display: none;"></div>`;
        return html;
    }

    function addDetailClickListeners(reportType) {
        document.querySelectorAll('.detail-link').forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                const itemId = this.dataset.id;
                const itemType = this.dataset.type;
                loadDetailData(itemType, itemId);
            });
        });
    }

    function loadDetailData(reportType, itemId) {
        const startDate = document.getElementById('start_date').value;
        const endDate = document.getElementById('end_date').value;
        const url = '/reports/detail/';
        const data = new FormData();
        data.append('report_type', reportType);
        data.append('item_id', itemId);
        data.append('start_date', startDate);
        data.append('end_date', endDate);

        fetch(url, {
            method: 'POST',
            body: data,
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            const detailContainer = document.getElementById(`${reportType}_detail`);
            detailContainer.innerHTML = createDetailTable(data, reportType);
            detailContainer.style.display = 'block';
        })
        .catch(error => {
            console.error('Error loading detail data:', error);
        });
    }

    function createDetailTable(data, reportType) {
        if (!data || data.length === 0) {
            return '<p>No detailed data available for this item.</p>';
        }
    
        let html = `<h4>${getDetailTitle(reportType, data[0])}</h4>`;
        html += '<table class="table"><thead><tr>';
        const headers = getDetailHeaders(reportType);
        headers.forEach(header => {
            html += `<th>${header}</th>`;
        });
        html += '</tr></thead><tbody>';
        data.forEach(item => {
            html += '<tr>';
            headers.forEach(header => {
                const key = getDetailKey(header, reportType);
                if (key && item.hasOwnProperty(key)) {
                    if (header === 'Paciente') {
                        html += `<td><a href="/patients/${item.patient__id}/">${item[key]}</a></td>`;
                    } else if (header === 'Tipo de Procedimiento' && reportType === 'payments_by_payment_method' && item.procedure_id) {
                        html += `<td><a href="/procedures/${item.procedure_id}/">${item[key]}</a></td>`;
                    } else if (header === 'Tipo de Procedimiento' && item.id) {
                        html += `<td><a href="/procedures/${item.id}/" class="procedure-link">${item[key]}</a></td>`;
                    } else {
                        html += `<td>${item[key]}</td>`;
                    }
                } else {
                    html += '<td>N/A</td>';
                }
            });
            html += '</tr>';
        });
        html += '</tbody></table>';
        return html;
    }

    function getHeaders(reportType) {
        switch (reportType) {
            case 'procedures_by_location':
                return ['Ubicación', 'Número de Procedimientos', 'Costo Total'];
            case 'procedures_by_signed_by':
                return ['Firmante', 'Número de Procedimientos'];
            case 'procedures_by_inventory_item':
                return ['Artículo de Inventario', 'Número de Procedimientos'];
            case 'procedures_by_status':
                return ['Estado', 'Número de Procedimientos'];
            case 'payments_by_payment_method':
                return ['Método de Pago', 'Número de Pagos'];
            case 'procedures_by_payment_status':
                return ['Estado de Pago', 'Número de Procedimientos'];
            default:
                return [];
        }
    }

    function getKey(header, reportType) {
        switch (header) {
            case 'Ubicación':
                return 'location__name';
            case 'Número de Procedimientos':
                return 'count';
            case 'Costo Total':
                return 'total_cost_sum';
            case 'Firmante':
                return 'signed_by__username';
            case 'Artículo de Inventario':
                return 'inventory_item__name';
            case 'Estado':
                return 'status';
            case 'Método de Pago':
                return 'payment_method';
            case 'Estado de Pago':
                return 'payment_status';
            case 'Número de Procedimientos':
            case 'Número de Pacientes':
            case 'Número de Pagos':
                return 'count';
            default:
                return '';
        }
    }

    function getIdKey(reportType) {
        switch (reportType) {
            case 'procedures_by_location':
                return 'location__id';
            case 'procedures_by_signed_by':
                return 'signed_by__id';
            case 'procedures_by_inventory_item':
                return 'inventory_item__id';
            case 'procedures_by_status':
                return 'status';
            case 'payments_by_payment_method':
                return 'payment_method';
            case 'procedures_by_payment_status':
                return 'payment_status';
            default:
                return '';
        }
    }

    function getDetailHeaders(reportType) {
        switch (reportType) {
            case 'procedures_by_location':
            case 'procedures_by_signed_by':
            case 'procedures_by_inventory_item':
            case 'procedures_by_status':
            case 'procedures_by_payment_status':
                return ['Fecha', 'Paciente', 'Tipo de Procedimiento', 'Estado', 'Estado de Pago', 'Costo Total'];
            case 'payments_by_payment_method':
                return ['Fecha', 'Paciente', 'Monto', 'Método de Pago', 'Tipo de Procedimiento'];
            default:
                return [];
        }
    }

    function getDetailKey(header, reportType) {
        switch (header) {
            case 'Fecha':
                return reportType === 'payments_by_payment_method' ? 'payment_date' : 'procedure_date';
            case 'Paciente':
            case 'Nombre del Paciente':
                return 'patient_name';
            case 'Tipo de Procedimiento':
                return 'procedure_type';
            case 'Estado':
                return 'status';
            case 'Estado de Pago':
                return 'payment_status';
            case 'Costo Total':
                return 'total_cost';
            case 'Monto':
                return 'amount';
            case 'Método de Pago':
                return 'payment_method';
            default:
                return '';
        }
    }

    function getDetailTitle(reportType, firstItem) {
        switch (reportType) {
            case 'procedures_by_location':
                return `Procedimientos en ${firstItem.location__name}`;
            case 'procedures_by_signed_by':
                return `Procedimientos firmados por ${firstItem.signed_by__username}`;
            case 'procedures_by_inventory_item':
                return `Procedimientos que usan ${firstItem.inventory_item__name}`;
            case 'procedures_by_status':
                return `Procedimientos con estado ${firstItem.status}`;
            case 'payments_by_payment_method':
                return `Pagos con método ${firstItem.payment_method}`;
            case 'procedures_by_payment_status':
                return `Procedimientos con estado de pago ${firstItem.payment_status}`;
            default:
                return 'Detalles del Reporte';
        }
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});