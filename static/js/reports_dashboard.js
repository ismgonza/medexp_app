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
            const reportContainer = document.getElementById(`${reportType}_table`);
            if (reportContainer && reportContainer.dataset.reportType) {
                loadReportData(reportType);
            }
        });
    });

    // Load initial report data
    const initialReportContainer = document.querySelector('.tab-pane.active [data-report-type]');
    if (initialReportContainer) {
        loadReportData(initialReportContainer.dataset.reportType);
    }

    function loadReportData(reportType) {
        if (!reportType) {
            return;
        }
        
        const startDate = document.getElementById('start_date').value;
        const endDate = document.getElementById('end_date').value;
        const url = `?report_type=${reportType}&start_date=${startDate}&end_date=${endDate}`;
        fetch(url)
            .then(response => response.json())
            .then(data => {
                const tableContainer = document.getElementById(`${reportType}_table`);
                if (tableContainer) {
                    tableContainer.innerHTML = createTable(data, reportType);
                    addDetailClickListeners(reportType);
                }
            })
            .catch(error => {
                console.error('Error cargando los datos:', error);
            });
    }

    function createTable(data, reportType) {
        if (!data || data.length === 0) {
            return '<p>No existen datos disponibles para este reporte</p>';
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
                if (['Número de Procedimientos', 'Número de Pagos'].includes(header) && reportType !== 'patient_balances') {
                    html += `<td><a href="#" class="detail-link" data-id="${item[getIdKey(reportType)]}" data-type="${reportType}">${item[key]}</a></td>`;
                } else if (reportType === 'patient_balances' && header === 'Paciente') {
                    html += `<td><a href="/patients/${item.id}/">${item[key]}</a></td>`;
                } else if (header === 'Costo Total' || (reportType === 'patient_balances' && ['Total de Tratamientos Pendientes', 'Total de Pagos Pendientes', 'Total Pendiente', 'Saldo a Favor'].includes(header))) {
                    html += `<td>₡${parseFloat(item[key]).toFixed(2)}</td>`;
                } else {
                    html += `<td>${formatValue(item[key], header, reportType) || 'N/A'}</td>`;
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
                if (itemType !== 'patient_balances') {
                    loadDetailData(itemType, itemId);
                } else {
                    // Handle patient balance click differently, maybe navigate to patient detail page
                    window.location.href = `/patients/${itemId}/`;
                }
            });
        });
    }

    function loadDetailData(reportType, itemId, page = 1) {
        const startDate = document.getElementById('start_date').value;
        const endDate = document.getElementById('end_date').value;
        const url = '/reports/detail/';
        const data = new FormData();
        data.append('report_type', reportType);
        data.append('item_id', itemId);
        data.append('start_date', startDate);
        data.append('end_date', endDate);
        data.append('page', page);
    
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
            detailContainer.innerHTML = createDetailTable(data.results, reportType);
            detailContainer.innerHTML += createPagination(data.pagination, reportType, itemId);
            detailContainer.style.display = 'block';
            addPaginationListeners(reportType, itemId);
        })
        .catch(error => {
            console.error('Error cargando los datos:', error);
        });
    }
    
    function createPagination(pagination, reportType, itemId) {
        if (!pagination) {
            return '';
        }
    
        let html = '<nav aria-label="Page navigation"><ul class="pagination justify-content-center">';
    
        if (pagination.has_previous) {
            html += `<li class="page-item"><a class="page-link" href="#" data-page="${pagination.previous_page}" data-report-type="${reportType}" data-item-id="${itemId}">Previous</a></li>`;
        } else {
            html += '<li class="page-item disabled"><span class="page-link">Previous</span></li>';
        }
    
        for (let i = 1; i <= pagination.total_pages; i++) {
            if (i === pagination.current_page) {
                html += `<li class="page-item active"><span class="page-link">${i}</span></li>`;
            } else {
                html += `<li class="page-item"><a class="page-link" href="#" data-page="${i}" data-report-type="${reportType}" data-item-id="${itemId}">${i}</a></li>`;
            }
        }
    
        if (pagination.has_next) {
            html += `<li class="page-item"><a class="page-link" href="#" data-page="${pagination.next_page}" data-report-type="${reportType}" data-item-id="${itemId}">Next</a></li>`;
        } else {
            html += '<li class="page-item disabled"><span class="page-link">Next</span></li>';
        }
    
        html += '</ul></nav>';
        return html;
    }
    
    function addPaginationListeners(reportType, itemId) {
        const paginationLinks = document.querySelectorAll('.pagination .page-link');
        paginationLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                const page = this.dataset.page;
                loadDetailData(reportType, itemId, page);
            });
        });
    }

    function createDetailTable(data, reportType) {
        if (!data || data.length === 0) {
            return '<p>No hay datos disponibles para esta entrada.</p>';
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
            case 'patient_balances':
                return ['Paciente', 'Total de Tratamientos Pendientes', 'Total de Pagos Pendientes', 'Total Pendiente', 'Saldo a Favor'];
            default:
                return [];
        }
    }

    function formatValue(value, header, reportType) {
        if (reportType === 'patient_balances' && ['Total de Tratamientos Pendientes', 'Total de Pagos Pendientes', 'Total Pendiente', 'Saldo a Favor'].includes(header)) {
            return `₡${parseFloat(value).toFixed(2)}`;
        }
        return value;
    }

    function getKey(header, reportType) {
        if (reportType === 'patient_balances') {
            switch (header) {
                case 'Paciente': return 'patient_name';
                case 'Total de Tratamientos Pendientes': return 'total_procedures';
                case 'Total de Pagos Pendientes': return 'total_payments';
                case 'Total Pendiente': return 'calculated_balance';
                case 'Saldo a Favor': return 'amount_in_favor';
            }
        } else {
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
            case 'patient_balances':
                return 'id';  // Assuming we use the patient's ID
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