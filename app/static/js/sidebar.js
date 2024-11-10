// sidebar.js

document.addEventListener("DOMContentLoaded", function () {
    const sidebar = document.querySelector(".sidebar");
    const toggleButton = document.querySelector(".sidebar-toggle");

    toggleButton.addEventListener("click", function () {
        sidebar.classList.toggle("collapsed");
        document.querySelector(".main-content").classList.toggle("collapsed");
    });
});
