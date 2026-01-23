document.addEventListener('DOMContentLoaded', function () {
    // --- Shared Elements ---
    const unsavedBar = document.getElementById('unsavedBar');

    // --- Navigation Logic ---
    const navProfile = document.getElementById('navProfile');
    const navPassword = document.getElementById('navPassword');
    const profileSection = document.getElementById('profileSection');
    const passwordSection = document.getElementById('passwordSection');
    const pageTitle = document.getElementById('pageTitle');
    const navSkills = document.getElementById('navSkills');
    const skillsSection = document.getElementById('skillsSection');
    const navVerification = document.getElementById('navVerification');
    const verificationSection = document.getElementById('verificationSection');
    const navPrivacy = document.getElementById('navPrivacy');
    const privacySection = document.getElementById('privacySection');

    function switchSection(section) {
        // Hide all first
        profileSection.classList.add('d-none');
        passwordSection.classList.add('d-none');
        skillsSection.classList.add('d-none');
        if (verificationSection) verificationSection.classList.add('d-none');
        if (privacySection) privacySection.classList.add('d-none');

        // Deactivate navs
        navProfile.classList.remove('active');
        if (navPassword) navPassword.classList.remove('active');
        navSkills.classList.remove('active');
        if (navVerification) navVerification.classList.remove('active');
        if (navPrivacy) navPrivacy.classList.remove('active');

        // Show specific
        if (section === 'profile') {
            profileSection.classList.remove('d-none');
            navProfile.classList.add('active');
        } else if (section === 'password') {
            passwordSection.classList.remove('d-none');
            navPassword.classList.add('active');
        } else if (section === 'skills') {
            skillsSection.classList.remove('d-none');
            navSkills.classList.add('active');
            renderSkills('teach'); // Init default tab
        } else if (section === 'verification') {
            verificationSection.classList.remove('d-none');
            navVerification.classList.add('active');
        } else if (section === 'privacy') {
            privacySection.classList.remove('d-none');
            navPrivacy.classList.add('active');
        }
    }

    navProfile.addEventListener('click', () => switchSection('profile'));
    if (navPassword) {
        navPassword.addEventListener('click', () => switchSection('password'));
    }
    navSkills.addEventListener('click', () => switchSection('skills'));
    if (navVerification) {
        navVerification.addEventListener('click', () => switchSection('verification'));
    }
    if (navPrivacy) {
        navPrivacy.addEventListener('click', () => switchSection('privacy'));
    }


    // --- Profile Logic ---
    const form = document.getElementById('settingsForm');
    const editBtn = document.getElementById('editBtn');
    const stopEditBtn = document.getElementById('stopEditBtn');
    const editContainer = document.getElementById('editContainer');
    const saveBtn = document.getElementById('saveBtn'); // In unsaved bar
    const clearBtn = document.getElementById('clearBtn'); // In unsaved bar
    const inputs = form.querySelectorAll('input, textarea, select');
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
            // Prevent editing of birth_date
            if (input.name !== 'birth_date') {
                input.disabled = false;
                // Switch formatting
                if (input.type !== 'file' && input.type !== 'hidden' && input.tagName.toLowerCase() !== 'select') {
                    input.classList.remove('form-control-plaintext');
                    input.classList.add('form-control'); // Bootstrap class for better editing style
                }
            }
        });

        // Add editing class for CSS hooks (like photo upload button)
        form.classList.add('is-editing');

        // Toggle Buttons
        editBtn.classList.add('d-none');
        stopEditBtn.classList.remove('d-none');
    });

    // Stop Editing Button (Same as Clear)
    stopEditBtn.addEventListener('click', function () {
        clearBtn.click();
    });

    // Check for changes (Profile)
    function checkChanges() {
        let hasChanges = false;

        // Check text/select inputs
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

        if (hasChanges && !passwordSection.classList.contains('active-section')) {
            // Logic check: only show bar if we are in profile section editing? 
            // Simpler: just check if form has is-editing class
            if (form.classList.contains('is-editing')) {
                unsavedBar.classList.add('active');
                // Ensure save btn is linked to profile update
                saveBtn.onclick = saveProfile;
            }
        } else {
            if (!passwordSection.classList.contains('d-none')) {
                // Ignore profile changes if we are in password mode?
                // For now, let's keep interactions simple.
            } else {
                unsavedBar.classList.remove('active');
            }
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

    // Clear / Cancel (Shared logic? No, mostly profile)
    clearBtn.addEventListener('click', function () {
        // Only if profile is active or editing
        if (form.classList.contains('is-editing')) {
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
                if (input.type !== 'file' && input.type !== 'hidden' && input.tagName.toLowerCase() !== 'select') {
                    input.classList.add('form-control-plaintext');
                    input.classList.remove('form-control');
                }
            });

            form.classList.remove('is-editing');

            // Restore buttons
            editBtn.classList.remove('d-none');
            stopEditBtn.classList.add('d-none');

            unsavedBar.classList.remove('active');
        }

        // Clear Password Form too
        document.getElementById('passwordForm').reset();
        if (!passwordSection.classList.contains('d-none')) {
            unsavedBar.classList.remove('active');
        }

        // Clear Skills Changes
        if (!skillsSection.classList.contains('d-none')) {
            // Reset to initial
            currentTeachSkills = [...INITIAL_TEACH_SKILLS];
            currentLearnSkills = [...INITIAL_LEARN_SKILLS];

            // Re-render
            const activeTab = document.getElementById('tabTeach').classList.contains('fw-bold') ? 'teach' : 'learn';
            renderSkills(activeTab);

            unsavedBar.classList.remove('active');
        }
    });

    function saveProfile() {
        const formData = new FormData(form);
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
                    captureInitialValues();
                    unsavedBar.classList.remove('active');

                    // Return to read-only
                    inputs.forEach(input => {
                        input.disabled = true;
                        if (input.type !== 'file' && input.type !== 'hidden' && input.tagName.toLowerCase() !== 'select') {
                            input.classList.add('form-control-plaintext');
                            input.classList.remove('form-control');
                        }
                    });
                    form.classList.remove('is-editing');
                    editBtn.classList.remove('d-none');
                    stopEditBtn.classList.add('d-none');
                } else {
                    showToast('Error updating profile: ' + data.message, 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showToast('An error occurred while saving.', 'error');
            })
            .finally(() => {
                saveBtn.innerText = originalText;
                saveBtn.disabled = false;
            });
    }

    // --- Password Logic ---
    const passwordForm = document.getElementById('passwordForm');
    const updatePassBtn = document.getElementById('updatePassBtn');
    const passInputs = passwordForm.querySelectorAll('input');

    // Show unsaved bar on password input?
    passInputs.forEach(input => {
        input.addEventListener('input', () => {
            // If any field has value, show bar? Or rely on Update button?
            // Screenshot implies sticky bar. Let's make typing show the bar.
            const hasVal = Array.from(passInputs).some(i => i.value.length > 0 && !i.readOnly);
            if (hasVal) {
                unsavedBar.classList.add('active');
                // Override save button to trigger password submit
                saveBtn.onclick = submitPasswordChange;
                // Update text if needed? "Save Changes" is generic enough.
            } else {
                unsavedBar.classList.remove('active');
            }
        });
    });

    // Allow the "Update Password" button in form to also trigger it
    updatePassBtn.addEventListener('click', submitPasswordChange);

    function submitPasswordChange() {
        const formData = new FormData(passwordForm);
        const newPass = formData.get('new_password');
        const confirmPass = formData.get('confirm_password');
        const currentPass = formData.get('current_password');

        if (!newPass || !confirmPass || !currentPass) {
            showToast('Please fill in all password fields.', 'warning');
            return;
        }

        if (newPass !== confirmPass) {
            showToast('New passwords do not match.', 'error');
            return;
        }

        // Password Complexity Check (Matching Auth Page)
        const strongRegex = /^(?=.*[A-Z])(?=.*[!@#$&*]).{8,}$/;
        if (!strongRegex.test(newPass)) {
            showToast('Password must have at least 8 characters, 1 uppercase letter, and 1 special character.', 'error');
            return;
        }

        // Use Save Btn for loading state feedback if bar is visible
        const OriginalBtnText = updatePassBtn.innerText;
        updatePassBtn.innerText = 'Updating...';
        updatePassBtn.disabled = true;
        saveBtn.innerText = 'Updating...';
        saveBtn.disabled = true;

        fetch('/settings/update_password', {
            method: 'POST',
            body: formData
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showToast('Password updated successfully!', 'success');
                    passwordForm.reset();
                    unsavedBar.classList.remove('active');
                } else {
                    showToast('Error: ' + data.message, 'error');
                }
            })
            .catch(err => {
                console.error(err);
                showToast('An error occurred.', 'error');
            })
            .finally(() => {
                updatePassBtn.innerText = OriginalBtnText;
                updatePassBtn.disabled = false;
                saveBtn.innerText = "Save Changes";
                saveBtn.disabled = false;
            });
    }

    // Default Save Button Handler (Profile)
    saveBtn.addEventListener('click', () => {
        // Fallback if onclick not set dynamically
        if (!passwordSection.classList.contains('d-none')) {
            submitPasswordChange();
        } else {
            saveProfile();
        }
    });


    // --- Skills Logic ---
    function getJsonData(id) {
        const el = document.getElementById(id);
        if (el) {
            try {
                return JSON.parse(el.textContent);
            } catch (e) {
                console.error('Error parsing JSON for ' + id, e);
                return [];
            }
        }
        return [];
    }

    const INITIAL_TEACH_SKILLS = getJsonData('data-teach-skills');
    const INITIAL_LEARN_SKILLS = getJsonData('data-learn-skills');
    const ALL_SKILLS = getJsonData('data-all-skills');

    let currentTeachSkills = [...INITIAL_TEACH_SKILLS];
    let currentLearnSkills = [...INITIAL_LEARN_SKILLS];
    const allAvailableSkills = [...ALL_SKILLS];

    // Elements
    const tabTeach = document.getElementById('tabTeach');
    const tabLearn = document.getElementById('tabLearn');
    const teachContainer = document.getElementById('teachContainer');
    const learnContainer = document.getElementById('learnContainer');

    // saveSkillsBtn removed from DOM

    if (tabTeach && tabLearn) {
        // Tab Switch
        tabTeach.addEventListener('click', () => {
            tabTeach.classList.add('fw-bold');
            tabTeach.classList.remove('text-muted');
            tabTeach.style.borderBottom = '2px solid black';

            tabLearn.classList.remove('fw-bold');
            tabLearn.classList.add('text-muted');
            tabLearn.style.borderBottom = 'none';

            teachContainer.classList.remove('d-none');
            learnContainer.classList.add('d-none');
            renderSkills('teach');
        });

        tabLearn.addEventListener('click', () => {
            tabLearn.classList.add('fw-bold');
            tabLearn.classList.remove('text-muted');
            tabLearn.style.borderBottom = '2px solid black';

            tabTeach.classList.remove('fw-bold');
            tabTeach.classList.add('text-muted');
            tabTeach.style.borderBottom = 'none';

            learnContainer.classList.remove('d-none');
            teachContainer.classList.add('d-none');
            renderSkills('learn');
        });
    }

    function renderSkills(type) {
        if (!document.getElementById(`${type}SelectedList`)) return;

        const selectedContainer = document.getElementById(`${type}SelectedList`);
        const suggestedContainer = document.getElementById(`${type}SuggestedList`);
        const currentSkills = type === 'teach' ? currentTeachSkills : currentLearnSkills;
        const emptyState = document.getElementById(`${type}EmptyState`);

        selectedContainer.innerHTML = '';
        suggestedContainer.innerHTML = '';

        // Render Selected
        if (currentSkills.length === 0) {
            emptyState.classList.remove('d-none');
        } else {
            emptyState.classList.add('d-none');
            currentSkills.forEach(skill => {
                const pill = createPill(skill, 'remove', type);
                selectedContainer.appendChild(pill);
            });
        }

        // Render Suggested (Filter out selected)
        const suggested = allAvailableSkills.filter(s => !currentSkills.includes(s));
        // Limit to 12
        suggested.slice(0, 12).forEach(skill => {
            const pill = createPill(skill, 'add', type);
            suggestedContainer.appendChild(pill);
        });
    }

    function createPill(text, action, type) {
        const pill = document.createElement('div');
        pill.className = `badge rounded-pill cursor-pointer user-select-none d-flex align-items-center gap-2 px-3 py-2`;
        // Style matching image (dark grey pills)
        pill.style.cssText = `background-color: #6b7280; color: white; font-weight: 500; font-size: 0.9rem; cursor: pointer; transition: background 0.2s;`;

        if (action === 'remove') {
            pill.innerHTML = `<span>${text}</span> <i class="bi bi-x-lg" style="font-size: 0.7em;"></i>`;
            pill.onclick = () => removeSkill(text, type);
            pill.onmouseover = () => pill.style.backgroundColor = '#dc2626'; // Red on hover
            pill.onmouseout = () => pill.style.backgroundColor = '#6b7280';
        } else {
            pill.innerHTML = `<i class="bi bi-plus-lg" style="font-size: 0.7em;"></i> <span>${text}</span>`;
            pill.onclick = () => addSkill(text, type);
            pill.onmouseover = () => pill.style.backgroundColor = '#4b5563'; // Slightly darker
            pill.onmouseout = () => pill.style.backgroundColor = '#6b7280';
        }
        return pill;
    }

    function addSkill(skill, type) {
        if (type === 'teach') {
            if (!currentTeachSkills.includes(skill)) {
                currentTeachSkills.push(skill);
                renderSkills('teach');
                checkSkillsChanges();
            }
        } else {
            if (!currentLearnSkills.includes(skill)) {
                currentLearnSkills.push(skill);
                renderSkills('learn');
                checkSkillsChanges();
            }
        }
    }

    function removeSkill(skill, type) {
        if (type === 'teach') {
            currentTeachSkills = currentTeachSkills.filter(s => s !== skill);
            renderSkills('teach');
            checkSkillsChanges();
        } else {
            currentLearnSkills = currentLearnSkills.filter(s => s !== skill);
            renderSkills('learn');
            checkSkillsChanges();
        }
    }

    // Custom Input Logic
    ['teach', 'learn'].forEach(type => {
        const input = document.getElementById(`${type}CustomInput`);
        if (input) {
            input.addEventListener('keypress', function (e) {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    const val = this.value.trim();
                    if (val) {
                        // Capitalize first letter?
                        const formatted = val.charAt(0).toUpperCase() + val.slice(1);
                        addSkill(formatted, type);
                        this.value = '';
                    }
                }
            });
        }
    });

    // Check changes for unsaved bar
    function checkSkillsChanges() {
        // Compare current with initial
        const teachChanged = JSON.stringify(currentTeachSkills.sort()) !== JSON.stringify(INITIAL_TEACH_SKILLS.sort());
        const learnChanged = JSON.stringify(currentLearnSkills.sort()) !== JSON.stringify(INITIAL_LEARN_SKILLS.sort());

        if (teachChanged || learnChanged) {
            unsavedBar.classList.add('active');
            saveBtn.onclick = saveSkills; // Reuse the sticky bar save button
        } else {
            unsavedBar.classList.remove('active');
        }
    }

    // Save Skills
    function saveSkills() {
        saveBtn.innerText = 'Saving...'; // Also update sticky bar button
        saveBtn.disabled = true;

        fetch('/settings/update_skills', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                teach_skills: currentTeachSkills,
                learn_skills: currentLearnSkills
            })
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showToast('Skills updated successfully!', 'success');
                    // Update initial state clones
                    INITIAL_TEACH_SKILLS.length = 0; INITIAL_TEACH_SKILLS.push(...currentTeachSkills);
                    INITIAL_LEARN_SKILLS.length = 0; INITIAL_LEARN_SKILLS.push(...currentLearnSkills);
                    unsavedBar.classList.remove('active');
                } else {
                    showToast('Error updating skills: ' + data.message, 'error');
                }
            })
            .catch(err => {
                console.error(err);
                showToast('An error occurred.', 'error');
            })
            .finally(() => {
                saveBtn.innerText = 'Save Changes';
                saveBtn.disabled = false;
            });
    }

    // --- Verification Logic ---
    const btnVerifyNow = document.getElementById('btnVerifyNow');
    if (btnVerifyNow && navVerification) {
        btnVerifyNow.addEventListener('click', (e) => {
            e.preventDefault();
            navVerification.click(); // Trigger section switch
        });
    }

    const verificationFile = document.getElementById('verificationFile');
    const uploadZone = document.getElementById('uploadZone');
    const uploadPlaceholder = document.getElementById('uploadPlaceholder');
    const uploadPreviewContainer = document.getElementById('uploadPreviewContainer');
    const uploadPreview = document.getElementById('uploadPreview');
    const submitVerificationBtn = document.getElementById('submitVerificationBtn');

    let selectedVerificationFile = null;

    function handleVerificationFile(file) {
        selectedVerificationFile = file;
        const reader = new FileReader();
        reader.onload = function (e) {
            if (uploadPreview) uploadPreview.src = e.target.result;
            if (uploadPlaceholder) uploadPlaceholder.classList.add('d-none');
            if (uploadPreviewContainer) uploadPreviewContainer.classList.remove('d-none');
            if (submitVerificationBtn) {
                submitVerificationBtn.disabled = false;
                submitVerificationBtn.style.backgroundColor = '#1f2937'; // Active dark color
            }
        };
        reader.readAsDataURL(file);
    }

    if (verificationFile) {
        verificationFile.addEventListener('change', function () {
            if (this.files && this.files[0]) {
                handleVerificationFile(this.files[0]);
            }
        });
    }

    if (uploadZone) {
        uploadZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            e.stopPropagation();
            uploadZone.style.backgroundColor = '#e5e7eb';
            uploadZone.style.borderColor = '#6b7280';
        });

        uploadZone.addEventListener('dragleave', (e) => {
            e.preventDefault();
            e.stopPropagation();
            uploadZone.style.backgroundColor = '#f3f4f6';
            uploadZone.style.borderColor = '#e5e7eb';
        });

        uploadZone.addEventListener('drop', (e) => {
            e.preventDefault();
            e.stopPropagation();
            uploadZone.style.backgroundColor = '#f3f4f6';
            uploadZone.style.borderColor = '#e5e7eb';

            if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files[0]) {
                const file = e.dataTransfer.files[0];
                if (file.type.startsWith('image/')) {
                    // Sync with input if possible, but rely on selectedVerificationFile
                    try {
                        verificationFile.files = e.dataTransfer.files;
                    } catch (err) {
                        console.log("Browser doesn't support setting input files via JS, using variable fallback");
                    }
                    handleVerificationFile(file);
                } else {
                    showToast('Please upload an image file (JPG, PNG).', 'error');
                }
            }
        });
    }

    if (submitVerificationBtn) {
        submitVerificationBtn.addEventListener('click', function () {
            // Use the variable if set (drag drop), else input (click sel)
            const file = selectedVerificationFile || (verificationFile.files.length > 0 ? verificationFile.files[0] : null);

            if (!file) {
                showToast('Please select a file first.', 'warning');
                return;
            }

            const formData = new FormData();
            formData.append('verificationPhoto', file);

            const originalText = this.innerText;
            this.innerText = 'Uploading...';
            this.disabled = true;

            fetch('/settings/upload_verification', {
                method: 'POST',
                body: formData
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        showToast('Verification document uploaded! Pending review.', 'success');
                        setTimeout(() => location.reload(), 1500);
                    } else {
                        showToast('Error uploading: ' + data.message, 'error');
                        this.innerText = originalText;
                        this.disabled = false;
                    }
                })
                .catch(err => {
                    console.error(err);
                    showToast('An error occurred.', 'error');
                    this.innerText = originalText;
                    this.disabled = false;
                });
        });
    }

});
