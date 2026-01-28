/**
 * Youth Schedule Page JavaScript
 * Handles tab switching, modals, and user interactions
 */

// ========================================
// GLOBAL MODAL HELPERS (Internal use)
// ========================================
function openModal(modalId) {
    console.log('openModal called with:', modalId);
    const modal = document.getElementById(modalId);
    console.log('Modal element found:', modal);
    if (modal) {
        console.log('Adding show class...');
        modal.classList.add('show');
        console.log('Modal classList after:', modal.classList.toString());
        console.log('Modal display:', window.getComputedStyle(modal).display);
        console.log('Modal opacity:', window.getComputedStyle(modal).opacity);
        console.log('Modal visibility:', window.getComputedStyle(modal).visibility);
    } else {
        console.error("Modal not found:", modalId);
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('show');
    }
}


document.addEventListener('DOMContentLoaded', function () {
    console.log('Schedule JS loaded');

    // ========================================
    // TAB SWITCHING
    // ========================================
    const tabs = document.querySelectorAll('.filter-tab');
    const upcomingView = document.getElementById('upcoming-view');
    const waitingView = document.getElementById('waiting-view');
    const completedView = document.getElementById('completed-view');

    function updateView(filter) {
        console.log('Switching to view:', filter);
        // Reset all to hidden
        if (upcomingView) upcomingView.style.display = 'none';
        if (waitingView) waitingView.style.display = 'none';
        if (completedView) completedView.style.display = 'none';

        if (filter === 'upcoming' && upcomingView) {
            upcomingView.style.display = 'flex';
        } else if (filter === 'waiting' && waitingView) {
            waitingView.style.display = 'block';
        } else if (filter === 'completed' && completedView) {
            completedView.style.display = 'flex';
        }
    }

    // Initial load logic (Upcoming is active by default in HTML)
    updateView('upcoming');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            if (tab.classList.contains('upcoming')) updateView('upcoming');
            if (tab.classList.contains('waiting')) updateView('waiting');
            if (tab.classList.contains('completed')) updateView('completed');
        });
    });

    // ========================================
    // BUTTON LISTENERS (Upload Only)
    // ========================================
    console.log('Attaching button listeners...');
    const uploadBtns = document.querySelectorAll('.js-open-upload');

    console.log('Found upload buttons:', uploadBtns.length);

    uploadBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            console.log('Upload button clicked!');
            const eventId = btn.dataset.id;
            const title = btn.dataset.title;

            console.log('Event ID:', eventId, 'Title:', title);

            document.getElementById('upload_event_id').value = eventId;
            const titleEl = document.getElementById('upload-event-title');
            if (titleEl) titleEl.textContent = title;

            openModal('upload-modal');
        });
    });

    // ========================================
    // SUB-TAB SWITCHING (Waiting for Feedback)
    // ========================================
    const subTabs = document.querySelectorAll('.sub-filter-tab');
    const actionRequiredView = document.getElementById('action-required-view');
    const pendingReviewView = document.getElementById('pending-review-view');

    function updateSubView(filter) {
        if (!actionRequiredView || !pendingReviewView) return;

        actionRequiredView.style.display = 'none';
        pendingReviewView.style.display = 'none';

        if (filter === 'action-required') {
            actionRequiredView.style.display = 'flex';
        } else if (filter === 'pending-review') {
            pendingReviewView.style.display = 'flex';
        }
    }

    // Initial sub-view (Action Required is active by default)
    updateSubView('action-required');

    subTabs.forEach(subTab => {
        subTab.addEventListener('click', () => {
            subTabs.forEach(t => t.classList.remove('active'));
            subTab.classList.add('active');

            if (subTab.classList.contains('action-required')) updateSubView('action-required');
            if (subTab.classList.contains('pending-review')) updateSubView('pending-review');
        });
    });

    // ========================================
    // CLOSE BUTTONS & OVERLAYS
    // ========================================
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

    // ========================================
    // STAR RATING LOGIC
    // ========================================
    const stars = document.querySelectorAll('.star');
    let currentRating = 0;

    stars.forEach((star, index) => {
        star.addEventListener('click', () => {
            currentRating = index + 1;
            const ratingInput = document.getElementById('rating_input');
            if (ratingInput) ratingInput.value = currentRating;
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
            closeModal('withdraw-modal');
        });
    }
});
