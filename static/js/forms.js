/* ==========================================================
   NCMS UI Design System
   forms.js
   ========================================================== */

document.addEventListener("DOMContentLoaded", () => {

    const total = document.getElementById("total_animals");
    const vaccinated = document.getElementById("vaccinated");
    const entries = document.getElementById("entries");

    const vaccinationPercentage =
        document.getElementById("vaccination_percentage");

    const entryPercentage =
        document.getElementById("entry_percentage");

    const difference =
        document.getElementById("difference");

    function numberValue(element) {

        if (!element) return 0;

        return parseFloat(element.value) || 0;

    }

    function calculate() {

        const totalAnimals = numberValue(total);
        const vaccinatedAnimals = numberValue(vaccinated);
        const pashudhanEntries = numberValue(entries);

        if (totalAnimals > 0) {

            vaccinationPercentage.value =
                ((vaccinatedAnimals / totalAnimals) * 100).toFixed(2) + "%";

            entryPercentage.value =
                ((pashudhanEntries / totalAnimals) * 100).toFixed(2) + "%";

        } else {

            vaccinationPercentage.value = "";
            entryPercentage.value = "";

        }

        difference.value =
            vaccinatedAnimals - pashudhanEntries;

        validate();

    }

    function validate() {

        clearValidation();

        if (numberValue(vaccinated) > numberValue(total)) {

            showError(vaccinated,
                "Vaccinated animals cannot exceed total animals.");

        }

        if (numberValue(entries) > numberValue(vaccinated)) {

            showError(entries,
                "Pashudhan entries cannot exceed vaccinated animals.");

        }

    }

    function clearValidation() {

        document
            .querySelectorAll(".is-invalid")
            .forEach(e => e.classList.remove("is-invalid"));

    }

    function showError(element, message) {

        element.classList.add("is-invalid");

        element.setCustomValidity(message);

    }

    [total, vaccinated, entries].forEach(field => {

        if (field) {

            field.addEventListener("input", calculate);

        }

    });

    calculate();

});