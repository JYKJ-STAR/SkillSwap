/**
 * Youth Schedule Page JavaScript
 * Handles tab switching, modals, and user interactions
 */

document.addEventListener('DOMContentLoaded', function () {

    // ========================================
    // TAB SWITCHING
    // ========================================
    const tabs = document.querySelectorAll('.filter-tab');
    const completedView = document.getElementById('completed-view');
    const upcomingView = document.getElementById('upcoming-view');
    const allEmptyState = document.getElementById('all-empty-state');

    function updateView(filter) {
        // Reset visibility
        completedView.style.display = 'none';
        upcomingView.style.display = 'none';
        allEmptyState.style.display = 'none';

        // Helper to check if a view has actual cards (ignoring empty message p tag)
        const hasCompleted = completedView.querySelector('.event-card') !== null;
        const hasUpcoming = upcomingView.querySelector('.event-card') !== null;

        // Manage individual empty messages visibility
        const completedMsg = completedView.querySelector('p.text-muted');
        const upcomingMsg = upcomingView.querySelector('p.text-muted');

        if (filter === 'completed') {
            completedView.style.display = 'flex';
            if (completedMsg) completedMsg.style.display = hasCompleted ? 'none' : 'block';
        } else if (filter === 'upcoming') {
            upcomingView.style.display = 'flex';
            if (upcomingMsg) upcomingMsg.style.display = hasUpcoming ? 'none' : 'block';
        } else {
            // ALL View
            if (!hasCompleted && !hasUpcoming) {
                // Both empty -> show combined message, hide individual views/messages
                allEmptyState.style.display = 'block';
            } else {
                // At least one has content
                completedView.style.display = hasCompleted ? 'flex' : 'none';
                upcomingView.style.display = hasUpcoming ? 'flex' : 'none';

                // Ensure individual empty messages are hidden in "All" view to avoid clutter
                if (completedMsg) completedMsg.style.display = 'none';
                if (upcomingMsg) upcomingMsg.style.display = 'none';
            }
        }
    }

    // Initial load logic (All view)
    updateView('all');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // Remove active class from all tabs
            tabs.forEach(t => t.classList.remove('active'));
            // Add active class to clicked tab
            tab.classList.add('active');

            let filter = 'all';
            if (tab.classList.contains('completed')) filter = 'completed';
            if (tab.classList.contains('upcoming')) filter = 'upcoming';

            updateView(filter);
        });
    });

    // ========================================
    // MODAL LOGIC
    // ========================================

    // Open Modal Function - attached to global window for inline onclicks
    window.openModal = function (modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add('show');
        }
    };

    // Close Modal Function
    window.closeModal = function (modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.remove('show');
        }
    };

    // Close buttons handler
    document.querySelectorAll('.close-modal').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault(); // Prevent link default
            const targetId = btn.getAttribute('data-target');
            if (targetId) {
                closeModal(targetId);
            }
        });
    });

    // Close on overlay click
    document.querySelectorAll('.modal-overlay').forEach(overlay => {
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                overlay.classList.remove('show');
            }
        });
    });

    // Log Reflection buttons -> Open Feedback Modal (Example connection)
    document.querySelectorAll('.log-reflection-btn').forEach(btn => {
        if (!btn.classList.contains('gray')) { // Only enable for non-gray buttons
            btn.addEventListener('click', () => {
                openModal('feedback-modal');
            });
        }
    });

    // ========================================
    // STAR RATING LOGIC
    // ========================================
    const stars = document.querySelectorAll('.star');
    let currentRating = 0;

    stars.forEach((star, index) => {
        star.addEventListener('click', () => {
            currentRating = index + 1;
            updateStars();
        });

        star.addEventListener('mouseenter', () => {
            highlightStars(index + 1);
        });

        star.addEventListener('mouseleave', () => {
            updateStars();
        });
    });

    function highlightStars(count) {
        stars.forEach((star, index) => {
            if (index < count) {
                star.classList.add('active');
            } else {
                star.classList.remove('active');
            }
        });
    }

    function updateStars() {
        highlightStars(currentRating);
    }

    // ========================================
    // FILE UPLOAD LOGIC
    // ========================================
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    const previewContainer = document.getElementById('previewContainer');
    const previewImage = document.getElementById('previewImage');
    const previewName = document.getElementById('previewName');

    if (uploadArea && fileInput) {
        // Click to upload
        uploadArea.addEventListener('click', () => {
            fileInput.click();
        });

        // Handle file selection
        fileInput.addEventListener('change', (e) => {
            handleFile(e.target.files[0]);
        });

        // Drag and drop
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            const file = e.dataTransfer.files[0];
            if (file && (file.type === 'image/jpeg' || file.type === 'image/png')) {
                handleFile(file);
            }
        });
    }

    function handleFile(file) {
        if (!file) return;

        const reader = new FileReader();
        reader.onload = (e) => {
            if (previewImage) previewImage.src = e.target.result;
            if (previewName) previewName.textContent = file.name;
            if (previewContainer) previewContainer.style.display = 'block';
            if (uploadArea) uploadArea.style.display = 'none';
        };
        reader.readAsDataURL(file);
    }

    // ========================================
    // WITHDRAW LOGIC
    // ========================================
    const withdrawSubmitBtn = document.querySelector('.btn-withdraw');
    if (withdrawSubmitBtn) {
        withdrawSubmitBtn.addEventListener('click', () => {
            const reasoning = document.querySelector('.reasoning-textarea')?.value;
            // Basic validation
            // In a real app, you might want to require reasoning
            // if (!reasoning || reasoning.trim() === '') {
            //     alert('Please provide a reason for withdrawing.');
            //     return;
            // }

            // Mock submission
            // alert('Event withdrawal submitted.');
            closeModal('withdraw-modal');
        });
    }
});
