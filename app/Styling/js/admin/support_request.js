// Sample ticket data
let adminTickets = [
    {
        id: 'TT-882',
        user: 'John Doe',
        type: 'Harassment',
        date: '26 - 8 - 2025',
        priority: 'High',
        event: 'Artistic',
        status: 'progress',
        description: 'User reported receiving harassing messages from another participant during the event.',
        reply: ''
    },
    {
        id: 'TT-883',
        user: 'John Doe',
        type: 'Technical',
        date: '26 - 8 - 2025',
        priority: 'High',
        event: 'Artistic',
        status: 'resolved',
        description: 'User experienced technical difficulties while trying to join the virtual event.',
        reply: 'We have identified the issue with the event platform and resolved it. The user has been given access to the event recording.'
    },
    {
        id: 'TT-884',
        user: 'John Doe',
        type: 'Scam',
        date: '26 - 8 - 2025',
        priority: 'High',
        event: 'Artistic',
        status: 'resolved',
        description: 'User reported a suspicious account trying to collect personal information.',
        reply: 'The suspicious account has been banned and all affected users have been notified. Thank you for your report.'
    },
    {
        id: 'TT-885',
        user: 'John Doe',
        type: 'Harassment',
        date: '26 - 8 - 2025',
        priority: 'High',
        event: 'Artistic',
        status: 'progress',
        description: 'Inappropriate behavior reported during the networking session.',
        reply: ''
    },
    {
        id: 'TT-886',
        user: 'John Doe',
        type: 'Harassment',
        date: '26 - 8 - 2025',
        priority: 'High',
        event: 'Artistic',
        status: 'progress',
        description: 'User felt uncomfortable due to persistent unwanted contact from another attendee.',
        reply: ''
    },
    {
        id: 'TT-887',
        user: 'John Doe',
        type: 'Harassment',
        date: '26 - 8 - 2025',
        priority: 'High',
        event: 'Artistic',
        status: 'progress',
        description: 'Multiple users reported the same individual for disruptive behavior.',
        reply: ''
    }
];

let currentFilter = 'all';
let currentTicketIndex = null;

function viewTicketDetails(button) {
    const description = button.getAttribute('data-description');
    if (description) {
        alert(description);
    }
}

function renderTickets() {
    const tbody = document.getElementById('tickets-tbody');
    tbody.innerHTML = '';

    const filteredTickets = adminTickets.filter(ticket => {
        if (currentFilter === 'all') return true;
        if (currentFilter === 'pending') return ticket.status === 'progress';
        if (currentFilter === 'resolved') return ticket.status === 'resolved';
        return true;
    });

    filteredTickets.forEach((ticket, index) => {
        const actualIndex = adminTickets.indexOf(ticket);
        const statusClass = ticket.status === 'resolved' ? 'status-resolved' : 'status-progress';
        const statusText = ticket.status === 'resolved' ? 'Resolved' : 'In Progress';

        const row = document.createElement('tr');
        row.innerHTML = `
            <td class="ticket-id">${ticket.id}</td>
            <td>${ticket.user}</td>
            <td>${ticket.type}</td>
            <td>${ticket.date}</td>
            <td class="priority-high">${ticket.priority}</td>
            <td>${ticket.event}</td>
            <td><span class="status-badge ${statusClass}">${statusText}</span></td>
            <td><a class="manage-link" onclick="openModal(${actualIndex})">Manage</a></td>
        `;
        tbody.appendChild(row);
    });

    updateStats();
}

function updateStats() {
    const total = adminTickets.length;
    const pending = adminTickets.filter(t => t.status === 'progress').length;
    const resolved = adminTickets.filter(t => t.status === 'resolved').length;

    document.getElementById('total-tickets').textContent = 160 + total;
    document.getElementById('pending-tickets').textContent = pending;
    document.getElementById('resolved-today').textContent = resolved;
}

function openModal(index) {
    currentTicketIndex = index;
    const ticket = adminTickets[index];
    const modal = document.getElementById('manage-modal');
    const modalBody = document.getElementById('modal-body');
    const resolveBtn = document.getElementById('resolve-btn');

    const isResolved = ticket.status === 'resolved';

    modalBody.innerHTML = `
        <div class="detail-row">
            <div class="detail-label">Ticket ID</div>
            <div class="detail-value">${ticket.id}</div>
        </div>
        <div class="detail-row">
            <div class="detail-label">User</div>
            <div class="detail-value">${ticket.user}</div>
        </div>
        <div class="detail-row">
            <div class="detail-label">Type</div>
            <div class="detail-value">${ticket.type}</div>
        </div>
        <div class="detail-row">
            <div class="detail-label">Event</div>
            <div class="detail-value">${ticket.event}</div>
        </div>
        <div class="detail-row">
            <div class="detail-label">Priority</div>
            <div class="detail-value">${ticket.priority}</div>
        </div>
        <div class="detail-row">
            <div class="detail-label">Date</div>
            <div class="detail-value">${ticket.date}</div>
        </div>
        <div class="detail-row">
            <div class="detail-label">Status</div>
            <div class="detail-value">
                <span class="status-badge ${ticket.status === 'resolved' ? 'status-resolved' : 'status-progress'}">
                    ${ticket.status === 'resolved' ? 'Resolved' : 'In Progress'}
                </span>
            </div>
        </div>
        <div class="detail-row">
            <div class="detail-label">Description</div>
            <div class="detail-value">${ticket.description}</div>
        </div>
        ${isResolved ? `
            <div class="detail-row">
                <div class="detail-label">Admin Reply</div>
                <div class="detail-value">${ticket.reply}</div>
            </div>
        ` : `
            <div class="detail-row" style="flex-direction: column;">
                <div class="detail-label">Admin Reply</div>
                <textarea class="reply-textarea" id="admin-reply" placeholder="Enter your response to the user..."></textarea>
            </div>
        `}
    `;

    resolveBtn.style.display = isResolved ? 'none' : 'block';
    modal.classList.add('active');
}

function closeModal() {
    document.getElementById('manage-modal').classList.remove('active');
    currentTicketIndex = null;
}

function resolveTicket() {
    if (currentTicketIndex === null) return;

    const replyTextarea = document.getElementById('admin-reply');
    const reply = replyTextarea?.value.trim();

    if (!reply) {
        alert('Please provide a reply before resolving the ticket.');
        return;
    }

    adminTickets[currentTicketIndex].status = 'resolved';
    adminTickets[currentTicketIndex].reply = reply;

    closeModal();
    renderTickets();
}

// Filter tabs
document.querySelectorAll('.filter-tab').forEach(tab => {
    tab.addEventListener('click', () => {
        document.querySelectorAll('.filter-tab').forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        currentFilter = tab.getAttribute('data-filter');
        renderTickets();
    });
});

// Refresh button
document.getElementById('refresh-btn').addEventListener('click', () => {
    renderTickets();
});

// Close modal on outside click
document.getElementById('manage-modal').addEventListener('click', (e) => {
    if (e.target.id === 'manage-modal') {
        closeModal();
    }
});

// Initialize
renderTickets();
function openTicketModal(descriptionText) {
    // 1. Put the text inside the modal
    document.getElementById('modalDescriptionContent').innerText = descriptionText;

    // 2. Show the modal (change display from none to flex)
    document.getElementById('ticketModal').style.display = 'flex';
}

function closeTicketModal() {
    document.getElementById('ticketModal').style.display = 'none';
}

// Close modal if user clicks outside the box
window.onclick = function (event) {
    const modal = document.getElementById('ticketModal');
    if (event.target == modal) {
        modal.style.display = "none";
    }
}
function openTicketModal(ticketId, description) {
    // 1. Set description
    document.getElementById('modalDescriptionContent').innerText = description;

    // 2. Set the form action dynamically to point to the correct ID
    document.getElementById('replyForm').action = `/admin/save-ticket-reply/${ticketId}`;

    // 3. Show Modal
    document.getElementById('ticketModal').style.display = 'flex';
}

function closeTicketModal() {
    document.getElementById('ticketModal').style.display = 'none';
}

// Toggle between Support Tickets and Live Chats
function toggleView() {
    const currentView = document.getElementById('current-view');
    const toggleHint = document.querySelector('.toggle-hint');
    const pageTitle = document.querySelector('.page-title');

    // The button shows what you can switch TO, not what you're currently on
    if (currentView.textContent === 'Live Chat') {
        // Currently on Tickets, switching to Live Chats
        currentView.textContent = 'Tickets';
        toggleHint.textContent = 'Click to switch view';
        pageTitle.textContent = 'Live Chats';

        // Show a message that Live Chats feature is coming soon
        alert('Live Chats feature is coming soon! This will allow you to manage real-time chat support with users.');
    } else {
        // Currently on Live Chats, switching back to Tickets
        currentView.textContent = 'Live Chat';
        toggleHint.textContent = 'Click to switch view';
        pageTitle.textContent = 'Support Ticket';
    }
}