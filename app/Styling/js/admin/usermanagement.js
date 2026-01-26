/**
 * User Management Page JavaScript
 * Handles filtering, user actions, and modals for the admin user management page
 */

document.addEventListener('DOMContentLoaded', function () {
    // Initialize filter functionality
    initializeFilters();

    // Initialize all button handlers
    initializeVerificationButtons();
    initializeEditButtons();
    initializeDeleteButtons();
});

// =====================================================
// FILTER FUNCTIONALITY
// =====================================================

/**
 * Initialize filter tab click handlers
 */
function initializeFilters() {
    const filterTabs = document.querySelectorAll('.filter-tab');

    filterTabs.forEach(tab => {
        tab.addEventListener('click', function () {
            // Update active state
            filterTabs.forEach(t => t.classList.remove('active'));
            this.classList.add('active');

            // Apply filter
            const filter = this.dataset.filter;
            filterUsers(filter);
        });
    });
}

/**
 * Filter users in the table based on role or verification status
 * @param {string} filter - 'all', 'senior', 'youth', or 'unverified'
 */
function filterUsers(filter) {
    const rows = document.querySelectorAll('#usersTableBody tr[data-role]');

    rows.forEach(row => {
        const role = row.dataset.role;
        const status = row.dataset.status;

        let show = false;

        switch (filter) {
            case 'all':
                show = true;
                break;
            case 'senior':
                show = role === 'senior';
                break;
            case 'youth':
                show = role === 'youth';
                break;
            case 'unverified':
                show = status !== 'verified';
                break;
            default:
                show = true;
        }

        row.style.display = show ? '' : 'none';
    });
}

// =====================================================
// VERIFICATION MODAL
// =====================================================

/**
 * Initialize verification button handlers
 */
function initializeVerificationButtons() {
    document.querySelectorAll('.verify-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            const userId = this.dataset.userId;
            const userName = this.dataset.userName;
            const joinDate = this.dataset.joinDate;
            const photo = this.dataset.photo;

            openVerifyModal(userId, userName, joinDate, photo);
        });
    });
}

/**
 * Open the verification modal with user data
 */
/**
 * Open the verification modal with user data.
 * Populates fields and sets form actions for Approve/Reject.
 * Handles display logic for existing vs missing photo.
 * 
 * @param {string} userId - ID of the user
 * @param {string} userName - Name of the user
 * @param {string} joinDate - Formatted join date
 * @param {string} photo - Filename of the verification photo
 */
function openVerifyModal(userId, userName, joinDate, photo) {
    // Set user info
    document.getElementById('verifyUserName').textContent = userName;
    document.getElementById('verifyJoinDate').textContent = joinDate;

    // Set form actions
    document.getElementById('approveForm').action = `/admin/verify-user/${userId}`;
    document.getElementById('rejectForm').action = `/admin/reject-verification/${userId}`;

    // Handle photo display
    const photoContainer = document.getElementById('verifyPhotoContainer');
    const noPhotoMessage = document.getElementById('noPhotoMessage');
    const photoLink = document.getElementById('verifyPhotoLink');

    if (photo && photo.trim() !== '') {
        // Photo exists
        photoContainer.style.display = 'flex';
        noPhotoMessage.style.display = 'none';
        photoLink.href = `/Styling/img/users/verification/${photo}`;
    } else {
        // No photo
        photoContainer.style.display = 'none';
        noPhotoMessage.style.display = 'flex';
    }

    // Show modal
    document.getElementById('verifyModal').classList.add('active');
}

/**
 * Close the verification modal
 */
function closeVerifyModal() {
    document.getElementById('verifyModal').classList.remove('active');
}

// =====================================================
// EDIT USER MODAL
// =====================================================

/**
 * Initialize edit button handlers
 */
function initializeEditButtons() {
    document.querySelectorAll('.edit-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            const userId = this.dataset.userId;
            const userName = this.dataset.userName;
            const userEmail = this.dataset.userEmail;

            openEditModal(userId, userName, userEmail);
        });
    });
}

/**
 * Open the edit modal with user data
 */
/**
 * Open the edit modal with user data.
 * Populates name and email fields for editing.
 * 
 * @param {string} userId 
 * @param {string} userName 
 * @param {string} userEmail 
 */
function openEditModal(userId, userName, userEmail) {
    // Set form action
    document.getElementById('editForm').action = `/admin/edit-user/${userId}`;

    // Populate form fields
    document.getElementById('editUserName').value = userName;
    document.getElementById('editUserEmail').value = userEmail;

    // Show modal
    document.getElementById('editModal').classList.add('active');
}

/**
 * Close the edit modal
 */
function closeEditModal() {
    document.getElementById('editModal').classList.remove('active');
}

// =====================================================
// DELETE USER MODAL
// =====================================================

/**
 * Initialize delete button handlers
 */
function initializeDeleteButtons() {
    document.querySelectorAll('.delete-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            const userId = this.dataset.userId;
            const userName = this.dataset.userName;

            openDeleteModal(userId, userName);
        });
    });
}

/**
 * Open the delete confirmation modal
 */
/**
 * Open the delete confirmation modal.
 * Sets the form action to delete the specific user.
 * 
 * @param {string} userId 
 * @param {string} userName 
 */
function openDeleteModal(userId, userName) {
    // Set form action
    document.getElementById('deleteForm').action = `/admin/delete-user/${userId}`;

    // Set user name display
    document.getElementById('deleteUserName').textContent = userName;

    // Show modal
    document.getElementById('deleteModal').classList.add('active');
}

/**
 * Close the delete modal
 */
function closeDeleteModal() {
    document.getElementById('deleteModal').classList.remove('active');
}

// =====================================================
// MODAL UTILITIES
// =====================================================

// Close modals when clicking outside
document.addEventListener('click', function (e) {
    if (e.target.classList.contains('modal-overlay')) {
        closeVerifyModal();
        closeEditModal();
        closeDeleteModal();
    }
});

// Close modals with Escape key
document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
        closeVerifyModal();
        closeEditModal();
        closeDeleteModal();
    }
});
