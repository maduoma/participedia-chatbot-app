// File: static/sidebar.js

document.addEventListener('DOMContentLoaded', function () {
    const toggleButton = document.getElementById('toggle-sidebar');
    const sidebarContent = document.getElementById('sidebar-content');
    const sidebar = document.getElementById('sidebar');

    toggleButton.addEventListener('click', function () {
        sidebar.classList.toggle('collapsed');
        sidebarContent.classList.toggle('collapsed');
    });
});
