// Main Global JavaScript for OnionVision AI
document.addEventListener("DOMContentLoaded", () => {
    // Initialize tooltips if Bootstrap Tooltip is present
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map((tooltipTriggerEl) => new bootstrap.Tooltip(tooltipTriggerEl));
});
