// =====================================================
// MANAGE EVENTS PAGE JAVASCRIPT
// =====================================================

// Create Modal Functions
function openCreateModal() {
    document.getElementById('createModal').classList.add('active');
}

function closeCreateModal() {
    document.getElementById('createModal').classList.remove('active');
}

// Edit Modal Functions
function openEditModal(eventId, title, datetime, location, category, status, ledBy, maxCapacity, mentorCapacity, participantCapacity, description, grcId) {
    const modal = document.getElementById('editModal');
    const form = document.getElementById('editForm');

    // Set form action
    form.action = '/admin/update-event/' + eventId;

    // Populate fields
    document.getElementById('edit_title').value = title || '';
    document.getElementById('edit_location').value = location || '';
    document.getElementById('edit_category').value = category || 'social_games';
    document.getElementById('edit_status').value = status || 'open';
    document.getElementById('edit_led_by').value = ledBy || 'employee';
    document.getElementById('edit_max_capacity').value = maxCapacity || '';

    // Populate New Capacity Fields
    document.getElementById('edit_mentor_capacity').value = mentorCapacity || 5;
    document.getElementById('edit_participant_capacity').value = participantCapacity || 15;

    document.getElementById('edit_description').value = description || '';
    document.getElementById('edit_grc').value = grcId || '';

    // Handle datetime (convert from string format to datetime-local format)
    if (datetime && datetime !== 'None') {
        // datetime might be in format "2025-01-20 10:00:00" or similar
        const dt = datetime.replace(' ', 'T').substring(0, 16);
        document.getElementById('edit_datetime').value = dt;
    } else {
        document.getElementById('edit_datetime').value = '';
    }

    modal.classList.add('active');
}

function closeEditModal() {
    document.getElementById('editModal').classList.remove('active');
}

// Close modal when clicking outside
document.addEventListener('DOMContentLoaded', function () {
    const modals = document.querySelectorAll('.modal-overlay');

    modals.forEach(modal => {
        modal.addEventListener('click', function (e) {
            if (e.target === modal) {
                modal.classList.remove('active');
            }
        });
    });

    // Close modal with Escape key
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') {
            modals.forEach(modal => {
                modal.classList.remove('active');
            });
        }
    });

    // Event delegation for edit buttons
    document.querySelectorAll('.edit-event-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            const eventId = this.dataset.eventId;
            const title = this.dataset.title;
            const datetime = this.dataset.datetime;
            const location = this.dataset.location;
            const category = this.dataset.category;
            const status = this.dataset.status;
            const ledBy = this.dataset.ledBy;
            const maxCapacity = this.dataset.maxCapacity;

            // New Capacity Data Attributes
            const mentorCapacity = this.dataset.mentorCapacity;
            const participantCapacity = this.dataset.participantCapacity;

            const description = this.dataset.description;
            const grcId = this.dataset.grcId;

            openEditModal(eventId, title, datetime, location, category, status, ledBy, maxCapacity, mentorCapacity, participantCapacity, description, grcId);
        });
    });
});
