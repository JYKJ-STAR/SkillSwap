/**
 * SkillSwap Admin JavaScript
 * Handles admin dashboard interactions and form submissions
 */

// =====================================================
// TOAST NOTIFICATIONS
// =====================================================
const AdminToast = {
    container: null,

    init() {
        if (!this.container) {
            this.container = document.createElement('div');
            this.container.id = 'toast-container';
            this.container.style.cssText = 'position:fixed;top:20px;right:20px;z-index:9999;';
            document.body.appendChild(this.container);
        }
    },

    show(message, type = 'info', duration = 3000) {
        this.init();

        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.style.cssText = `
            background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6'};
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            margin-bottom: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            animation: slideIn 0.3s ease;
        `;
        toast.textContent = message;

        this.container.appendChild(toast);

        setTimeout(() => {
            toast.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }, duration);
    },

    success(msg) { this.show(msg, 'success'); },
    error(msg) { this.show(msg, 'error'); },
    info(msg) { this.show(msg, 'info'); }
};

// Add animation styles
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style);

// =====================================================
// FORM VALIDATION
// =====================================================
function validateLoginForm(form) {
    const email = form.querySelector('[name="email"]');
    const password = form.querySelector('[name="password"]');

    if (!email.value.trim()) {
        AdminToast.error('Email is required');
        email.focus();
        return false;
    }

    if (!password.value.trim()) {
        AdminToast.error('Password is required');
        password.focus();
        return false;
    }

    return true;
}

// =====================================================
// DASHBOARD INTERACTIONS
// =====================================================
function confirmAction(message) {
    return confirm(message);
}

function approveUser(userId, form) {
    if (confirmAction('Approve this user?')) {
        form.submit();
    }
}

function rejectUser(userId, form) {
    if (confirmAction('Reject and delete this user?')) {
        form.submit();
    }
}

// =====================================================
// SIDEBAR NAVIGATION
// =====================================================
document.addEventListener('DOMContentLoaded', function () {
    // Highlight active nav item based on current URL
    const navItems = document.querySelectorAll('.nav-item');
    const currentPath = window.location.pathname;

    navItems.forEach(item => {
        if (item.getAttribute('href') === currentPath) {
            item.classList.add('active');
        }
    });

    // Initialize tooltips if any
    initTooltips();
});

function initTooltips() {
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    tooltipElements.forEach(el => {
        el.addEventListener('mouseenter', showTooltip);
        el.addEventListener('mouseleave', hideTooltip);
    });
}

function showTooltip(e) {
    const text = e.target.dataset.tooltip;
    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip';
    tooltip.textContent = text;
    tooltip.style.cssText = `
        position: absolute;
        background: #1f2937;
        color: white;
        padding: 5px 10px;
        border-radius: 4px;
        font-size: 12px;
        z-index: 1000;
    `;
    document.body.appendChild(tooltip);

    const rect = e.target.getBoundingClientRect();
    tooltip.style.left = rect.left + 'px';
    tooltip.style.top = (rect.bottom + 5) + 'px';

    e.target._tooltip = tooltip;
}

function hideTooltip(e) {
    if (e.target._tooltip) {
        e.target._tooltip.remove();
        delete e.target._tooltip;
    }
}

// =====================================================
// POINTS MANAGEMENT
// =====================================================
function showPointsModal(userId, userName) {
    const modal = document.getElementById('pointsModal');
    if (modal) {
        modal.querySelector('[name="user_id"]').value = userId;
        modal.querySelector('.user-name').textContent = userName;
        modal.style.display = 'flex';
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
    }
}

// =====================================================
// UTILITY FUNCTIONS
// =====================================================
function formatDate(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-SG', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

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

// Export for module usage if needed
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { AdminToast, validateLoginForm };
}
