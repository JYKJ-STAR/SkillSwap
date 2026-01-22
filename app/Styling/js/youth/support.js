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

    // --- 4. Form Select Placeholder Styling ---
    document.querySelectorAll('.form-select').forEach(select => {
        select.addEventListener('change', function () {
            if (this.value) {
                this.classList.remove('placeholder');
            }
        });
    });

    // Ticket Management System
    let ticketIdCounter = 4;
    const ticketsData = [
        {
            id: 'T-001',
            title: 'Inappropriate Behavior',
            description: 'During the Web Development Workshop, a participant was making inappropriate comments to other attendees. This made several people uncomfortable and disrupted the learning environment.',
            involvedPerson: 'John Smith',
            eventName: 'Workshop: Web Development',
            date: '10 - 8 - 2025',
            status: 'progress',
            agentReply: null
        },
        {
            id: 'T-002',
            title: 'Harassment',
            description: 'I received multiple unwanted messages from another user after the Networking Meetup. They kept asking for my personal contact details even after I declined.',
            involvedPerson: 'Unknown User',
            eventName: 'Meetup: Networking',
            date: '8 - 8 - 2025',
            status: 'progress',
            agentReply: null
        },
        {
            id: 'T-003',
            title: 'Spam',
            description: 'Someone was promoting their personal business during the AI Basics Seminar, sending promotional materials to all attendees without permission.',
            involvedPerson: 'Marketing Account',
            eventName: 'Seminar: AI Basics',
            date: '5 - 8 - 2025',
            status: 'resolved',
            agentReply: 'Thank you for bringing this to our attention. We have identified the user and taken appropriate action. Their account has been warned and the promotional content has been removed. We apologize for any inconvenience caused.'
        },
        {
            id: 'T-004',
            title: 'Safety Concern',
            description: 'The emergency exit at the venue was blocked by equipment during the Python Workshop. This could be a safety hazard in case of emergency.',
            involvedPerson: 'N/A',
            eventName: 'Workshop: Python Programming',
            date: '1 - 8 - 2025',
            status: 'resolved',
            agentReply: 'Thank you for reporting this safety concern. We have contacted the venue management and they have cleared the emergency exit. We have also added this to our venue checklist to prevent future occurrences. Your vigilance helps keep our community safe!'
        }
    ];

    function renderTickets() {
        const ticketsList = document.getElementById('tickets-list');
        const emptyTickets = document.getElementById('empty-tickets');

        if (ticketsData.length === 0) {
            ticketsList.style.display = 'none';
            emptyTickets.style.display = 'block';
            return;
        }

        ticketsList.style.display = 'flex';
        emptyTickets.style.display = 'none';
        ticketsList.innerHTML = '';

        ticketsData.forEach((ticket, index) => {
            const ticketCard = document.createElement('div');
            ticketCard.className = 'ticket-card';
            ticketCard.setAttribute('data-ticket-index', index);

            const statusClass = ticket.status === 'resolved' ? 'status-resolved' : 'status-progress';
            const statusText = ticket.status === 'resolved' ? 'Resolved' : 'In Progress';

            ticketCard.innerHTML = `
                    <h4 class="ticket-title">${ticket.title}</h4>
                    <p class="ticket-description">${ticket.description}</p>
                    <div class="ticket-meta">
                        <span class="ticket-id">ID: ${ticket.id}</span>
                        <span class="ticket-date">Submitted: ${ticket.date}</span>
                        <span class="ticket-status ${statusClass}">${statusText}</span>
                    </div>
                `;

            ticketCard.addEventListener('click', () => showTicketDetail(index));
            ticketsList.appendChild(ticketCard);
        });
    }

    function showTicketDetail(index) {
        const ticket = ticketsData[index];
        const detailContent = document.getElementById('ticket-detail-content');

        // Update active state
        document.querySelectorAll('.ticket-card').forEach(card => card.classList.remove('active'));
        document.querySelector(`[data-ticket-index="${index}"]`)?.classList.add('active');

        let detailHTML = `
                <h3 class="detail-id">ID: ${ticket.id}</h3>
                <div class="detail-section">
                    <p class="detail-label">Issue Type</p>
                    <p class="detail-value">${ticket.title}</p>
                </div>
                <div class="detail-section">
                    <p class="detail-label">Person Involved</p>
                    <p class="detail-value">${ticket.involvedPerson || 'Not specified'}</p>
                </div>
                <div class="detail-section">
                    <p class="detail-label">Event</p>
                    <p class="detail-value">${ticket.eventName || 'Not specified'}</p>
                </div>
                <div class="detail-section">
                    <p class="detail-label">Description</p>
                    <div class="detail-box">
                        <p>${ticket.description}</p>
                    </div>
                </div>
            `;

        if (ticket.status === 'resolved' && ticket.agentReply) {
            detailHTML += `
                    <h4 class="agent-reply-title">Agent Reply</h4>
                    <div class="detail-box">
                        <p>${ticket.agentReply}</p>
                    </div>
                `;
        } else {
            detailHTML += `
                    <div class="pending-notice">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <circle cx="12" cy="12" r="10"/>
                            <polyline points="12 6 12 12 16 14"/>
                        </svg>
                        <p>Your report is being reviewed. An agent will respond shortly.</p>
                    </div>
                `;
        }

        detailContent.innerHTML = detailHTML;
    }

    // Initialize tickets on page load
    renderTickets();

    // Safety Report Form Submission
    const submitReportBtn = document.getElementById('submit-report-btn');
    const formSuccess = document.getElementById('form-success');

    submitReportBtn?.addEventListener('click', (e) => {
        e.preventDefault();

        const issueType = document.getElementById('issue-type').value;
        const involvedPerson = document.getElementById('involved-person').value;
        const eventName = document.getElementById('event-name').value;
        const description = document.getElementById('incident-description').value;

        // Validation
        if (!description.trim()) {
            alert('Please provide a description of the incident.');
            return;
        }

        if (!eventName) {
            alert('Please select an event.');
            return;
        }

        // Generate new ticket ID
        ticketIdCounter++;
        const newTicketId = `T-${String(ticketIdCounter).padStart(3, '0')}`;

        // Get current date
        const now = new Date();
        const dateStr = `${now.getDate()} - ${now.getMonth() + 1} - ${now.getFullYear()}`;

        // Create new ticket
        const newTicket = {
            id: newTicketId,
            title: issueType,
            description: description,
            involvedPerson: involvedPerson || 'Not specified',
            eventName: eventName,
            date: dateStr,
            status: 'progress',
            agentReply: null
        };

        // Add to beginning of tickets array
        ticketsData.unshift(newTicket);

        // Re-render tickets
        renderTickets();

        // Show success message
        formSuccess.style.display = 'flex';
        submitReportBtn.style.display = 'none';

        // Reset form after 3 seconds
        setTimeout(() => {
            document.getElementById('involved-person').value = '';
            document.getElementById('issue-type').value = 'Inappropriate Behavior';
            document.getElementById('event-name').value = '';
            document.getElementById('incident-description').value = '';
            document.getElementById('upload-area').querySelector('.upload-text').textContent = 'Upload Screenshot (Optional)';
            formSuccess.style.display = 'none';
            submitReportBtn.style.display = 'block';
        }, 3000);
    });

    // Live Chat Functionality
    const chatInput = document.querySelector('.chat-input');
    const sendBtn = document.querySelector('.send-btn');
    const chatMessages = document.querySelector('.chat-messages');
    const chatListView = document.getElementById('chat-list-view');
    const chatConversationView = document.getElementById('chat-conversation-view');
    const backToChatList = document.getElementById('back-to-chat-list');
    const startNewChatBtn = document.getElementById('start-new-chat');

    // Support admin names
    const supportAdmins = ['Chan Yi Liang', 'Jayden Yip', 'Caius Chan', 'Dickson Lim'];

    // Store conversation data for each chat
    const chatConversations = {
        1: {
            agentName: 'Chan Yi Liang',
            duration: 'Started today at 2:15 PM',
            messages: [
                { type: 'right', text: 'Hello, I require assistance with my account.' },
                { type: 'left', text: 'Hi there! Welcome to SkillSwap Support. I\'m Chan Yi Liang. How can I help you today?' },
                { type: 'right', text: 'I have a question about my reward points. They don\'t seem to be updating.' },
                { type: 'left', text: 'I\'d be happy to help you with that. Can you tell me when you last earned points?' },
                { type: 'right', text: 'I attended an event yesterday but my points are still showing the same.' },
                { type: 'left', text: 'I\'ll look into the points issue for you right away.' }
            ]
        },
        2: {
            agentName: 'Jayden Yip',
            duration: 'Conversation from yesterday',
            messages: [
                { type: 'right', text: 'Hi, I need help with event registration.' },
                { type: 'left', text: 'Hello! I\'m Jayden Yip from SkillSwap Support. What seems to be the issue?' },
                { type: 'right', text: 'I\'m trying to register for the Web Development Workshop but getting an error.' },
                { type: 'left', text: 'I\'m sorry to hear that. What error message are you seeing?' },
                { type: 'right', text: 'It says "Registration failed. Please try again later."' },
                { type: 'left', text: 'Let me check the system for you. One moment please.' },
                { type: 'left', text: 'I found the issue - there was a temporary glitch. I\'ve manually registered you for the event.' },
                { type: 'right', text: 'Thank you so much! That was quick.' },
                { type: 'left', text: 'Your event registration has been confirmed. See you there!' }
            ]
        },
        3: {
            agentName: 'Caius Chan',
            duration: 'Conversation from Jan 15, 2025',
            messages: [
                { type: 'right', text: 'Hello, I need some help please.' },
                { type: 'left', text: 'Hi! I\'m Caius Chan. Welcome to SkillSwap Support! How may I help you?' },
                { type: 'right', text: 'I need to verify my account to access premium events.' },
                { type: 'left', text: 'Sure, I can help with that. Could you please provide your student ID?' },
                { type: 'right', text: 'My student ID is STU-2024-7823.' },
                { type: 'left', text: 'Thank you. Let me verify that in our system.' },
                { type: 'left', text: 'Your account has been verified successfully. You\'re all set!' }
            ]
        },
        4: {
            agentName: 'Dickson Lim',
            duration: 'Started Jan 10, 2025',
            messages: [
                { type: 'right', text: 'Hi, I require assistance with a refund.' },
                { type: 'left', text: 'Hello! I\'m Dickson Lim from SkillSwap Support. What can I do for you today?' },
                { type: 'right', text: 'I accidentally registered for the wrong event and need a refund for my points.' },
                { type: 'left', text: 'I understand. Which event did you register for by mistake?' },
                { type: 'right', text: 'The Advanced Python Workshop. I meant to register for the Beginner one.' },
                { type: 'left', text: 'We\'re still looking into your refund request. I\'ll update you shortly.' }
            ]
        }
    };

    let currentChatId = null;
    let currentAgent = null;

    // Chat List Item Click - Open Conversation
    document.querySelectorAll('.chat-list-item').forEach(item => {
        item.addEventListener('click', () => {
            const chatId = item.getAttribute('data-chat');
            currentChatId = chatId;
            const chatData = chatConversations[chatId];

            if (chatData) {
                currentAgent = chatData.agentName;

                // Update conversation header with agent name
                document.querySelector('.chat-user-name').textContent = chatData.agentName;
                document.querySelector('.chat-user-details .chat-duration').textContent = chatData.duration;

                // Clear and load messages
                chatMessages.innerHTML = '';
                chatData.messages.forEach(msg => {
                    const messageDiv = document.createElement('div');
                    messageDiv.className = `message message-${msg.type}`;
                    messageDiv.innerHTML = `<p>${msg.text}</p>`;
                    chatMessages.appendChild(messageDiv);
                });

                // Scroll to bottom
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }

            // Switch to conversation view
            chatListView.classList.remove('active');
            chatConversationView.classList.add('active');
        });
    });

    // Back to Chat List
    backToChatList?.addEventListener('click', (e) => {
        e.preventDefault();
        chatConversationView.classList.remove('active');
        chatListView.classList.add('active');
        currentChatId = null;
        currentAgent = null;
    });

    // Start New Chat
    startNewChatBtn?.addEventListener('click', () => {
        currentChatId = 'new';

        // Randomly select an admin
        currentAgent = supportAdmins[Math.floor(Math.random() * supportAdmins.length)];

        // Clear previous messages
        chatMessages.innerHTML = '';

        // Update header for new chat with random admin
        document.querySelector('.chat-user-name').textContent = currentAgent;
        document.querySelector('.chat-user-details .chat-duration').textContent = 'New conversation';

        // Add system message
        const systemMessage = document.createElement('div');
        systemMessage.className = 'system-message';
        systemMessage.innerHTML = `<p>You are now connected with <strong>${currentAgent}</strong>. Type your message below to start the conversation.</p>`;
        chatMessages.appendChild(systemMessage);

        // Switch to conversation view
        chatListView.classList.remove('active');
        chatConversationView.classList.add('active');
    });

    function sendMessage() {
        const messageText = chatInput.value.trim();
        if (!messageText) return;

        // Add user message
        const userMessage = document.createElement('div');
        userMessage.className = 'message message-right';
        userMessage.innerHTML = `<p>${messageText}</p>`;
        chatMessages.appendChild(userMessage);

        // Clear input
        chatInput.value = '';

        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;

        // Check for greeting/help messages and respond
        const lowerMessage = messageText.toLowerCase();
        if (lowerMessage.includes('hello') || lowerMessage.includes('help') || lowerMessage.includes('hi') || lowerMessage.includes('assistance')) {
            // Show typing indicator
            const typingIndicator = document.createElement('div');
            typingIndicator.className = 'message message-left typing-indicator';
            typingIndicator.innerHTML = `<p><span class="dot"></span><span class="dot"></span><span class="dot"></span></p>`;
            chatMessages.appendChild(typingIndicator);
            chatMessages.scrollTop = chatMessages.scrollHeight;

            // Delay before bot response
            setTimeout(() => {
                // Remove typing indicator
                typingIndicator.remove();

                // Add bot response with agent name
                const botMessage = document.createElement('div');
                botMessage.className = 'message message-left';
                botMessage.innerHTML = `<p>Hello! I'm ${currentAgent} from SkillSwap Support. How may I assist you today?</p>`;
                chatMessages.appendChild(botMessage);

                // Scroll to bottom
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }, 1500); // 1.5 second delay
        }
    }

    // Send on button click
    sendBtn?.addEventListener('click', sendMessage);

    // Send on Enter key
    chatInput?.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            sendMessage();
        }
    });
});