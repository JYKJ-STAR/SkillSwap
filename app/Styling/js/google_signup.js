/**
 * Google Signup Page JavaScript
 * Multi-step form for completing Google OAuth signup
 */

// State variables
let currentStep = 1;
const totalSteps = 3;
let selectedRole = null;
let teachSkills = [];
let learnSkills = [];

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    initializeRoleSelection();
    initializeSkillTags();
});

// Role Selection Logic
function initializeRoleSelection() {
    document.querySelectorAll('.role-card').forEach(card => {
        card.addEventListener('click', function () {
            document.querySelectorAll('.role-card').forEach(c => c.classList.remove('selected'));
            this.classList.add('selected');
            this.querySelector('input').checked = true;
            selectedRole = this.querySelector('input').value;
        });
    });
}

// Skill Tags Logic
function initializeSkillTags() {
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
}

// Update step visibility and progress bar
function updateSteps() {
    document.querySelectorAll('.step-content').forEach(el => el.classList.remove('active'));
    document.getElementById(`step${currentStep}`).classList.add('active');
    document.getElementById('stepTitle').textContent = `Complete Profile (${currentStep}/${totalSteps})`;
    document.getElementById('progressFill').style.width = `${(currentStep / totalSteps) * 100}%`;
}

// Validate current step
function validateStep(step) {
    if (step === 1) {
        if (!selectedRole) {
            showToast('Please select a role to continue.', 'warning');
            return false;
        }
    } else if (step === 2) {
        if (!document.getElementById('firstName').value || !document.getElementById('lastName').value ||
            !document.getElementById('age').value || !document.getElementById('schoolProfession').value ||
            !document.getElementById('language').value || !document.getElementById('phone').value) {
            showToast('Please complete all required fields.', 'warning');
            return false;
        }
        const phone = document.getElementById('phone').value;
        const age = parseInt(document.getElementById('age').value);

        // Age validation based on role
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

        // Phone validation (8 digits, starts with 8 or 9)
        if (!/^[89]\d{7}$/.test(phone)) {
            showToast('Phone number must be 8 digits and start with 8 or 9.', 'error');
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

// Navigate to next step
function nextStep(step) {
    if (!validateStep(step)) return;
    currentStep = step + 1;

    // Dynamic labels for step 2
    if (currentStep === 2) {
        const label = document.getElementById('schoolProfessionLabel');
        const input = document.getElementById('schoolProfession');
        const ageInput = document.getElementById('age');

        if (selectedRole === 'youth') {
            label.innerHTML = '<i class="bi bi-mortarboard-fill"></i> School/University';
            input.placeholder = 'School / Profession';
            ageInput.min = 15;
            ageInput.max = 35;
            ageInput.placeholder = "Age (15-35)";
        } else {
            label.innerHTML = '<i class="bi bi-briefcase-fill"></i> Profession';
            input.placeholder = 'Profession';
            ageInput.min = 36;
            ageInput.max = 80;
            ageInput.placeholder = "Age (36-80)";
        }
    }

    updateSteps();
}

// Navigate to previous step
function prevStep(step) {
    currentStep = step - 1;
    updateSteps();
}

// Submit the form
async function submitGoogleSignup() {
    // Validate step 3 before submitting
    if (!validateStep(3)) return;
    const data = {
        role: selectedRole,
        firstName: document.getElementById('firstName').value,
        lastName: document.getElementById('lastName').value,
        age: document.getElementById('age').value,
        phone: document.getElementById('phone').value,
        schoolProfession: document.getElementById('schoolProfession').value,
        language: document.getElementById('language').value,
        teachSkills: teachSkills.concat(document.getElementById('teachCustom').value ? [document.getElementById('teachCustom').value] : []),
        learnSkills: learnSkills.concat(document.getElementById('learnCustom').value ? [document.getElementById('learnCustom').value] : [])
    };

    try {
        const response = await fetch(SUBMIT_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        const resData = await response.json();
        if (response.ok && resData.redirect) {
            window.location.href = resData.redirect;
        } else {
            showToast('Signup failed: ' + (resData.error || 'Unknown error'), 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showToast('An error occurred. Please try again.', 'error');
    }
}
