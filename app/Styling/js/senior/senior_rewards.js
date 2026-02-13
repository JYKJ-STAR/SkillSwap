/**
 * Youth Rewards Page JavaScript
 * Handles tab switching, modals, and reward redemption logic
 */

document.addEventListener('DOMContentLoaded', function () {
    // User data - will be populated from server
    let userPoints = parseInt(document.getElementById('user-points')?.dataset.points || 0);

    // =========================
    // Tab Switching
    // =========================
    const tabs = document.querySelectorAll('.rewards-tab');
    const tabContents = document.querySelectorAll('.tab-content');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const targetTab = tab.dataset.tab;

            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            tabContents.forEach(content => {
                content.classList.remove('active');
                if (content.id === `${targetTab}-content`) {
                    content.classList.add('active');
                }
            });
        });
    });

    // =========================
    // Snackbar Functions
    // =========================
    function showSnackbar(message) {
        const snackbar = document.getElementById('snackbar');
        const snackbarMessage = snackbar.querySelector('.snackbar-message');
        if (snackbarMessage) {
            snackbarMessage.textContent = message || 'Error: Insufficient points';
        }
        snackbar.classList.add('show');
    }

    function hideSnackbar() {
        document.getElementById('snackbar').classList.remove('show');
    }

    // Attach snackbar dismiss
    const dismissBtn = document.querySelector('.snackbar-dismiss');
    if (dismissBtn) {
        dismissBtn.addEventListener('click', hideSnackbar);
    }

    // =========================
    // Redeem Reward - Event Delegation
    // =========================
    document.querySelectorAll('.redeem-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            const name = this.dataset.name;
            const vendor = this.dataset.vendor;
            const points = parseInt(this.dataset.points) || 0;

            if (name && vendor && points) {
                attemptRedeem(name, vendor, points);
            }
        });
    });

    let pendingRedemption = null;

    function attemptRedeem(title, vendor, points) {
        if (userPoints < points) {
            showSnackbar('Error: Insufficient points');
            setTimeout(hideSnackbar, 5000);
        } else {
            pendingRedemption = { title, vendor, points };
            showRedeemModal(title, vendor, points);
        }
    }

    // =========================
    // Claim Reward - Event Delegation
    // =========================
    let currentRedemptionId = null;

    document.querySelectorAll('.claim-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            const name = this.dataset.name;
            const vendor = this.dataset.vendor;
            currentRedemptionId = this.dataset.redemptionId;

            if (name && vendor) {
                showClaimModal(name, vendor);
            }
        });
    });

    // =========================
    // Redeem Confirmation Modal
    // =========================
    function showRedeemModal(title, vendor, points) {
        document.getElementById('redeem-modal-title').textContent = title;
        document.getElementById('redeem-modal-vendor').textContent = vendor;
        document.getElementById('redeem-modal-points').textContent = points + ' Points';
        document.getElementById('redeem-modal').classList.add('show');
    }

    window.hideRedeemModal = function () {
        document.getElementById('redeem-modal').classList.remove('show');
        // Don't clear pendingRedemption here just in case, but usually safe
    };

    window.confirmRedeem = function () {
        if (!pendingRedemption) return;

        const { title, vendor, points } = pendingRedemption;
        hideRedeemModal();

        // Perform AJAX request
        fetch('/redeem_reward', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                reward_name: title,
                reward_vendor: vendor,
                points_required: points
            })
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Deduct points locally
                    userPoints -= points;
                    const pointsDisplay = document.getElementById('user-points');
                    if (pointsDisplay) {
                        pointsDisplay.textContent = userPoints + ' Points';
                        pointsDisplay.dataset.points = userPoints;
                    }

                    showSubmittedModal();
                } else {
                    showSnackbar(data.error || 'Redemption failed');
                    setTimeout(hideSnackbar, 5000);
                }
            })
            .catch(error => {

                showSnackbar('Network error, please try again');
                setTimeout(hideSnackbar, 5000);
            });

        pendingRedemption = null;
    };

    // =========================
    // Claim Modal (from My Rewards tab)
    // =========================
    window.showClaimModal = function (title, vendor) {
        document.getElementById('claim-modal-title').textContent = title;
        document.getElementById('claim-modal-vendor').textContent = vendor;
        document.getElementById('claim-modal').classList.add('show');
    };

    window.hideClaimModal = function () {
        document.getElementById('claim-modal').classList.remove('show');
    };

    // =========================
    // Submitted Modal
    // =========================
    function showSubmittedModal() {
        document.getElementById('submitted-modal').classList.add('show');
    }

    window.hideSubmittedModal = function () {
        document.getElementById('submitted-modal').classList.remove('show');
    };

    // =========================
    // Vendor Modal (Show to Vendor)
    // =========================
    window.showVendorModal = function (title, vendor) {
        document.getElementById('vendor-modal-title').textContent = title;
        document.getElementById('vendor-modal-vendor').textContent = vendor;
        document.getElementById('vendor-modal').classList.add('show');
    };

    window.hideVendorModal = function () {
        document.getElementById('vendor-modal').classList.remove('show');
    };

    window.dismissReward = function () {
        hideVendorModal();

        if (!currentRedemptionId) {

            return;
        }

        // Make AJAX call to persist dismiss action
        fetch('/dismiss_reward', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                redemption_id: parseInt(currentRedemptionId)
            })
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {

                    // Reload page to update History tab with dismissed reward
                    window.location.reload();
                } else {

                }
            })
            .catch(error => {

            });

        currentRedemptionId = null;
    };

    // =========================
    // Close Modals on Overlay Click
    // =========================
    document.querySelectorAll('.modal-overlay').forEach(overlay => {
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                overlay.classList.remove('show');
            }
        });
    });

    // =========================
    // Close Modals on Escape Key
    // =========================
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            document.querySelectorAll('.modal-overlay.show').forEach(modal => {
                modal.classList.remove('show');
            });
            hideSnackbar();
        }
    });
});
