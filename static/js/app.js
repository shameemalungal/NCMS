document.addEventListener("DOMContentLoaded", () => {

    const toggle = document.querySelector("#sidebarToggle");
    const sidebar = document.querySelector(".sidebar");

    if (toggle && sidebar) {

        toggle.addEventListener("click", () => {

            sidebar.classList.toggle("show");

        });

    }

});