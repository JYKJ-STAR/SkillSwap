document.addEventListener('DOMContentLoaded', () => {
    // --- Tabs Logic ---
    const filterTabs = document.querySelectorAll('.filter-tab');
    const eventCards = document.querySelectorAll('.event-card');

    filterTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // Remove active class from all tabs
            filterTabs.forEach(t => t.classList.remove('active'));
            // Add active class to clicked tab
            tab.classList.add('active');

            const filterType = tab.textContent.trim().toLowerCase();

            eventCards.forEach(card => {
                const statusBadge = card.querySelector('.status-badge');
                if (!statusBadge) return;

                const isCompleted = statusBadge.classList.contains('completed');
                const isPending = statusBadge.classList.contains('pending');

                // Reset animation to ensure consistency when showing/hiding
                card.style.animation = 'none';
                card.offsetHeight; /* trigger reflow */
                card.style.animation = '';

                if (filterType === 'all') {
                    card.style.display = '';
                } else if (filterType === 'completed') {
                    if (isCompleted) {
                        card.style.display = '';
                    } else {
                        card.style.display = 'none';
                    }
                } else if (filterType === 'upcoming') {
                    // Mapping Upcoming to Pending status events
                    if (isPending) {
                        card.style.display = '';
                    } else {
                        card.style.display = 'none';
                    }
                }
            });
        });
    });

    // --- Modal Logic ---
    const uploadModal = document.getElementById('uploadModal');
    const feedbackModal = document.getElementById('feedbackModal');
    const withdrawModal = document.getElementById('withdrawModal');

    // Close modal function
    function closeModal(modal) {
        if (modal) {
            modal.classList.remove('active');
            // Reset forms if needed
            if (modal.id === 'uploadModal') {
                resetUploadForm();
            } else if (modal.id === 'withdrawModal') {
                const textarea = modal.querySelector('textarea');
                if (textarea) textarea.value = '';
            }
        }
    }

    // LISTENER FOR PENDING EVENTS (Legacy "Log Reflection" button)
    // NOTE: These might have been removed from HTML but keeping listener just in case
    document.querySelectorAll('.log-reflection-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const isPending = btn.classList.contains('pending');
            const isCompleted = btn.classList.contains('completed');

            if (isPending) {
                if (uploadModal) uploadModal.classList.add('active');
            } else if (isCompleted) {
                if (feedbackModal) feedbackModal.classList.add('active');
            }
        });
    });

    // LISTENER FOR NEW "SUBMIT PHOTO" BUTTONS
    document.querySelectorAll('.action-btn.upload-photo').forEach(btn => {
        btn.addEventListener('click', () => {
            if (uploadModal) uploadModal.classList.add('active');
        });
    });

    // LISTENER FOR NEW "SESSION FEEDBACK" BUTTONS
    document.querySelectorAll('.action-btn.give-feedback').forEach(btn => {
        btn.addEventListener('click', () => {
            if (feedbackModal) feedbackModal.classList.add('active');
        });
    });

    // Withdraw Logic
    let eventToWithdraw = null;

    // LISTENER FOR "WITHDRAW" BUTTONS
    document.querySelectorAll('.action-btn.withdraw').forEach(btn => {
        btn.addEventListener('click', (e) => {
            eventToWithdraw = btn.closest('.event-card');
            if (withdrawModal) withdrawModal.classList.add('active');
        });
    });

    // Withdraw specific buttons
    const closeWithdrawBtn = document.querySelector('.close-withdraw');
    if (closeWithdrawBtn && withdrawModal) {
        closeWithdrawBtn.addEventListener('click', () => {
            closeModal(withdrawModal);
            eventToWithdraw = null;
        });
    }

    // Back links in modals
    document.querySelectorAll('.modal .back-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const modal = link.closest('.modal-overlay');
            closeModal(modal);
        });
    });

    // Close on overlay click
    document.querySelectorAll('.modal-overlay').forEach(overlay => {
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                closeModal(overlay);
            }
        });
    });


    const confirmWithdrawBtn = document.querySelector('.confirm-withdraw');
    if (confirmWithdrawBtn && withdrawModal) {
        confirmWithdrawBtn.addEventListener('click', () => {
            if (eventToWithdraw) {
                eventToWithdraw.remove();
                eventToWithdraw = null;
            }
            closeModal(withdrawModal);
        });
    }


    // --- Upload Photo Logic ---
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    const previewArea = document.getElementById('previewArea');
    const previewImage = document.getElementById('previewImage');
    const removePreview = document.getElementById('removePreview');

    if (uploadArea && fileInput && previewArea && previewImage && removePreview) {
        // Click to upload
        uploadArea.addEventListener('click', () => fileInput.click());

        // File selection
        fileInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                showPreview(file);
            }
        });

        // Drag and drop
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('drag-over');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('drag-over');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('drag-over');
            const file = e.dataTransfer.files[0];
            if (file && (file.type === 'image/jpeg' || file.type === 'image/png')) {
                showPreview(file);
            }
        });

        // Show preview
        function showPreview(file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                previewImage.src = e.target.result;
                uploadArea.style.display = 'none';
                previewArea.classList.add('active');
            };
            reader.readAsDataURL(file);
        }

        function resetUploadForm() {
            previewImage.src = '';
            fileInput.value = '';
            previewArea.classList.remove('active');
            uploadArea.style.display = 'block';
        }

        // Remove preview
        removePreview.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            resetUploadForm();
        });
    }

    // --- Star Rating Logic ---
    const stars = document.querySelectorAll('.star');
    let currentRating = 0;

    if (stars.length > 0) {
        const starRatingContainer = document.getElementById('starRating');

        stars.forEach((star, index) => {
            // Click to set rating
            star.addEventListener('click', () => {
                currentRating = index + 1;
                updateStars();
            });

            // Hover effect
            star.addEventListener('mouseenter', () => {
                highlightStars(index);
            });
        });

        // Reset on mouse leave
        if (starRatingContainer) {
            starRatingContainer.addEventListener('mouseleave', () => {
                updateStars();
            });
        }

        function highlightStars(index) {
            stars.forEach((s, i) => {
                if (i <= index) {
                    s.classList.add('active');
                } else {
                    s.classList.remove('active');
                }
            });
        }

        function updateStars() {
            stars.forEach((s, i) => {
                if (i < currentRating) {
                    s.classList.add('active');
                } else {
                    s.classList.remove('active');
                }
            });
        }
    }
});
