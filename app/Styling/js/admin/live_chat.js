// =====================================================
// ADMIN LIVE CHAT FUNCTIONALITY
// =====================================================

let currentChatSessionId = null;
let currentChatUserName = null;
let currentChatStatus = null;
let chatRefreshInterval = null;

// Close chat modal function
function closeChatModal() {
    const modal = document.getElementById('chatModal');
    modal.style.display = 'none';
    if (chatRefreshInterval) {
        clearInterval(chatRefreshInterval);
        chatRefreshInterval = null;
    }
    currentChatSessionId = null;
}

// Click outside modal to close
document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('chatModal');
    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeChatModal();
            }
        });
    }
});

// Toggle view between Support Tickets and Live Chats
function toggleView() {
    window.location.href = window.location.origin + '/admin/support-tickets';
}


// Filter chats by status
function filterChats(status) {
    const rows = document.querySelectorAll('.chat-row');
    const buttons = document.querySelectorAll('.custom-tab');

    // Update active button
    buttons.forEach(btn => btn.classList.remove('active'));

    // Find the button that was clicked and activate it
    const activeButton = document.querySelector(`.custom-tab[data-filter="${status}"]`);
    if (activeButton) {
        activeButton.classList.add('active');
    }

    // Filter rows
    rows.forEach(row => {
        const rowStatus = row.getAttribute('data-status');
        if (status === 'all' || rowStatus === status) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

// Open chat modal
async function openChatModal(sessionId) {
    currentChatSessionId = sessionId;

    // Fetch chat details
    try {
        const response = await fetch(`/admin/get-chat-details/${sessionId}`);
        const data = await response.json();

        if (data.error) {
            alert('Error loading chat: ' + data.error);
            return;
        }

        // Update modal header and store chat status
        document.getElementById('chatModalTitle').textContent = `Chat Session #${sessionId}`;
        document.getElementById('chatUserName').textContent = data.user_name;
        document.getElementById('chatSessionId').textContent = sessionId;
        currentChatUserName = data.user_name;
        currentChatStatus = data.status;

        // Check if chat is locked by another admin
        if (data.is_locked) {
            // Disable input and show locked message
            const input = document.getElementById('adminMessageInput');
            const sendBtn = document.querySelector('.chat-input-section button');
            const chatActions = document.getElementById('chatActions');

            if (input) {
                input.disabled = true;
                input.placeholder = `This chat is currently being handled by ${data.locked_by_admin}`;
                input.style.backgroundColor = '#2d3748';
                input.style.cursor = 'not-allowed';
            }
            if (sendBtn) {
                sendBtn.disabled = true;
                sendBtn.style.opacity = '0.5';
                sendBtn.style.cursor = 'not-allowed';
            }
            if (chatActions) {
                chatActions.innerHTML = `
                    <div style="padding: 10px; background: rgba(251, 191, 36, 0.1); border: 1px solid rgba(251, 191, 36, 0.3); border-radius: 8px; color: #fbbf24;">
                        <i class="bi bi-lock-fill"></i> This chat is currently being handled by ${data.locked_by_admin}
                    </div>
                `;
            }
        } else {
            // Update chat input state based on status
            updateChatInputState();
        }

        // Load messages
        await loadChatMessages(sessionId);

        // Show modal with flex display for centering
        document.getElementById('chatModal').style.display = 'flex';


        // Start auto-refresh
        if (chatRefreshInterval) {
            clearInterval(chatRefreshInterval);
        }
        chatRefreshInterval = setInterval(() => {
            if (currentChatSessionId) {
                loadChatMessages(currentChatSessionId);
            }
        }, 3000); // Refresh every 3 seconds

    } catch (error) {

        alert('Failed to load chat. Please try again.');
    }
}

// Load chat messages
async function loadChatMessages(sessionId) {
    try {
        const response = await fetch(`/admin/get-chat-messages/${sessionId}`);
        const data = await response.json();

        if (data.error) {

            return;
        }

        const container = document.getElementById('chatMessagesContent');
        container.innerHTML = '';

        if (data.messages.length === 0) {
            container.innerHTML = '<p style="text-align: center; color: #9ca3af;">No messages yet.</p>';
            return;
        }

        data.messages.forEach(msg => {
            const bubble = document.createElement('div');
            bubble.className = `message-bubble message-${msg.sender_type}`;

            let senderName = 'System';
            if (msg.sender_type === 'user') {
                senderName = currentChatUserName || 'User';
            } else if (msg.sender_type === 'admin') {
                senderName = 'You (Admin)';
            }

            bubble.innerHTML = `
                <div class="message-sender">${escapeHtml(senderName)}</div>
                <div class="message-text">${escapeHtml(msg.message_text)}</div>
                <div class="message-time">${formatChatTime(msg.created_at)}</div>
            `;
            container.appendChild(bubble);
        });

        // Scroll to bottom
        container.scrollTop = container.scrollHeight;
    } catch (error) {

    }
}

// Send admin message
async function sendAdminMessage() {
    const input = document.getElementById('adminMessageInput');
    const message = input.value.trim();

    if (!message || !currentChatSessionId) return;

    try {
        const response = await fetch('/admin/send-chat-message', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: currentChatSessionId,
                message: message
            })
        });

        const data = await response.json();

        if (data.status === 'sent') {
            input.value = '';
            await loadChatMessages(currentChatSessionId);
        } else {
            alert('Failed to send message: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {

        alert('Failed to send message. Please try again.');
    }
}

// Close chat session
async function closeChat(sessionId) {
    try {
        const response = await fetch(`/admin/close-chat/${sessionId}`, {
            method: 'POST'
        });

        const data = await response.json();

        if (data.status === 'closed') {
            currentChatStatus = 'closed';
            updateChatInputState();
            // Reload to update the table
            setTimeout(() => location.reload(), 500);
        } else {

        }
    } catch (error) {

    }
}

// Reopen chat session
async function reopenChat(sessionId) {
    try {
        const response = await fetch(`/admin/reopen-chat/${sessionId}`, {
            method: 'POST'
        });

        const data = await response.json();

        if (data.status === 'reopened') {
            currentChatStatus = 'active';
            updateChatInputState();
            // Reload to update the table
            setTimeout(() => location.reload(), 500);
        } else {

        }
    } catch (error) {

    }
}

// Update chat input state based on chat status
function updateChatInputState() {
    const input = document.getElementById('adminMessageInput');
    const sendBtn = document.querySelector('.chat-input-section button');
    const chatActions = document.getElementById('chatActions');

    if (currentChatStatus === 'closed') {
        // Disable input for closed chats
        if (input) {
            input.disabled = true;
            input.placeholder = 'This chat is closed. Reopen to send messages.';
            input.style.backgroundColor = '#2d3748';
            input.style.cursor = 'not-allowed';
        }
        if (sendBtn) {
            sendBtn.disabled = true;
            sendBtn.style.opacity = '0.5';
            sendBtn.style.cursor = 'not-allowed';
        }
        // Update action buttons
        if (chatActions) {
            chatActions.innerHTML = `
                <button onclick="reopenChat(${currentChatSessionId})" class="btn btn-sm btn-outline-success">
                    Reopen Chat
                </button>
            `;
        }
    } else {
        // Enable input for active chats
        if (input) {
            input.disabled = false;
            input.placeholder = 'Type your message...';
            input.style.backgroundColor = '#374151';
            input.style.cursor = 'text';
        }
        if (sendBtn) {
            sendBtn.disabled = false;
            sendBtn.style.opacity = '1';
            sendBtn.style.cursor = 'pointer';
        }
        // Update action buttons
        if (chatActions) {
            chatActions.innerHTML = `
                <button onclick="closeChat(${currentChatSessionId})" class="btn btn-sm btn-outline-danger">
                    Close Chat
                </button>
            `;
        }
    }
}

// Close chat modal
function closeChatModal() {
    document.getElementById('chatModal').style.display = 'none';
    currentChatSessionId = null;
    currentChatUserName = null;
    currentChatStatus = null;

    // Stop auto-refresh
    if (chatRefreshInterval) {
        clearInterval(chatRefreshInterval);
        chatRefreshInterval = null;
    }
}

// Close modal when clicking outside
window.onclick = function (event) {
    const modal = document.getElementById('chatModal');
    if (event.target === modal) {
        closeChatModal();
    }
}

// Format chat time
function formatChatTime(timestamp) {
    if (!timestamp) return '';

    // Parse the UTC timestamp and add 8 hours for UTC+8
    const date = new Date(timestamp);
    const utcPlus8 = new Date(date.getTime() + (8 * 60 * 60 * 1000));

    const now = new Date();
    const diffMs = now - utcPlus8;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} min ago`;
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;

    return utcPlus8.toLocaleDateString() + ' ' + utcPlus8.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Allow sending message with Enter key
document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('adminMessageInput');
    if (input) {
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendAdminMessage();
            }
        });
    }
});
