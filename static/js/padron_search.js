// static/js/padron_search.js

document.addEventListener('DOMContentLoaded', function() {
    const idNumberInput = document.getElementById('id_id_number');
    const firstNameInput = document.getElementById('id_first_name');
    const lastName1Input = document.getElementById('id_last_name1');
    const lastName2Input = document.getElementById('id_last_name2');

    idNumberInput.addEventListener('blur', function() {
        const idNumber = this.value.trim();
        if (idNumber) {
            searchPadron(idNumber);
        }
    });

    function searchPadron(idNumber) {
        fetch(`/patients/search-padron/${idNumber}/`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.error) {
                    throw new Error(data.error);
                }
                if (data.found) {
                    firstNameInput.value = data.first_name;
                    lastName1Input.value = data.lastname1;
                    lastName2Input.value = data.lastname2;
                    showMessage('Datos encontrados y completados.', 'success');
                } else {
                    showMessage('No se encontró un registro coincidente. Por Favor los datos manualmente.', 'info');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showMessage(`Error: ${error.message}`, 'danger');
            });
    }

    function showMessage(message, type) {
        const messageDiv = document.getElementById('message');
        if (!messageDiv) {
            const formElement = document.querySelector('form');
            const newMessageDiv = document.createElement('div');
            newMessageDiv.id = 'message';
            formElement.insertBefore(newMessageDiv, formElement.firstChild);
        }
        const messageElement = document.getElementById('message');
        messageElement.textContent = message;
        messageElement.className = `alert alert-${type}`;
        messageElement.style.display = 'block';
        messageElement.style.opacity = '1';
    
        // Set a timeout to fade out the message after 5 seconds
        setTimeout(() => {
            messageElement.classList.add('fade-out');
            setTimeout(() => {
                messageElement.style.display = 'none';
                messageElement.classList.remove('fade-out');
            }, 1000);
        }, 2000);
    }
});