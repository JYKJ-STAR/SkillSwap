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
// Role Selection Logic
/**
 * Initializes click handlers for Role Cards.
 * Manages selection state and updates 'selectedRole'.
 */
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
// Skill Tags Logic
/**
 * Initializes click handlers for Skill Tags (Teach/Learn).
 * Manages selection arrays: 'teachSkills' and 'learnSkills'.
 */
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
// Update step visibility and progress bar
/**
 * Updates the UI to reflect the current step in the process.
 */
function updateSteps() {
    document.querySelectorAll('.step-content').forEach(el => el.classList.remove('active'));
    document.getElementById(`step${currentStep}`).classList.add('active');
    document.getElementById('stepTitle').textContent = `Complete Profile (${currentStep}/${totalSteps})`;
    document.getElementById('progressFill').style.width = `${(currentStep / totalSteps) * 100}%`;
}

// Calculate age from birth date
// Calculate age from birth date
/**
 * Helper: Calculates age based on birth date string.
 * @param {string} birthDateString 
 * @returns {number} Age
 */
function calculateAge(birthDateString) {
    const birthDate = new Date(birthDateString);
    const today = new Date();
    let age = today.getFullYear() - birthDate.getFullYear();
    const m = today.getMonth() - birthDate.getMonth();
    if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) {
        age--;
    }
    return age;
}

// Validate current step
// Validate current step
/**
 * Validates inputs for the specified step.
 * Checks for required fields and applies logic rules (e.g., Age limits).
 * 
 * @param {number} step 
 * @returns {boolean} True if valid
 */
function validateStep(step) {
    if (step === 1) {
        if (!selectedRole) {
            showToast('Please select a role to continue.', 'warning');
            return false;
        }
    } else if (step === 2) {
        if (!document.getElementById('firstName').value || !document.getElementById('lastName').value ||
            !document.getElementById('birth_date').value || !document.getElementById('schoolProfession').value ||
            !document.getElementById('language').value || !document.getElementById('phone').value) {
            showToast('Please complete all required fields.', 'warning');
            return false;
        }
        const phone = document.getElementById('phone').value;
        const birthDateInput = document.getElementById('birth_date');
        const age = calculateAge(birthDateInput.value);

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
            showToast(`For ${selectedRole === 'youth' ? 'Youth' : 'Seniors'}, you must be between ${minAge} and ${maxAge} years old (Your age: ${age}).`, 'error');
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
// Navigate to next step
/**
 * Proceed to the next step if validation passes.
 * Updates dynamic constraints for Step 2 based on chosen Role.
 * @param {number} step 
 */
function nextStep(step) {
    if (!validateStep(step)) return;
    currentStep = step + 1;

    // Dynamic labels for step 2
    if (currentStep === 2) {
        const label = document.getElementById('schoolProfessionLabel');
        const input = document.getElementById('schoolProfession');
        const birthDateInput = document.getElementById('birth_date');

        const today = new Date();
        const formatDate = (date) => date.toISOString().split('T')[0];

        let minYearDiff, maxYearDiff;

        if (selectedRole === 'youth') {
            label.innerHTML = '<i class="bi bi-mortarboard-fill"></i> School/University';
            input.placeholder = 'School / Profession';
            minYearDiff = 15;
            maxYearDiff = 35;
        } else {
            label.innerHTML = '<i class="bi bi-briefcase-fill"></i> Profession';
            input.placeholder = 'Profession';
            minYearDiff = 36;
            maxYearDiff = 80;
        }

        const maxDate = new Date(today.getFullYear() - minYearDiff, today.getMonth(), today.getDate());
        const minDate = new Date(today.getFullYear() - maxYearDiff, today.getMonth(), today.getDate());

        birthDateInput.max = formatDate(maxDate);
        birthDateInput.min = formatDate(minDate);
    }

    updateSteps();
}

// Navigate to previous step
function prevStep(step) {
    currentStep = step - 1;
    updateSteps();
}

// Submit the form
// Submit the form
/**
 * Submits the Google Signup completion form via AJAX.
 * Sends all collected data (Role, Details, Skills) to the backend.
 */
async function submitGoogleSignup() {
    // Validate step 3 before submitting
    if (!validateStep(3)) return;
    const data = {
        role: selectedRole,
        firstName: document.getElementById('firstName').value,
        lastName: document.getElementById('lastName').value,
        birthDate: document.getElementById('birth_date').value,
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
