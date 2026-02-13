document.addEventListener('DOMContentLoaded', () => {

    // --- 1. FAQ Accordion Functionality ---
    const faqButtons = document.querySelectorAll('.faq-question');
    faqButtons.forEach(button => {
        button.addEventListener('click', () => {
            const faqItem = button.parentElement;
            // This toggle works correctly now because it only exists once
            faqItem.classList.toggle('open');
        });
    });

    // --- 2. Page Navigation ---
    document.querySelectorAll('.sidebar-nav a').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const pageId = link.getAttribute('data-page');

            // Update active nav link
            document.querySelectorAll('.sidebar-nav a').forEach(navLink => {
                navLink.classList.remove('active');
            });
            link.classList.add('active');

            // Show selected page
            document.querySelectorAll('.page').forEach(page => {
                page.classList.remove('active');
            });
            const targetPage = document.getElementById(pageId);
            if (targetPage) {
                targetPage.classList.add('active');
            }
        });
    });

    // --- 3. Upload Area File Name Display ---
    // Commented out to keep label as "Upload Screenshot (Optional)" instead of showing filename
    /*
    const uploadInput = document.querySelector('.upload-input');
    if (uploadInput) {
        uploadInput.addEventListener('change', function () {
            const fileName = this.files[0]?.name;
            if (fileName) {
                const uploadText = this.parentElement.querySelector('.upload-text');
                if (uploadText) uploadText.textContent = fileName;
            }
        });
    }
    */

    // --- 4. Form Select Placeholder Styling ---
    document.querySelectorAll('.form-select').forEach(select => {
        select.addEventListener('change', function () {
            if (this.value) {
                this.classList.remove('placeholder');
            }
        });
    });

    // Note: Ticket rendering is now handled server-side via Jinja2 templates
    // The submitReport() function in the HTML handles form submission to the database

});

function showTicketDetails(ticketId, element) {
    // 1. Hide all detail cards
    document.querySelectorAll('.ticket-full-detail').forEach(card => {
        card.style.display = 'none';
    });

    // 2. Show the selected detail card
    document.getElementById('detail-' + ticketId).style.display = 'block';

    // 3. Update 'active' styling on list items
    document.querySelectorAll('.ticket-card').forEach(card => {
        card.classList.remove('active');
    });
    element.classList.add('active');
}

// =====================================================
// LIVE CHAT FUNCTIONALITY
// =====================================================

let currentChatSessionId = null;
let chatRefreshInterval = null;
let previousAdminConnected = false;

// Initialize live chat page when it becomes active
document.addEventListener('DOMContentLoaded', () => {
    const liveChatNav = document.querySelector('[data-page="live-chats-page"]');
    if (liveChatNav) {
        liveChatNav.addEventListener('click', () => {
            loadChatHistory();
            checkActiveChat();
        });
    }

    // Start New Chat button
    const startChatBtn = document.getElementById('start-new-chat');
    if (startChatBtn) {
        startChatBtn.addEventListener('click', startNewChat);
    }

    // Back to chat list button
    const backBtn = document.getElementById('back-to-chat-list');
    if (backBtn) {
        backBtn.addEventListener('click', (e) => {
            e.preventDefault();
            showChatList();
        });
    }

    // Send message button
    const sendBtn = document.querySelector('.send-btn');
    if (sendBtn) {
        sendBtn.addEventListener('click', sendUserMessage);
    }

    // Send message on Enter key
    const chatInput = document.querySelector('.chat-input');
    if (chatInput) {
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendUserMessage();
            }
        });
    }
});

async function startNewChat() {
    try {
        const response = await fetch('/start-chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        const data = await response.json();

        if (data.session_id) {
            currentChatSessionId = data.session_id;
            await loadChatSession(data.session_id);
            showChatConversation();

            if (data.status === 'created') {

            } else {

            }
        }
    } catch (error) {

        alert('Failed to start chat. Please try again.');
    }
}

async function sendUserMessage() {
    const input = document.querySelector('.chat-input');
    const message = input.value.trim();

    if (!message || !currentChatSessionId) return;

    try {
        const response = await fetch('/send-message', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: currentChatSessionId,
                message: message
            })
        });

        if (response.ok) {
            input.value = '';
            await loadMessages(currentChatSessionId);
        }
    } catch (error) {

        alert('Failed to send message. Please try again.');
    }
}

async function loadMessages(sessionId) {
    try {
        const response = await fetch(`/get-messages/${sessionId}`);
        const data = await response.json();

        const container = document.querySelector('.chat-messages');
        container.innerHTML = '';

        // Check if admin is connected
        const adminConnected = data.admin_connected;
        const chatStatus = data.status;

        // Show notification if admin just connected (status changed from false to true)
        if (adminConnected && !previousAdminConnected) {
            showAdminConnectedNotification();
        }
        previousAdminConnected = adminConnected;

        // Check if chat is closed
        if (chatStatus === 'closed') {
            const closedMessage = document.createElement('div');
            closedMessage.className = 'system-message closed-message';
            closedMessage.innerHTML = `
                <div style="text-align: center; padding: 20px; color: #dc2626;">
                    <div style="font-size: 16px; margin-bottom: 8px; font-weight: 600;">🔒 This chat has been closed</div>
                    <div style="font-size: 14px; opacity: 0.8;">You can no longer send messages in this conversation.</div>
                </div>
            `;
            container.appendChild(closedMessage);
            disableChatInput();
        } else if (!adminConnected) {
            // Show waiting message if admin not connected
            const waitingMessage = document.createElement('div');
            waitingMessage.className = 'system-message waiting-message';
            waitingMessage.innerHTML = `
                <div style="text-align: center; padding: 20px; color: #64748b;">
                    <div style="font-size: 16px; margin-bottom: 8px;">⏳ Please hold while we connect you to one of our admins...</div>
                    <div style="font-size: 14px; opacity: 0.8;">You'll be able to chat once an admin joins the conversation.</div>
                </div>
            `;
            container.appendChild(waitingMessage);
            disableChatInput();
        } else {
            enableChatInput();
        }

        // Display messages
        data.messages.forEach(msg => {
            const bubble = document.createElement('div');
            bubble.className = `message-bubble message-${msg.sender_type}`;

            let senderName = 'System';
            if (msg.sender_type === 'user') {
                senderName = 'You';
            } else if (msg.sender_type === 'admin') {
                senderName = 'Support Agent';
            }

            bubble.innerHTML = `
                <div class="message-sender">${senderName}</div>
                <div class="message-text">${escapeHtml(msg.message_text)}</div>
                <div class="message-time">${formatChatTime(msg.created_at)}</div>
            `;
            container.appendChild(bubble);
        });

        container.scrollTop = container.scrollHeight;
    } catch (error) {

    }
}

async function loadChatSession(sessionId) {
    currentChatSessionId = sessionId;
    await loadMessages(sessionId);

    // Start auto-refresh for messages
    if (chatRefreshInterval) {
        clearInterval(chatRefreshInterval);
    }
    chatRefreshInterval = setInterval(() => {
        if (currentChatSessionId) {
            loadMessages(currentChatSessionId);
        }
    }, 3000); // Refresh every 3 seconds
}

async function checkActiveChat() {
    try {
        const response = await fetch('/get-active-chat');
        const data = await response.json();

        if (data.has_active) {
            // User has an active chat
            currentChatSessionId = data.session_id;
        }
    } catch (error) {

    }
}

async function loadChatHistory() {
    try {
        const response = await fetch('/get-chat-history');
        const data = await response.json();

        const chatList = document.querySelector('.chat-list');
        if (!chatList) return;

        if (data.chats.length === 0) {
            chatList.innerHTML = '<div class="empty-state"><p>No chat history yet. Start a new chat to get help!</p></div>';
            return;
        }

        chatList.innerHTML = '';

        data.chats.forEach(chat => {
            const chatItem = document.createElement('div');
            chatItem.className = 'chat-list-item';
            chatItem.setAttribute('data-chat', chat.session_id);
            chatItem.onclick = () => {
                loadChatSession(chat.session_id);
                showChatConversation();
            };

            const statusClass = chat.status === 'active' ? 'status-ongoing' : 'status-resolved';
            const statusText = chat.status === 'active' ? 'Ongoing' : 'Resolved';

            chatItem.innerHTML = `
                <div class="chat-list-avatar">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
                        stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                        <circle cx="12" cy="7" r="4" />
                    </svg>
                </div>
                <div class="chat-list-info">
                    <div class="chat-list-top">
                        <h4 class="chat-list-name">Support Agent</h4>
                        <span class="chat-list-time">${formatChatTime(chat.last_message_at)}</span>
                    </div>
                    <p class="chat-list-preview">${escapeHtml(chat.last_message || 'No messages yet')}</p>
                    <div class="chat-list-meta">
                        <span class="chat-status ${statusClass}">${statusText}</span>
                        <span class="chat-duration">${chat.message_count} messages</span>
                    </div>
                </div>
            `;

            chatList.appendChild(chatItem);
        });
    } catch (error) {

    }
}

function showChatList() {
    document.getElementById('chat-list-view').classList.add('active');
    document.getElementById('chat-conversation-view').classList.remove('active');

    // Stop auto-refresh
    if (chatRefreshInterval) {
        clearInterval(chatRefreshInterval);
        chatRefreshInterval = null;
    }

    loadChatHistory();
}

function showChatConversation() {
    document.getElementById('chat-list-view').classList.remove('active');
    document.getElementById('chat-conversation-view').classList.add('active');
}

function disableChatInput() {
    const input = document.querySelector('.chat-input');
    const sendBtn = document.querySelector('.send-btn');
    if (input) {
        input.disabled = true;
        input.placeholder = 'Waiting for admin to connect...';
        input.style.opacity = '0.6';
    }
    if (sendBtn) {
        sendBtn.disabled = true;
        sendBtn.style.opacity = '0.6';
        sendBtn.style.cursor = 'not-allowed';
    }
}

function enableChatInput() {
    const input = document.querySelector('.chat-input');
    const sendBtn = document.querySelector('.send-btn');
    if (input) {
        input.disabled = false;
        input.placeholder = 'Type your message...';
        input.style.opacity = '1';
    }
    if (sendBtn) {
        sendBtn.disabled = false;
        sendBtn.style.opacity = '1';
        sendBtn.style.cursor = 'pointer';
    }
}

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

    return utcPlus8.toLocaleDateString();
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showAdminConnectedNotification() {
    // Create notification container
    const notification = document.createElement('div');
    notification.className = 'admin-connected-notification';
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #fff;
        color: #1a1a1a;
        padding: 20px 24px;
        border-radius: 12px;
        border: 1.5px solid #1a1a1a;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        z-index: 10000;
        min-width: 300px;
        animation: slideIn 0.3s ease-out;
        font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    `;

    notification.innerHTML = `
        <div style="display: flex; align-items: center; gap: 12px;">
            <div style="font-size: 24px;">✅</div>
            <div>
                <div style="font-weight: 600; font-size: 16px; margin-bottom: 4px; color: #1a1a1a;">Admin Connected!</div>
                <div style="font-size: 14px; color: #666;">A support agent has joined the chat</div>
            </div>
        </div>
    `;

    // Add animation keyframes
    if (!document.getElementById('notification-styles')) {
        const style = document.createElement('style');
        style.id = 'notification-styles';
        style.textContent = `
            @keyframes slideIn {
                from {
                    transform: translateX(400px);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
            @keyframes slideOut {
                from {
                    transform: translateX(0);
                    opacity: 1;
                }
                to {
                    transform: translateX(400px);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(style);
    }

    document.body.appendChild(notification);

    // Auto-remove after 4 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 4000);
}