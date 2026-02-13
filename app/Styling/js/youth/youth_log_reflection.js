/**
 * Youth Log Reflection JavaScript
 * Handles star rating and file upload functionality
 */

document.addEventListener('DOMContentLoaded', function () {

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
    // FORM VALIDATION
    // ========================================
    const form = document.querySelector('.reflection-form');
    const errorMessage = document.getElementById('error-message');

    function showError(message) {
        if (errorMessage) {
            errorMessage.textContent = message;
            errorMessage.style.display = 'flex';
            // Scroll to error message
            errorMessage.scrollIntoView({ behavior: 'smooth', block: 'center' });
            // Hide after 5 seconds
            setTimeout(() => {
                errorMessage.style.display = 'none';
            }, 5000);
        }
    }

    if (form) {
        form.addEventListener('submit', (e) => {
            const rating = document.getElementById('rating_input').value;
            const comment = document.querySelector('[name="comment"]').value;
            const photoInput = document.getElementById('fileInput');
            const photo = photoInput ? photoInput.files[0] : null;

            if (!rating || rating === '0') {
                e.preventDefault();
                showError('Please provide a rating by clicking on the stars.');
                return false;
            }

            if (!comment.trim()) {
                e.preventDefault();
                showError('Please share your thoughts in the feedback section.');
                return false;
            }

            if (!photo) {
                e.preventDefault();
                showError('Please upload a photo.');
                return false;
            }
        });
    }
});
