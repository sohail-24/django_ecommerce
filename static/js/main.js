/**
 * Django E-commerce - Main JavaScript
 * Client-side functionality for the clothing e-commerce platform
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize all popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const closeButton = alert.querySelector('.btn-close');
            if (closeButton) {
                closeButton.click();
            }
        }, 5000);
    });

    // Quantity input handlers
    initQuantityInputs();

    // Product image gallery
    initProductGallery();

    // Form validation
    initFormValidation();
});

/**
 * Initialize quantity input handlers
 */
function initQuantityInputs() {
    const quantityInputs = document.querySelectorAll('.quantity-input');
    
    quantityInputs.forEach(function(input) {
        // Handle increment/decrement buttons
        const decrementBtn = input.parentElement.querySelector('.btn-decrement');
        const incrementBtn = input.parentElement.querySelector('.btn-increment');
        
        if (decrementBtn) {
            decrementBtn.addEventListener('click', function() {
                const currentValue = parseInt(input.value) || 0;
                const minValue = parseInt(input.min) || 1;
                if (currentValue > minValue) {
                    input.value = currentValue - 1;
                    input.dispatchEvent(new Event('change'));
                }
            });
        }
        
        if (incrementBtn) {
            incrementBtn.addEventListener('click', function() {
                const currentValue = parseInt(input.value) || 0;
                const maxValue = parseInt(input.max) || 99;
                if (currentValue < maxValue) {
                    input.value = currentValue + 1;
                    input.dispatchEvent(new Event('change'));
                }
            });
        }
    });
}

/**
 * Initialize product image gallery
 */
function initProductGallery() {
    const mainImage = document.getElementById('mainImage');
    const thumbnails = document.querySelectorAll('.thumbnail-image');
    
    if (mainImage && thumbnails.length > 0) {
        thumbnails.forEach(function(thumb) {
            thumb.addEventListener('click', function() {
                // Update main image
                mainImage.src = this.dataset.fullImage || this.src;
                
                // Update active state
                thumbnails.forEach(t => t.classList.remove('active'));
                this.classList.add('active');
            });
        });
    }
}

/**
 * Initialize form validation
 */
function initFormValidation() {
    const forms = document.querySelectorAll('form[data-validate]');
    
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
}

/**
 * Update cart quantity via AJAX
 * @param {number} itemId - Cart item ID
 * @param {number} quantity - New quantity
 */
function updateCartQuantity(itemId, quantity) {
    const form = document.querySelector(`form[data-item-id="${itemId}"]`);
    if (form) {
        const input = form.querySelector('input[name="quantity"]');
        input.value = quantity;
        form.submit();
    }
}

/**
 * Add to cart with loading state
 * @param {HTMLFormElement} form - The add to cart form
 */
function addToCart(form) {
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    
    // Show loading state
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Adding...';
    
    // Form will submit normally
    return true;
}

/**
 * Toggle mobile menu
 */
function toggleMobileMenu() {
    const navbar = document.getElementById('navbarNav');
    if (navbar) {
        navbar.classList.toggle('show');
    }
}

/**
 * Show confirmation dialog
 * @param {string} message - Confirmation message
 * @returns {boolean} - User's choice
 */
function confirmAction(message) {
    return confirm(message || 'Are you sure you want to proceed?');
}

/**
 * Format price with currency
 * @param {number} amount - Price amount
 * @param {string} currency - Currency code
 * @returns {string} - Formatted price
 */
function formatPrice(amount, currency = 'USD') {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency
    }).format(amount);
}

/**
 * Debounce function
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @returns {Function} - Debounced function
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Lazy load images
 */
function lazyLoadImages() {
    const images = document.querySelectorAll('img[data-src]');
    
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
                observer.unobserve(img);
            }
        });
    });
    
    images.forEach(img => imageObserver.observe(img));
}

// Initialize lazy loading if supported
if ('IntersectionObserver' in window) {
    lazyLoadImages();
}

// Export functions for use in other scripts
window.DjangoEcommerce = {
    updateCartQuantity,
    addToCart,
    formatPrice,
    debounce,
    confirmAction
};
