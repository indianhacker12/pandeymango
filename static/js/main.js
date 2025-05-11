// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize Bootstrap popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-hide flash messages after 5 seconds
    setTimeout(function() {
        var flashMessages = document.querySelectorAll('.alert');
        flashMessages.forEach(function(message) {
            var alert = new bootstrap.Alert(message);
            alert.close();
        });
    }, 5000);

    // Product quantity increment/decrement buttons
    const quantityInputs = document.querySelectorAll('.quantity-input');
    
    if (quantityInputs) {
        quantityInputs.forEach(input => {
            const decrementBtn = input.previousElementSibling;
            const incrementBtn = input.nextElementSibling;
            
            if (decrementBtn) {
                decrementBtn.addEventListener('click', () => {
                    if (input.value > 1) {
                        input.value = parseInt(input.value) - 1;
                    }
                });
            }
            
            if (incrementBtn) {
                incrementBtn.addEventListener('click', () => {
                    const maxStock = input.getAttribute('data-max-stock');
                    if (!maxStock || parseInt(input.value) < parseInt(maxStock)) {
                        input.value = parseInt(input.value) + 1;
                    }
                });
            }
        });
    }

    // Product image gallery (for product detail page)
    const mainImage = document.getElementById('main-product-image');
    const thumbnails = document.querySelectorAll('.product-thumbnail');
    
    if (mainImage && thumbnails.length > 0) {
        thumbnails.forEach(thumbnail => {
            thumbnail.addEventListener('click', function() {
                // Update main image src
                mainImage.src = this.src;
                
                // Remove active class from all thumbnails
                thumbnails.forEach(thumb => thumb.classList.remove('active'));
                
                // Add active class to clicked thumbnail
                this.classList.add('active');
            });
        });
    }

    // Newsletter form validation
    const newsletterForm = document.querySelector('.newsletter-form');
    
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const emailInput = this.querySelector('input[type="email"]');
            const email = emailInput.value.trim();
            
            if (!email || !isValidEmail(email)) {
                showFormError(emailInput, 'Please enter a valid email address');
                return;
            }
            
            // If validation passes, you would typically submit the form via AJAX
            // For now, just show a success message
            this.innerHTML = '<div class="alert alert-success">Thank you for subscribing to our newsletter!</div>';
        });
    }

    // Helper function to validate email
    function isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    // Helper function to show form errors
    function showFormError(inputElement, message) {
        // Remove any existing error message
        const existingError = inputElement.nextElementSibling;
        if (existingError && existingError.classList.contains('invalid-feedback')) {
            existingError.remove();
        }
        
        // Add error class to input
        inputElement.classList.add('is-invalid');
        
        // Create and append error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback';
        errorDiv.textContent = message;
        inputElement.parentNode.appendChild(errorDiv);
        
        // Focus the input
        inputElement.focus();
    }
}); 