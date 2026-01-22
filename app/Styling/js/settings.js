document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('settingsForm');
    const editBtn = document.getElementById('editBtn');
    const editContainer = document.getElementById('editContainer');
    const saveBtn = document.getElementById('saveBtn');
    const clearBtn = document.getElementById('clearBtn');
    const unsavedBar = document.getElementById('unsavedBar');
    const inputs = form.querySelectorAll('input, textarea');
    const photoInput = document.getElementById('profile_photo');
    const avatarPreview = document.getElementById('avatarPreview');

    // Store initial values
    let initialValues = {};
    let initialPhotoSrc = avatarPreview.src;

    function captureInitialValues() {
        inputs.forEach(input => {
            if (input.type !== 'file') {
                initialValues[input.name] = input.value;
            }
        });
        initialPhotoSrc = avatarPreview.src;
    }

    captureInitialValues();

    // Toggle Edit Mode
    editBtn.addEventListener('click', function () {
        // Enable inputs
        inputs.forEach(input => {
            input.disabled = false;
            // Switch formatting
            if (input.type !== 'file' && input.type !== 'hidden') {
                input.classList.remove('form-control-plaintext');
                input.classList.add('form-control'); // Bootstrap class for better editing style
            }
        });

        // Add editing class for CSS hooks (like photo upload button)
        form.classList.add('is-editing');

        // Hide Edit Button
        editContainer.classList.add('d-none');
    });

    // Check for changes
    function checkChanges() {
        let hasChanges = false;

        // Check text inputs
        inputs.forEach(input => {
            if (input.type !== 'file' && input.name in initialValues) {
                if (input.value !== initialValues[input.name]) {
                    hasChanges = true;
                }
            }
        });

        // Check file input
        if (photoInput.files.length > 0) {
            hasChanges = true;
        }

        if (hasChanges) {
            unsavedBar.classList.add('active');
        } else {
            unsavedBar.classList.remove('active');
        }
    }

    // Input listeners
    inputs.forEach(input => {
        input.addEventListener('input', checkChanges);
        input.addEventListener('change', checkChanges);
    });

    // Image Upload Preview
    photoInput.addEventListener('change', function () {
        if (this.files && this.files[0]) {
            const reader = new FileReader();
            reader.onload = function (e) {
                avatarPreview.src = e.target.result;
            };
            reader.readAsDataURL(this.files[0]);
            checkChanges();
        }
    });

    // Clear / Cancel
    clearBtn.addEventListener('click', function () {
        // Reset inputs
        inputs.forEach(input => {
            if (input.type !== 'file' && input.name in initialValues) {
                input.value = initialValues[input.name];
            }
        });

        // Reset File
        photoInput.value = '';
        avatarPreview.src = initialPhotoSrc;

        // Reset UI to Read Only
        inputs.forEach(input => {
            input.disabled = true;
            if (input.type !== 'file' && input.type !== 'hidden') {
                input.classList.add('form-control-plaintext');
                input.classList.remove('form-control');
            }
        });

        form.classList.remove('is-editing');
        editContainer.classList.remove('d-none');
        unsavedBar.classList.remove('active');
    });

    // Save Changes
    saveBtn.addEventListener('click', function () {
        const formData = new FormData(form);

        // Visual feedback
        const originalText = saveBtn.innerText;
        saveBtn.innerText = 'Saving...';
        saveBtn.disabled = true;

        fetch('/settings/update', {
            method: 'POST',
            body: formData
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update successfully
                    captureInitialValues(); // Update baseline
                    unsavedBar.classList.remove('active');

                    // Return to read-only
                    inputs.forEach(input => {
                        input.disabled = true;
                        if (input.type !== 'file' && input.type !== 'hidden') {
                            input.classList.add('form-control-plaintext');
                            input.classList.remove('form-control');
                        }
                    });
                    form.classList.remove('is-editing');
                    editContainer.classList.remove('d-none');

                    // Optional: Show success toast (not implemented but good practice)
                    // alert('Profile updated!'); 
                } else {
                    alert('Error updating profile: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while saving.');
            })
            .finally(() => {
                saveBtn.innerText = originalText;
                saveBtn.disabled = false;
            });
    });
});
