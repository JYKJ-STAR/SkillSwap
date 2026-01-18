/**
 * Auth Page JavaScript
 * 
 * Takes dependency on global API_URLS object defined in auth.html:
 * const API_URLS = {
 *     checkEmail: "...",
 *     checkPhone: "...",
 *     register: "...",
 *     loginPage: "..."
 * };
 */

// Tab switching logic
function switchTab(tab) {
    const tabs = document.querySelectorAll('.auth-tab');
    // If switching to login, show loginSection and login tab active
    if (tab === 'login') {
        tabs[0].classList.add('active');
        tabs[1].classList.remove('active');
        document.getElementById('loginSection').classList.add('active');
        document.getElementById('signupSection').classList.remove('active');
    } else {
        tabs[1].classList.add('active');
        tabs[0].classList.remove('active');
        document.getElementById('signupSection').classList.add('active');
        document.getElementById('loginSection').classList.remove('active');
    }
}

/* --- Multi-Step Signup Logic --- */
let currentStep = 1;
const totalSteps = 4;
let selectedRole = null; // Default null to force selection
let teachSkills = [];
let learnSkills = [];

// Role Selection
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.role-card').forEach(card => {
        card.addEventListener('click', function () {
            document.querySelectorAll('.role-card').forEach(c => c.classList.remove('selected'));
            this.classList.add('selected');
            this.querySelector('input').checked = true;
            selectedRole = this.querySelector('input').value; // 'youth' or 'senior'
        });
    });

    // Skill Tags
    document.querySelectorAll('.skill-tag').forEach(tag => {
        tag.addEventListener('click', function () {
            this.classList.toggle('selected');
            const skill = this.dataset.skill;
            const isTeach = this.closest('.skill-column').classList.contains('teach');

            if (this.classList.contains('selected')) {
                isTeach ? teachSkills.push(skill) : learnSkills.push(skill);
            } else {
                if (isTeach) {
                    teachSkills = teachSkills.filter(s => s !== skill);
                } else {
                    learnSkills = learnSkills.filter(s => s !== skill);
                }
            }
        });
    });

    // File Upload and Drag & Drop
    const uploadZone = document.getElementById('uploadZone');
    const fileInput = document.getElementById('fileInput');
    const fileName = document.getElementById('fileName');

    if (uploadZone) {
        uploadZone.addEventListener('click', () => fileInput.click());

        fileInput.addEventListener('change', (e) => {
            handleFiles(e.target.files);
        });

        // Drag & Drop
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            uploadZone.addEventListener(eventName, preventDefaults, false);
        });

        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }

        ['dragenter', 'dragover'].forEach(eventName => {
            uploadZone.addEventListener(eventName, () => uploadZone.classList.add('dragover'), false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            uploadZone.addEventListener(eventName, () => uploadZone.classList.remove('dragover'), false);
        });

        uploadZone.addEventListener('drop', (e) => {
            const dt = e.dataTransfer;
            const files = dt.files;
            fileInput.files = files; // Update input files
            handleFiles(files);
        });

        function handleFiles(files) {
            if (files.length) {
                const file = files[0];
                if (file.size > 5 * 1024 * 1024) {
                    showToast('File too large. Maximum size is 5MB.', 'error');
                    fileInput.value = ''; // Clear input
                    return;
                }
                fileName.textContent = file.name;
                uploadZone.classList.add('has-file');
            }
        }
    }
});

// Navigation
function updateSteps() {
    document.querySelectorAll('.step-content').forEach(el => el.classList.remove('active'));
    document.getElementById(`step${currentStep}`).classList.add('active');
    // Update Title and Progress
    document.getElementById('stepTitle').textContent = `Create Account (${currentStep}/${totalSteps})`;
    document.getElementById('progressFill').style.width = `${(currentStep / totalSteps) * 100}%`;

    // Scroll to top of signup section
    document.getElementById('signupSection').scrollIntoView({ behavior: 'smooth' });
}

async function validateStep(step) {
    if (step === 1) {
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;

        if (!selectedRole) {
            showToast('Please select whether you are a Youth or Senior.', 'warning'); return false;
        }
        if (!email || !password) {
            showToast('Please enter your email and password.', 'warning'); return false;
        }

        // Email format validation
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            showToast('Please enter a valid email address.', 'error');
            return false;
        }

        // Password Complexity Check
        const strongRegex = /^(?=.*[A-Z])(?=.*[!@#$&*]).{8,}$/;

        if (!strongRegex.test(password)) {
            showToast('Password must have at least 8 characters, 1 uppercase letter, and 1 special character.', 'error');
            return false;
        }

        // Check email uniqueness
        try {
            const response = await fetch(API_URLS.checkEmail, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email: email })
            });
            const data = await response.json();
            if (data.exists) {
                showToast('This email is already registered. Please log in or use a different email.', 'warning');
                return false;
            }
        } catch (e) {
            console.error("Email check failed", e);
            showToast('Unable to verify email availability. Please try again.', 'error');
            return false;
        }

    } else if (step === 2) {
        const phone = document.getElementById('phone').value;
        if (!document.getElementById('firstName').value || !document.getElementById('lastName').value) {
            showToast('Please enter your name.', 'warning'); return false;
        }
        if (!document.getElementById('age').value || !document.getElementById('schoolProfession').value || !document.getElementById('language').value) {
            showToast('Please complete all required fields.', 'warning'); return false;
        }

        // Age validation based on role
        const age = parseInt(document.getElementById('age').value);
        let minAge = 12;
        let maxAge = 80;

        if (selectedRole === 'youth') {
            minAge = 15;
            maxAge = 35;
        } else if (selectedRole === 'senior') {
            minAge = 36;
            maxAge = 80;
        }

        if (age < minAge || age > maxAge) {
            showToast(`For ${selectedRole === 'youth' ? 'Youth' : 'Seniors'}, age must be between ${minAge} and ${maxAge} years.`, 'error');
            return false;
        }

        // Phone Validation (8 digits, starts with 8 or 9)
        const phoneRegex = /^[89]\d{7}$/;
        if (!phone || !phoneRegex.test(phone)) {
            showToast('Phone number must be 8 digits and start with 8 or 9.', 'error'); return false;
        }

        // Check phone uniqueness
        try {
            const response = await fetch(API_URLS.checkPhone, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ phone: phone })
            });
            const data = await response.json();
            if (data.exists) {
                showToast('This phone number is already registered. Please use a different number.', 'warning');
                return false;
            }
        } catch (e) {
            console.error("Phone check failed", e);
            showToast('Unable to verify phone availability. Please try again.', 'error');
            return false;
        }
    } else if (step === 3) {
        // Check if at least one skill is selected (teach or learn)
        const customTeach = document.getElementById('teachCustom').value.trim();
        const customLearn = document.getElementById('learnCustom').value.trim();
        const totalSkills = teachSkills.length + learnSkills.length + (customTeach ? 1 : 0) + (customLearn ? 1 : 0);

        if (totalSkills === 0) {
            showToast('Please select at least one skill to teach or learn.', 'warning');
            return false;
        }
    }
    return true;
}

async function nextStep(step) {
    const isValid = await validateStep(step);
    if (!isValid) return;

    currentStep = step + 1;

    // Dynamic labels for step 2
    if (currentStep === 2) {
        const label = document.getElementById('schoolProfessionLabel');
        const input = document.getElementById('schoolProfession');
        const ageInput = document.getElementById('age');

        if (selectedRole === 'youth') {
            label.textContent = 'School / University OR Profession';
            input.placeholder = 'School / Profession';
            ageInput.min = 15;
            ageInput.max = 35;
            ageInput.placeholder = "Age (15-35)";
        } else {
            label.textContent = 'Current or Former Profession';
            input.placeholder = 'Profession';
            ageInput.min = 36;
            ageInput.max = 80;
            ageInput.placeholder = "Age (36-80)";
        }
    }
    updateSteps();
}

function prevStep(step) {
    currentStep = step - 1;
    updateSteps();
}

async function submitForm(hasVerification) {
    // Validate step 3 (skills) before submitting
    const isValid = await validateStep(3);
    if (!isValid) return;

    // Require photo if user clicked "Submit and Finish" (hasVerification = true)
    const fileInput = document.getElementById('fileInput');
    if (hasVerification) {
        if (!fileInput.files || fileInput.files.length === 0) {
            showToast('Please upload a photo ID to complete verification.', 'warning');
            return;
        }
    }

    // Use FormData for file upload
    const formData = new FormData();
    formData.append('role', selectedRole === 'senior' ? 'senior' : 'youth');
    formData.append('email', document.getElementById('email').value);
    formData.append('password', document.getElementById('password').value);
    formData.append('firstName', document.getElementById('firstName').value);
    formData.append('lastName', document.getElementById('lastName').value);
    formData.append('age', document.getElementById('age').value);
    formData.append('phone', document.getElementById('phone') ? document.getElementById('phone').value : '');
    formData.append('schoolProfession', document.getElementById('schoolProfession').value);
    formData.append('language', document.getElementById('language').value);

    // Combine tags and custom inputs for skills
    const finalTeachSkills = teachSkills.concat(document.getElementById('teachCustom').value ? [document.getElementById('teachCustom').value] : []);
    const finalLearnSkills = learnSkills.concat(document.getElementById('learnCustom').value ? [document.getElementById('learnCustom').value] : []);

    // Send as JSON strings to be easier to parse on backend with simple FormData
    formData.append('teachSkills', JSON.stringify(finalTeachSkills));
    formData.append('learnSkills', JSON.stringify(finalLearnSkills));
    formData.append('hasVerification', hasVerification);

    // Append file if present
    if (fileInput.files.length > 0) {
        formData.append('verificationPhoto', fileInput.files[0]);
    }

    try {
        const response = await fetch(API_URLS.register, {
            method: 'POST',
            // No Content-Type header - fetch adds it automatically for FormData (multipart/form-data)
            body: formData
        });

        if (response.redirected) {
            window.location.href = API_URLS.loginPage;
        } else {
            const resData = await response.json();
            if (resData.error) {
                showToast('Registration failed: ' + resData.error, 'error');
            } else {
                // Success -> Redirect to Login
                window.location.href = API_URLS.loginPage;
            }
        }
    } catch (error) {
        console.error('Error:', error);
        showToast('An error occurred during registration. Please try again.', 'error');
    }
}
