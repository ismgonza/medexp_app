// tableSort.js

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

function makeTableSortable(table) {
    const tableId = table.id || `table-${Math.random().toString(36).substr(2, 9)}`;
    if (!table.id) table.id = tableId;

    const headers = table.querySelectorAll('th');
    const tableBody = table.querySelector('tbody');
    const rows = Array.from(tableBody.querySelectorAll('tr'));

    let directions = Array.from(headers).map(() => '');

    const sortColumn = (index) => {
        const direction = directions[index] || 'asc';
        const multiplier = (direction === 'asc') ? 1 : -1;
        const newRows = rows.sort((rowA, rowB) => {
            const cellA = rowA.querySelectorAll('td')[index].textContent.trim();
            const cellB = rowB.querySelectorAll('td')[index].textContent.trim();

            switch (true) {
                case cellA > cellB: return 1 * multiplier;
                case cellA < cellB: return -1 * multiplier;
                case cellA === cellB: return 0;
            }
        });

        [].forEach.call(rows, (row) => {
            tableBody.removeChild(row);
        });

        newRows.forEach(newRow => tableBody.appendChild(newRow));

        directions[index] = direction === 'asc' ? 'desc' : 'asc';

        headers.forEach(header => header.classList.remove('asc', 'desc'));
        headers[index].classList.add(direction === 'asc' ? 'desc' : 'asc');

        // Save sorting state to backend
        fetch('/user-preference/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: `key=${tableId}-sort&value=${JSON.stringify({index, direction: directions[index]})}`
        });
    };

    headers.forEach((header, index) => {
        header.addEventListener('click', () => {
            sortColumn(index);
        });
    });

    // Load saved sorting from backend
    fetch(`/user-preference/?key=${tableId}-sort`)
        .then(response => response.json())
        .then(data => {
            if (data.value) {
                const savedSort = JSON.parse(data.value);
                sortColumn(savedSort.index);
            }
        });
}

// Apply sorting to all tables on the page
document.addEventListener('DOMContentLoaded', () => {
    const tables = document.querySelectorAll('table');
    tables.forEach(table => makeTableSortable(table));
});