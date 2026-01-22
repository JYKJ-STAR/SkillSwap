// Senior Dashboard JavaScript
// ========================================

document.addEventListener('DOMContentLoaded', function () {
    // Confirm logout
    const logoutBtn = document.querySelector('a[href*="logout"]');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function (e) {
            if (!confirm('Are you sure you want to log out?')) {
                e.preventDefault();
            }
        });
    }

    // Make all text larger for better readability
    document.body.style.fontSize = '18px';
});
