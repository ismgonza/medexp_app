document.addEventListener("DOMContentLoaded", function() {
    const provinciaSelect = document.getElementById("provincia");
    const cantonSelect = document.getElementById("canton");
    const distritoSelect = document.getElementById("distrito");

    const currentProvince = document.getElementById("current_province").value;
    const currentCanton = document.getElementById("current_canton").value;
    const currentDistrict = document.getElementById("current_district").value;

    // Initialize selects
    provinciaSelect.innerHTML = '<option value="">Seleccione Provincia</option>';
    cantonSelect.innerHTML = '<option value="">Seleccione Cantón</option>';
    distritoSelect.innerHTML = '<option value="">Seleccione Distrito</option>';

    fetch("/static/js/cr_geo_distribution.json")
        .then(response => response.json())
        .then(geoData => {
            // Populate provincia select
            Object.keys(geoData).forEach(provincia => {
                const option = document.createElement("option");
                option.value = provincia;
                option.textContent = provincia;
                option.selected = (provincia === currentProvince);
                provinciaSelect.appendChild(option);
            });

            // If editing, populate canton and distrito
            if (currentProvince) {
                populateCanton(currentProvince);
                if (currentCanton) {
                    populateDistrito(currentProvince, currentCanton);
                }
            }

            // Event listener for provincia select
            provinciaSelect.addEventListener("change", function() {
                populateCanton(this.value);
            });

            // Event listener for canton select
            cantonSelect.addEventListener("change", function() {
                populateDistrito(provinciaSelect.value, this.value);
            });

            function populateCanton(selectedProvincia) {
                const cantones = geoData[selectedProvincia];
                cantonSelect.innerHTML = '<option value="">Seleccione Cantón</option>';
                distritoSelect.innerHTML = '<option value="">Seleccione Distrito</option>';

                if (cantones) {
                    Object.keys(cantones).forEach(canton => {
                        const option = document.createElement("option");
                        option.value = canton;
                        option.textContent = canton;
                        option.selected = (canton === currentCanton);
                        cantonSelect.appendChild(option);
                    });
                }
            }

            function populateDistrito(selectedProvincia, selectedCanton) {
                const distritos = geoData[selectedProvincia]?.[selectedCanton];
                distritoSelect.innerHTML = '<option value="">Seleccione Distrito</option>';

                if (distritos) {
                    distritos.forEach(distrito => {
                        const option = document.createElement("option");
                        option.value = distrito;
                        option.textContent = distrito;
                        option.selected = (distrito === currentDistrict);
                        distritoSelect.appendChild(option);
                    });
                }
            }
        })
        .catch(error => console.error('Error loading the JSON data:', error));
});