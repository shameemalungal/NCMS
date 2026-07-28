document.addEventListener("DOMContentLoaded", function () {

    const search = document.getElementById("campaignSearch");

    if (!search) return;

    search.addEventListener("keyup", function () {

        const filter = this.value.toLowerCase();

        const rows = document.querySelectorAll("#campaignTable tbody tr");

        rows.forEach(row => {

            const text = row.textContent.toLowerCase();

            row.style.display = text.includes(filter) ? "" : "none";

        });

    });

});