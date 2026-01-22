/**
 * Senior Rewards Page JavaScript
 * Handles tab switching and reward interactions
 */

document.addEventListener('DOMContentLoaded', function () {
    // =========================
    // Tab Switching
    // =========================
    const tabs = document.querySelectorAll('.table-tab');
    const lists = document.querySelectorAll('.rewards-list');
    const pageTitle = document.getElementById('page-title');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const targetTab = tab.dataset.tab;

            // Update active tab
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            // Update visible list
            lists.forEach(list => {
                list.classList.remove('active');
            });

            if (targetTab === 'redeem') {
                document.getElementById('redeem-list').classList.add('active');
                if (pageTitle) {
                    pageTitle.textContent = 'Redeem Rewards';
                }
            } else {
                document.getElementById('my-rewards-list').classList.add('active');
                if (pageTitle) {
                    pageTitle.textContent = 'My Rewards';
                }
            }
        });
    });

    // =========================
    // Redeem Button - Event Delegation
    // =========================
    document.querySelectorAll('.redeem-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            const name = this.dataset.name;
            const vendor = this.dataset.vendor;
            const points = parseInt(this.dataset.points) || 0;
            const action = this.dataset.action;

            if (action === 'claim') {
                // Handle claim action for My Rewards tab
                showClaimConfirmation(name, vendor);
            } else if (name && vendor && points) {
                // Handle redeem action
                attemptRedeem(name, vendor, points);
            }
        });
    });

    // =========================
    // Show Voucher Link - Event Delegation
    // =========================
    document.querySelectorAll('.show-voucher-link').forEach(link => {
        link.addEventListener('click', function (e) {
            e.preventDefault();
            const name = this.dataset.name;
            const vendor = this.dataset.vendor;
            if (name && vendor) {
                showVoucherToVendor(name, vendor);
            }
        });
    });

    // =========================
    // Redeem Function
    // =========================
    function attemptRedeem(title, vendor, points) {
        // Get user points from session/page data
        const userPointsEl = document.getElementById('user-points');
        const userPoints = userPointsEl ? parseInt(userPointsEl.dataset.points) || 0 : 0;

        if (userPoints < points) {
            showNotification('Insufficient points to redeem this reward.', 'error');
        } else {
            // Show confirmation modal or process redemption
            if (confirm(`Redeem "${title}" for ${points} points?`)) {
                showNotification('Redemption request submitted!', 'success');
                // Here you would make an AJAX call to process the redemption
            }
        }
    }

    // =========================
    // Claim Confirmation
    // =========================
    function showClaimConfirmation(title, vendor) {
        if (confirm(`Claim "${title}" from ${vendor}?`)) {
            showNotification('Claim request submitted! Please show this to the vendor.', 'success');
            // Here you would make an AJAX call to process the claim
        }
    }

    // =========================
    // Show Voucher to Vendor
    // =========================
    function showVoucherToVendor(title, vendor) {
        alert(`Show this voucher to ${vendor}:\n\n${title}\n\nPresent this screen at the counter to redeem.`);
        // In production, this would open a modal with a barcode/QR code
    }

    // =========================
    // Notification Helper
    // =========================
    function showNotification(message, type) {
        // Check if toast.js is available
        if (typeof showToast === 'function') {
            showToast(message, type);
        } else {
            alert(message);
        }
    }
});
