async function refreshDashboard(){

    const response =
        await fetch("/api/dashboard/summary");

    const data =
        await response.json();

    document.querySelector(
        "#submittedValue"
    ).textContent =
        data.submitted_squads;

    document.querySelector(
        "#pendingValue"
    ).textContent =
        data.pending_squads;

    document.querySelector(
        "#vaccinationValue"
    ).textContent =
        data.total_vaccinations;

    document.querySelector(
        "#entryValue"
    ).textContent =
        data.total_entries;

}

document.addEventListener(
    "DOMContentLoaded",
    refreshDashboard
);