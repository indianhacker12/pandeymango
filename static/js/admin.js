/**
 * Mango Delight Admin Dashboard JavaScript
 */

// DOM elements
const dashboardElements = {
    totalOrders: document.getElementById('total-orders'),
    totalRevenue: document.getElementById('total-revenue'),
    totalBookings: document.getElementById('total-bookings'),
    totalCustomers: document.getElementById('total-customers'),
    updateTime: document.getElementById('update-time'),
    pendingBadges: document.querySelectorAll('.pending-badge'),
    notificationToast: document.getElementById('notificationToast')
};

// Fetch dashboard stats via AJAX
async function fetchDashboardStats() {
    try {
        const response = await fetch('/api/dashboard/stats');
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        
        const data = await response.json();
        if (data.success) {
            updateDashboardUI(data.data);
        } else {
            console.error('Error fetching dashboard stats:', data.error);
        }
    } catch (error) {
        console.error('Error fetching dashboard stats:', error);
    }
}

// Update dashboard UI with new data
function updateDashboardUI(data) {
    // Update the stats if elements exist
    if (dashboardElements.totalOrders) {
        dashboardElements.totalOrders.textContent = data.total_orders;
    }
    
    if (dashboardElements.totalRevenue) {
        dashboardElements.totalRevenue.textContent = '₹' + data.total_revenue;
    }
    
    if (dashboardElements.totalBookings) {
        dashboardElements.totalBookings.textContent = data.total_bookings;
    }
    
    if (dashboardElements.totalCustomers) {
        dashboardElements.totalCustomers.textContent = data.total_customers;
    }
    
    // Update timestamp
    if (dashboardElements.updateTime) {
        dashboardElements.updateTime.textContent = data.timestamp;
    }
    
    // Check for new pending bookings
    const oldPendingCount = parseInt(localStorage.getItem('pendingBookingsCount') || '0');
    if (data.pending_bookings > oldPendingCount) {
        showNotification(`${data.pending_bookings - oldPendingCount} नई बुकिंग प्राप्त हुई!`, 'primary');
    }
    
    // Update pending bookings count in localStorage
    localStorage.setItem('pendingBookingsCount', data.pending_bookings);
    
    // Update any pending badges
    dashboardElements.pendingBadges.forEach(badge => {
        badge.textContent = data.pending_bookings;
        badge.style.display = data.pending_bookings > 0 ? 'inline-block' : 'none';
    });
}

// Show notification toast
function showNotification(message, type = 'primary') {
    // Check if notification element exists
    const notificationToast = document.getElementById('notificationToast');
    if (!notificationToast) return;
    
    const toast = new bootstrap.Toast(notificationToast);
    
    // Set the message
    const notificationMessage = document.getElementById('notification-message');
    if (notificationMessage) {
        notificationMessage.innerText = message;
    }
    
    // Set the time
    const notificationTime = document.getElementById('notification-time');
    if (notificationTime) {
        notificationTime.innerText = new Date().toLocaleTimeString('hi-IN');
    }
    
    // Update the header color based on type
    const header = notificationToast.querySelector('.toast-header');
    if (header) {
        header.className = 'toast-header bg-' + type + ' text-white';
    }
    
    // Show the toast
    toast.show();
}

// Function to update booking status via AJAX
async function updateBookingStatus(bookingId, status) {
    try {
        const response = await fetch(`/api/booking/${bookingId}/status`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ status })
        });
        
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        
        const data = await response.json();
        if (data.success) {
            return data.data;
        } else {
            console.error('Error updating booking status:', data.error);
            return null;
        }
    } catch (error) {
        console.error('Error updating booking status:', error);
        return null;
    }
}

// Add event listeners when document is ready
document.addEventListener('DOMContentLoaded', function() {
    // Set up click handlers for confirm booking buttons
    document.querySelectorAll('.confirm-booking').forEach(button => {
        button.addEventListener('click', async function() {
            const bookingId = this.getAttribute('data-id');
            const result = await updateBookingStatus(bookingId, 'confirmed');
            
            if (result) {
                // Show success notification
                showNotification(`बुकिंग #${bookingId} सफलतापूर्वक कन्फर्म की गई!`, 'success');
                
                // Update UI
                const row = this.closest('tr');
                const statusCell = row.querySelector('td:nth-child(7)');
                if (statusCell) {
                    statusCell.innerHTML = '<span class="badge bg-primary">confirmed</span>';
                }
                
                // Remove the confirm button
                this.remove();
            } else {
                showNotification('बुकिंग अपडेट करने में त्रुटि हुई!', 'danger');
            }
        });
    });
    
    // Set up click handlers for mark delivered buttons
    document.querySelectorAll('.mark-delivered').forEach(button => {
        button.addEventListener('click', async function() {
            const bookingId = this.getAttribute('data-id');
            const result = await updateBookingStatus(bookingId, 'delivered');
            
            if (result) {
                // Show success notification
                showNotification(`बुकिंग #${bookingId} डिलीवर्ड के रूप में मार्क की गई!`, 'success');
                
                // Update UI
                const row = this.closest('tr');
                const statusCell = row.querySelector('td:nth-child(7)');
                if (statusCell) {
                    statusCell.innerHTML = '<span class="badge bg-success">delivered</span>';
                }
                
                // Remove the mark as delivered button
                this.remove();
            } else {
                showNotification('बुकिंग अपडेट करने में त्रुटि हुई!', 'danger');
            }
        });
    });
    
    // Manual refresh button
    const refreshButton = document.querySelector('a[onclick="refreshData(); return false;"]');
    if (refreshButton) {
        refreshButton.addEventListener('click', function(e) {
            e.preventDefault();
            fetchDashboardStats();
        });
    }
    
    // Show welcome notification on page load
    setTimeout(() => {
        showNotification('स्वागत है, एडमिन! आपका डैशबोर्ड तैयार है।', 'primary');
    }, 1000);
    
    // Initialize periodic refresh (every 30 seconds)
    setInterval(fetchDashboardStats, 30000);
    
    // Store initial pending bookings count
    const pendingCountElem = document.querySelector('.badge-pending-count');
    if (pendingCountElem) {
        localStorage.setItem('pendingBookingsCount', pendingCountElem.textContent);
    }
});

// Expose global function for manual refresh
window.refreshData = fetchDashboardStats;

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