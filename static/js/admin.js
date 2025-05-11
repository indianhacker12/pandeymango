// Admin Panel JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize all popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Sales Chart initialization
    var salesChartCanvas = document.getElementById('salesChart');
    if (salesChartCanvas) {
        var ctx = salesChartCanvas.getContext('2d');
        var salesChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                datasets: [{
                    label: 'Sales this year',
                    data: [12, 19, 10, 15, 22, 30, 28, 33, 25, 17, 19, 23],
                    backgroundColor: 'rgba(25, 135, 84, 0.2)',
                    borderColor: '#198754',
                    tension: 0.4,
                    borderWidth: 2,
                    pointBackgroundColor: '#fff',
                    pointBorderColor: '#198754',
                    pointRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            borderDash: [3, 3]
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }

    // Product Categories Chart initialization
    var categoryChartCanvas = document.getElementById('categoryChart');
    if (categoryChartCanvas) {
        var ctx = categoryChartCanvas.getContext('2d');
        var categoryChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Alphonso', 'Kesar', 'Langra', 'Hapus', 'Payri', 'Rajapuri'],
                datasets: [{
                    data: [30, 25, 15, 18, 12, 10],
                    backgroundColor: [
                        '#198754',
                        '#0d6efd',
                        '#ffc107',
                        '#0dcaf0',
                        '#dc3545',
                        '#6c757d'
                    ],
                    hoverOffset: 4,
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    // Function to confirm deletion
    window.confirmDelete = function(formId) {
        if (confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
            document.getElementById(formId).submit();
        }
    };

    // Function to preview image before upload
    const imagePreview = document.getElementById('imagePreview');
    const imageUpload = document.getElementById('image');
    
    if (imageUpload && imagePreview) {
        imageUpload.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    imagePreview.src = e.target.result;
                    imagePreview.style.display = 'block';
                }
                reader.readAsDataURL(file);
            }
        });
    }

    // Status update handler
    const statusSelects = document.querySelectorAll('.status-select');
    statusSelects.forEach(select => {
        select.addEventListener('change', function() {
            const form = this.closest('form');
            if (form) {
                form.submit();
            }
        });
    });

    // User role update handler
    const roleSelects = document.querySelectorAll('.role-select');
    roleSelects.forEach(select => {
        select.addEventListener('change', function() {
            const form = this.closest('form');
            if (form) {
                form.submit();
            }
        });
    });
}); 