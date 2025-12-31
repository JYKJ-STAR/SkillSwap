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

    // File Upload
    const uploadZone = document.getElementById('uploadZone');
    const fileInput = document.getElementById('fileInput');
    const fileName = document.getElementById('fileName');

    if (uploadZone) {
        uploadZone.addEventListener('click', () => fileInput.click());
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length) {
                const file = e.target.files[0];
                if (file.size > 5 * 1024 * 1024) {
                    alert('File too large (>5MB)'); return;
                }
                fileName.textContent = file.name;
                uploadZone.classList.add('has-file');
            }
        });
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
            alert('Please select whether you are a Youth or Senior'); return false;
        }
        if (!email || !password) {
            alert('Please enter email and password'); return false;
        }

        // Password Complexity Check
        const strongRegex = /^(?=.*[A-Z])(?=.*[!@#$&*]).{8,}$/;

        if (!strongRegex.test(password)) {
            alert('Password must have at least 8 characters, 1 Uppercase letter, and 1 Special character.');
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
                alert('This email is already registered. Please log in or use a different email.');
                return false;
            }
        } catch (e) {
            console.error("Email check failed", e);
            alert('Unable to verify email availability. Please try again.');
            return false;
        }

    } else if (step === 2) {
        const phone = document.getElementById('phone').value;
        if (!document.getElementById('firstName').value || !document.getElementById('lastName').value) {
            alert('Please enter your name'); return false;
        }
        if (!document.getElementById('age').value || !document.getElementById('schoolProfession').value || !document.getElementById('language').value) {
            alert('Please complete all fields'); return false;
        }

        // Phone Validation (8 digits)
        const phoneRegex = /^\d{8}$/;
        if (!phone || !phoneRegex.test(phone)) {
            alert('Phone number must be exactly 8 digits.'); return false;
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
                alert('This phone number is already registered. Please use a different number.');
                return false;
            }
        } catch (e) {
            console.error("Phone check failed", e);
            alert('Unable to verify phone availability. Please try again.');
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
        if (selectedRole === 'youth') {
            label.textContent = 'School / University OR Profession';
            input.placeholder = 'School / Profession';
        } else {
            label.textContent = 'Current or Former Profession';
            input.placeholder = 'Profession';
        }
    }
    updateSteps();
}

function prevStep(step) {
    currentStep = step - 1;
    updateSteps();
}

async function submitForm(hasVerification) {
    // Require photo if user clicked "Submit and Finish" (hasVerification = true)
    if (hasVerification) {
        const fileInput = document.getElementById('fileInput');
        if (!fileInput.files || fileInput.files.length === 0) {
            alert('Please upload a photo ID to complete verification.');
            return;
        }
    }

    const data = {
        // Determine the correct role string for backend
        role: selectedRole === 'senior' ? 'senior' : 'youth',
        email: document.getElementById('email').value,
        password: document.getElementById('password').value,
        firstName: document.getElementById('firstName').value,
        lastName: document.getElementById('lastName').value,
        age: document.getElementById('age').value,
        phone: document.getElementById('phone') ? document.getElementById('phone').value : '',
        schoolProfession: document.getElementById('schoolProfession').value,
        language: document.getElementById('language').value,
        teachSkills: teachSkills.concat(document.getElementById('teachCustom').value ? [document.getElementById('teachCustom').value] : []),
        learnSkills: learnSkills.concat(document.getElementById('learnCustom').value ? [document.getElementById('learnCustom').value] : []),
        hasVerification: hasVerification
    };

    try {
        const response = await fetch(API_URLS.register, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        if (response.redirected) {
            window.location.href = API_URLS.loginPage;
        } else {
            const resData = await response.json();
            if (resData.error) {
                alert('Registration failed: ' + resData.error);
            } else {
                // Success -> Redirect to Login
                window.location.href = API_URLS.loginPage;
            }
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred during registration.');
    }
}
