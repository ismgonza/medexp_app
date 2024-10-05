document.addEventListener('DOMContentLoaded', function() {
    const serviceSearch = document.getElementById('service_search');
    const serviceSearchResults = document.getElementById('service_search_results');
    const procedureTypeInput = document.getElementById('id_procedure_type');
    const inventoryItemInput = document.getElementById('id_inventory_item');
    const totalCostInput = document.getElementById('id_total_cost');
    const itemCountInput = document.getElementById('id_item_count');
    const discountInput = document.getElementById('id_discount');
    const unitPriceInput = document.getElementById('id_unit_price');

    let selectedItemPrice = 0;
    let selectedItemVariablePrice = false;
    let currentFocus = -1;

    function clearResults() {
        if (serviceSearchResults) {
            serviceSearchResults.innerHTML = '';
            serviceSearchResults.classList.remove('active');
        }
        currentFocus = -1;
    }

    function updateCosts() {
        const itemCount = itemCountInput && itemCountInput.value ? parseInt(itemCountInput.value) : 1;
        const discount = discountInput && discountInput.value ? parseFloat(discountInput.value) : 0;
        const unitPrice = unitPriceInput && unitPriceInput.value ? parseFloat(unitPriceInput.value) : selectedItemPrice;

        if (unitPrice) {
            const initialCost = unitPrice * itemCount;
            const totalCost = Math.max(initialCost - discount, 0).toFixed(2);
            if (totalCostInput) totalCostInput.value = totalCost;
        } else if (totalCostInput) {
            totalCostInput.value = '';
        }
    }

    function searchServices() {
        const query = serviceSearch.value;
        if (query.length >= 2) {
            fetch(`/procedures/service-search/?query=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    let results = '';
                    data.forEach((item, index) => {
                        results += `
                            <div class="search-item" data-index="${index}" data-id="${item.id}" data-name="${item.name}" data-price="${item.price}" data-variable-price="${item.variable_price}">
                                <span class="service-code">(${item.code})</span>
                                <span class="service-name">${item.name}</span>
                            </div>`;
                    });
                    if (serviceSearchResults) {
                        serviceSearchResults.innerHTML = results;
                        serviceSearchResults.classList.add('active');
                    }
                    currentFocus = -1;
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        } else {
            clearResults();
        }
    }

    function handleKeyDown(e) {
        const items = serviceSearchResults.getElementsByClassName('search-item');
        
        if (e.keyCode === 40) { // Down arrow
            e.preventDefault();
            currentFocus++;
            addActive(items);
        } else if (e.keyCode === 38) { // Up arrow
            e.preventDefault();
            currentFocus--;
            addActive(items);
        } else if (e.keyCode === 13) { // Enter
            e.preventDefault();
            if (currentFocus > -1) {
                if (items[currentFocus]) {
                    selectItem(items[currentFocus]);
                }
            } else {
                selectItem(items[0]);  // Select first item if none is focused
            }
        }
    }

    function addActive(items) {
        if (!items || items.length === 0) return;
        removeActive(items);
        if (currentFocus >= items.length) currentFocus = 0;
        if (currentFocus < 0) currentFocus = (items.length - 1);
        items[currentFocus].classList.add('active');
    }

    function removeActive(items) {
        for (let i = 0; i < items.length; i++) {
            items[i].classList.remove('active');
        }
    }

    if (serviceSearch) {
        serviceSearch.addEventListener('input', debounce(searchServices, 300));
        serviceSearch.addEventListener('keydown', handleKeyDown);
        serviceSearch.addEventListener('blur', function() {
            // Delay to allow click event on search results
            setTimeout(() => {
                const items = serviceSearchResults.getElementsByClassName('search-item');
                if (items.length > 0) {
                    selectItem(items[currentFocus > -1 ? currentFocus : 0]);
                }
            }, 200);
        });
    }

    if (serviceSearchResults) {
        serviceSearchResults.addEventListener('click', function(e) {
            if (e.target.closest('.search-item')) {
                selectItem(e.target.closest('.search-item'));
            }
        });
    }

    function selectItem(item) {
        if (!item) return;
        const id = item.getAttribute('data-id');
        const name = item.getAttribute('data-name');
        const price = parseFloat(item.getAttribute('data-price'));
        const variablePrice = item.getAttribute('data-variable-price') === 'true';

        if (serviceSearch) serviceSearch.value = name;
        if (procedureTypeInput) procedureTypeInput.value = name;
        if (inventoryItemInput) inventoryItemInput.value = id;
        selectedItemPrice = price;
        selectedItemVariablePrice = variablePrice;

        if (unitPriceInput) {
            unitPriceInput.value = price.toFixed(2);
            if (variablePrice) {
                unitPriceInput.removeAttribute('readonly');
            } else {
                unitPriceInput.setAttribute('readonly', 'readonly');
            }
        }

        clearResults();
        updateCosts();
    }

    if (itemCountInput) itemCountInput.addEventListener('input', updateCosts);
    if (discountInput) discountInput.addEventListener('input', updateCosts);
    if (unitPriceInput) {
        unitPriceInput.addEventListener('input', function() {
            selectedItemPrice = parseFloat(this.value) || 0;
            updateCosts();
        });
    }

    document.addEventListener('click', function(e) {
        if (serviceSearch && serviceSearchResults && 
            !serviceSearch.contains(e.target) && 
            !serviceSearchResults.contains(e.target)) {
            clearResults();
        }
    });

    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // New code for handling pre-filled values
    if (procedureTypeInput && procedureTypeInput.value) {
        if (serviceSearch) {
            serviceSearch.value = procedureTypeInput.value;
        }
    }

    if (inventoryItemInput && inventoryItemInput.value) {
        const inventoryItemId = inventoryItemInput.value;
        fetch(`/procedures/service-search/?query=${encodeURIComponent(inventoryItemId)}`)
            .then(response => response.json())
            .then(data => {
                if (data.length > 0) {
                    const item = data[0];
                    selectItem({
                        getAttribute: (attr) => {
                            switch(attr) {
                                case 'data-id': return item.id;
                                case 'data-name': return item.name;
                                case 'data-price': return item.price;
                                case 'data-variable-price': return item.variable_price;
                            }
                        }
                    });
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
    }

    // Initial setup
    if (unitPriceInput && inventoryItemInput.value) {
        // You might need to fetch the initial variable_price status from the server
        // For now, we'll assume it's not variable if it's preselected
        unitPriceInput.setAttribute('readonly', 'readonly');
    }

    updateCosts();
});