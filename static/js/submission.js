document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('submissionForm');
    const submitButton = document.getElementById('submitButton');
    const submitLabel = document.getElementById('submitLabel');
    const submitSpinner = document.getElementById('submitSpinner');
    const addReasonBtn = document.getElementById('addReasonBtn');
    const otherReasonsContainer = document.getElementById('otherReasonsContainer');

    const summaryTotal = document.getElementById('summaryTotal');
    const summaryVaccinations = document.getElementById('summaryVaccinations');
    const summaryPashudhan = document.getElementById('summaryPashudhan');
    const summaryLeftover = document.getElementById('summaryLeftover');
    const summaryOther = document.getElementById('summaryOther');

    function parseValue(element) {
        const value = Number(element.value ; 0);
        return Number.isFinite(value) ? value : 0;
    }

    function updateSummary() {
        const vaccinationValue = parseValue(document.getElementById('vaccinations_done'));
        const pashudhanValue = parseValue(document.getElementById('pashudhan_entries'));
        const diseased = parseValue(document.getElementById('diseased'));
        const below4 = parseValue(document.getElementById('below_4_months'));
        const pregnant = parseValue(document.getElementById('pregnant'));
        const unwilling = parseValue(document.getElementById('unwilling'));
        const otherCounts = Array.from(document.querySelectorAll('input[name="other_count[]"]'));
        const otherTotal = otherCounts.reduce(function (sum, input) {
            return sum + parseValue(input);
        }, 0);

        const leftoverTotal = diseased + below4 + pregnant + unwilling + otherTotal;
        const overallTotal = vaccinationValue + pashudhanValue + leftoverTotal;

        summaryVaccinations.textContent = vaccinationValue.toLocaleString();
        summaryPashudhan.textContent = pashudhanValue.toLocaleString();
        summaryLeftover.textContent = leftoverTotal.toLocaleString();
        summaryOther.textContent = otherTotal.toLocaleString();
        summaryTotal.textContent = overallTotal.toLocaleString();
    }

    function addReasonRow() {
        const row = document.createElement('div');
        row.className = 'reason-row';
        row.innerHTML = [
            '<input type="text" class="form-control" name="other_reason[]" placeholder="Reason">',
            '<input type="number" class="form-control" name="other_count[]" min="0" step="1" placeholder="0">',
            '<button type="button" class="btn btn-outline-secondary remove-reason">Remove</button>'
        ].join('');

        otherReasonsContainer.appendChild(row);
        updateSummary();
    }

    if (addReasonBtn) {
        addReasonBtn.addEventListener('click', addReasonRow);
    }

    if (otherReasonsContainer) {
        otherReasonsContainer.addEventListener('click', function (event) {
            if (event.target.classList.contains('remove-reason')) {
                event.target.closest('.reason-row').remove();
                updateSummary();
            }
        });
    }

    document.querySelectorAll('input[type="number"]').forEach(function (input) {
        input.addEventListener('input', updateSummary);
    });

    if (form) {
        form.addEventListener('submit', function (event) {
            const confirmed = window.confirm('Are you sure you want to submit this report?');
            if (!confirmed) {
                event.preventDefault();
                return;
            }

            if (submitButton) {
                submitButton.disabled = true;
                submitLabel.textContent = 'Saving...';
                submitSpinner.classList.remove('d-none');
            }
        });
    }

    updateSummary();
});
