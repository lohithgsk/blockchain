/**
 * P2P Blockchain Network - Main JavaScript
 * =======================================
 * Common functionality for the blockchain web interface
 */

// Global variables
let refreshInterval = null;
let networkHealthInterval = null;

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

/**
 * Initialize the application
 */
function initializeApp() {
    console.log('🔗 Blockchain Network Interface Initialized');
    
    // Add loading animations
    addLoadingAnimations();
    
    // Initialize tooltips
    initializeTooltips();
    
    // Setup auto-refresh
    setupAutoRefresh();
    
    // Setup keyboard shortcuts
    setupKeyboardShortcuts();
    
    // Setup form enhancements
    setupFormEnhancements();
    
    // Setup network monitoring
    setupNetworkMonitoring();
    
    // Show welcome message
    setTimeout(() => {
        showToast('Blockchain network interface loaded successfully!', 'success');
    }, 1000);
}

/**
 * Add loading animations to elements
 */
function addLoadingAnimations() {
    // Add fade-in animation to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            card.style.transition = 'all 0.5s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
    
    // Add slide-in animation to stats cards
    const statCards = document.querySelectorAll('.stat-card');
    statCards.forEach((card, index) => {
        card.classList.add('fade-in');
        card.style.animationDelay = `${index * 0.1}s`;
    });
}

/**
 * Initialize Bootstrap tooltips
 */
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Setup auto-refresh functionality
 */
function setupAutoRefresh() {
    // Refresh every 10 seconds
    refreshInterval = setInterval(() => {
        refreshGlobalStats();
    }, 10000);
    
    // Network health check every 30 seconds
    networkHealthInterval = setInterval(() => {
        checkNetworkHealth();
    }, 30000);
}

/**
 * Setup keyboard shortcuts
 */
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Only trigger shortcuts with Ctrl/Cmd key
        if (!(e.ctrlKey || e.metaKey)) return;
        
        switch(e.key.toLowerCase()) {
            case 'm':
                e.preventDefault();
                if (window.location.pathname === '/mining') {
                    const mineButton = document.getElementById('mineButton');
                    if (mineButton && !mineButton.disabled) {
                        mineButton.click();
                    }
                } else {
                    window.location.href = '/mining';
                }
                break;
                
            case 't':
                e.preventDefault();
                if (window.location.pathname === '/transactions') {
                    const senderInput = document.getElementById('sender');
                    if (senderInput) senderInput.focus();
                } else {
                    window.location.href = '/transactions';
                }
                break;
                
            case 'n':
                e.preventDefault();
                window.location.href = '/network';
                break;
                
            case 'e':
                e.preventDefault();
                window.location.href = '/explorer';
                break;
                
            case 's':
                e.preventDefault();
                if (window.location.pathname === '/network') {
                    const syncButton = document.getElementById('syncBtn');
                    if (syncButton && !syncButton.disabled) {
                        syncButton.click();
                    }
                }
                break;
                
            case 'r':
                e.preventDefault();
                refreshGlobalStats();
                showToast('Data refreshed manually', 'info');
                break;
        }
    });
    
    // Show keyboard shortcuts info
    console.log('⌨️  Keyboard Shortcuts:');
    console.log('   Ctrl/Cmd + M: Mine block (or go to mining page)');
    console.log('   Ctrl/Cmd + T: Create transaction (or go to transactions page)');
    console.log('   Ctrl/Cmd + N: Go to network page');
    console.log('   Ctrl/Cmd + E: Go to explorer page');
    console.log('   Ctrl/Cmd + S: Sync network (if on network page)');
    console.log('   Ctrl/Cmd + R: Refresh data');
}

/**
 * Setup form enhancements
 */
function setupFormEnhancements() {
    // Add loading states to forms
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitButton = form.querySelector('button[type="submit"]');
            if (submitButton) {
                const originalText = submitButton.innerHTML;
                submitButton.disabled = true;
                submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
                
                // Reset after 5 seconds (fallback)
                setTimeout(() => {
                    submitButton.disabled = false;
                    submitButton.innerHTML = originalText;
                }, 5000);
            }
        });
    });
    
    // Add real-time validation
    const inputs = document.querySelectorAll('input[type="number"]');
    inputs.forEach(input => {
        input.addEventListener('input', function() {
            if (this.value < 0) {
                this.setCustomValidity('Value must be positive');
                this.classList.add('is-invalid');
            } else {
                this.setCustomValidity('');
                this.classList.remove('is-invalid');
            }
        });
    });
}

/**
 * Setup network monitoring
 */
function setupNetworkMonitoring() {
    // Monitor connection status
    window.addEventListener('online', function() {
        showToast('Connection restored', 'success');
        resumeAutoRefresh();
    });
    
    window.addEventListener('offline', function() {
        showToast('Connection lost - working offline', 'warning');
        pauseAutoRefresh();
    });
}

/**
 * Refresh global statistics
 */
function refreshGlobalStats() {
    fetch('/api/stats')
        .then(response => response.json())
        .then(data => {
            updateGlobalStats(data);
        })
        .catch(error => {
            console.log('Failed to refresh global stats:', error);
            // Show offline indicator
            updateConnectionStatus(false);
        });
}

/**
 * Update global statistics in the UI
 */
function updateGlobalStats(data) {
    // Update connection status
    updateConnectionStatus(true);
    
    // Update common elements that appear on multiple pages
    const elements = {
        'chainLength': data.chain_length,
        'peerCount': data.peer_count,
        'pendingTx': data.pending_count,
        'nodeBalance': data.balance.toFixed(2)
    };
    
    Object.entries(elements).forEach(([id, value]) => {
        const element = document.getElementById(id);
        if (element) {
            animateCounterUpdate(element, value);
        }
    });
    
    // Update navbar badge if exists
    const navbarBadges = document.querySelectorAll('.navbar .badge');
    navbarBadges.forEach(badge => {
        if (badge.textContent.includes('Peers')) {
            badge.textContent = `${data.peer_count} Peers`;
        }
    });
}

/**
 * Animate counter updates
 */
function animateCounterUpdate(element, newValue) {
    const currentValue = parseFloat(element.textContent) || 0;
    const increment = (newValue - currentValue) / 20;
    let current = currentValue;
    
    const timer = setInterval(() => {
        current += increment;
        if ((increment > 0 && current >= newValue) || 
            (increment < 0 && current <= newValue)) {
            current = newValue;
            clearInterval(timer);
        }
        
        element.textContent = typeof newValue === 'string' ? 
            current.toFixed(2) : Math.floor(current);
        
        // Add highlight effect
        element.style.transform = 'scale(1.05)';
        element.style.transition = 'transform 0.2s ease';
        
        setTimeout(() => {
            element.style.transform = 'scale(1)';
        }, 200);
    }, 50);
}

/**
 * Update connection status indicator
 */
function updateConnectionStatus(isOnline) {
    const statusIndicators = document.querySelectorAll('.status-indicator');
    statusIndicators.forEach(indicator => {
        if (indicator.classList.contains('online')) {
            indicator.style.backgroundColor = isOnline ? '#48bb78' : '#e53e3e';
            indicator.style.animation = isOnline ? 'pulse 2s infinite' : 'none';
        }
    });
    
    // Update navbar if needed
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        if (isOnline) {
            navbar.classList.remove('offline');
        } else {
            navbar.classList.add('offline');
        }
    }
}

/**
 * Check network health
 */
function checkNetworkHealth() {
    fetch('/api/health')
        .then(response => response.json())
        .then(data => {
            updateNetworkHealthIndicators(data);
        })
        .catch(error => {
            console.log('Network health check failed:', error);
        });
}

/**
 * Update network health indicators
 */
function updateNetworkHealthIndicators(healthData) {
    // Update health percentage
    const healthBars = document.querySelectorAll('#healthBar');
    healthBars.forEach(bar => {
        const health = healthData.is_chain_valid ? 100 : 75;
        bar.style.width = health + '%';
        bar.textContent = health + '%';
        
        // Update color based on health
        bar.className = 'progress-bar';
        if (health > 80) {
            bar.classList.add('bg-success');
        } else if (health > 60) {
            bar.classList.add('bg-warning');
        } else {
            bar.classList.add('bg-danger');
        }
    });
    
    // Update peer status if on network page
    if (window.location.pathname === '/network' && healthData.peer_status) {
        Object.entries(healthData.peer_status).forEach(([peer, status]) => {
            const statusElement = document.getElementById(`status-${peer}`);
            if (statusElement) {
                statusElement.innerHTML = status === 'online' ? 
                    '<i class="fas fa-check"></i> Online' : 
                    '<i class="fas fa-times"></i> Offline';
                statusElement.className = status === 'online' ? 
                    'badge bg-success' : 'badge bg-danger';
            }
        });
    }
}

/**
 * Show toast notification
 */
function showToast(message, type = 'info', duration = 4000) {
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <i class="fas fa-${getToastIcon(type)}"></i> ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" 
                    data-bs-dismiss="toast"></button>
        </div>
    `;
    
    // Add to toast container or create one
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
        toastContainer.style.zIndex = '1055';
        document.body.appendChild(toastContainer);
    }
    
    toastContainer.appendChild(toast);
    
    // Initialize and show toast
    const bsToast = new bootstrap.Toast(toast, {
        autohide: true,
        delay: duration
    });
    bsToast.show();
    
    // Remove element after hiding
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}

/**
 * Get icon for toast type
 */
function getToastIcon(type) {
    const icons = {
        'success': 'check-circle',
        'warning': 'exclamation-triangle',
        'danger': 'times-circle',
        'info': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

/**
 * Pause auto-refresh
 */
function pauseAutoRefresh() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
        refreshInterval = null;
    }
    if (networkHealthInterval) {
        clearInterval(networkHealthInterval);
        networkHealthInterval = null;
    }
}

/**
 * Resume auto-refresh
 */
function resumeAutoRefresh() {
    if (!refreshInterval) {
        setupAutoRefresh();
    }
}

/**
 * Format timestamp
 */
function formatTimestamp(timestamp) {
    const date = new Date(timestamp * 1000);
    return date.toLocaleString();
}

/**
 * Format hash for display
 */
function formatHash(hash, length = 16) {
    if (!hash) return 'N/A';
    return hash.length > length ? 
        hash.substring(0, length) + '...' : hash;
}

/**
 * Format address for display
 */
function formatAddress(address, length = 12) {
    if (!address || address === 'Mining Reward') return address;
    return address.length > length ? 
        address.substring(0, length) + '...' : address;
}

/**
 * Copy text to clipboard
 */
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        showToast('Copied to clipboard!', 'success', 2000);
    }).catch(function(err) {
        console.error('Failed to copy text: ', err);
        showToast('Failed to copy to clipboard', 'danger', 2000);
    });
}

/**
 * Add copy functionality to hash elements
 */
function makeCopyable() {
    const hashElements = document.querySelectorAll('.hash, .hash-display, .address-display');
    hashElements.forEach(element => {
        element.style.cursor = 'pointer';
        element.title = 'Click to copy';
        element.addEventListener('click', function() {
            copyToClipboard(this.textContent);
        });
    });
}

/**
 * Validate form data
 */
function validateForm(formData) {
    const errors = [];
    
    // Check for empty required fields
    for (let [key, value] of formData.entries()) {
        if (!value.trim()) {
            errors.push(`${key} is required`);
        }
    }
    
    // Validate amount if present
    const amount = formData.get('amount');
    if (amount && parseFloat(amount) <= 0) {
        errors.push('Amount must be positive');
    }
    
    // Validate URL if present
    const url = formData.get('peer_url') || formData.get('nodes');
    if (url && !isValidUrl(url)) {
        errors.push('Invalid URL format');
    }
    
    return errors;
}

/**
 * Check if URL is valid
 */
function isValidUrl(string) {
    try {
        new URL(string);
        return true;
    } catch (_) {
        return false;
    }
}

/**
 * Format number with commas
 */
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

/**
 * Debounce function
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
 * Throttle function
 */
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    }
}

/**
 * Get current page name
 */
function getCurrentPage() {
    const path = window.location.pathname;
    if (path === '/') return 'dashboard';
    return path.substring(1);
}

/**
 * API helper function
 */
async function apiCall(endpoint, options = {}) {
    try {
        const response = await fetch(endpoint, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API call failed:', error);
        throw error;
    }
}

/**
 * Initialize copy functionality when DOM is ready
 */
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(makeCopyable, 500);
});

/**
 * Handle page visibility changes
 */
document.addEventListener('visibilitychange', function() {
    if (document.visibilityState === 'visible') {
        resumeAutoRefresh();
        refreshGlobalStats();
    } else {
        pauseAutoRefresh();
    }
});

/**
 * Export functions for global use
 */
window.BlockchainUI = {
    showToast,
    copyToClipboard,
    formatHash,
    formatAddress,
    formatTimestamp,
    formatNumber,
    apiCall,
    refreshGlobalStats,
    checkNetworkHealth
};

// Development helpers
if (window.location.hostname === 'localhost') {
    window.dev = {
        refreshStats: refreshGlobalStats,
        checkHealth: checkNetworkHealth,
        showToast: showToast,
        pauseRefresh: pauseAutoRefresh,
        resumeRefresh: resumeAutoRefresh
    };
    
    console.log('🛠️  Development helpers available in window.dev');
}