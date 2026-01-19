document.addEventListener('DOMContentLoaded', () => {
    // FAQ Accordion Functionality
    document.querySelectorAll('.faq-question').forEach(button => {
        button.addEventListener('click', () => {
            const faqItem = button.parentElement;
            faqItem.classList.toggle('open');
        });
    });

    // Page Navigation
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

    // Upload area file name display
    const uploadInput = document.querySelector('.upload-input');
    if (uploadInput) {
        uploadInput.addEventListener('change', function () {
            const fileName = this.files[0]?.name;
            if (fileName) {
                this.parentElement.querySelector('.upload-text').textContent = fileName;
            }
        });
    }

    // Form select placeholder styling
    document.querySelectorAll('.form-select').forEach(select => {
        select.addEventListener('change', function () {
            if (this.value) {
                this.classList.remove('placeholder');
            }
        });
    });

    // Ticket Selection
    document.querySelectorAll('.ticket-card').forEach(card => {
        card.addEventListener('click', () => {
            // Update active ticket
            document.querySelectorAll('.ticket-card').forEach(c => {
                c.classList.remove('active');
            });
            card.classList.add('active');

            // Update detail panel (in a real app, this would fetch ticket data)
            const ticketId = card.querySelector('.ticket-id').textContent;
            const ticketDesc = card.querySelector('.ticket-description').textContent;
            const detailPanel = document.querySelector('.ticket-detail-panel');

            if (detailPanel) {
                detailPanel.querySelector('.detail-id').textContent = ticketId.replace('ID: ', 'ID: ');
                const detailBoxes = detailPanel.querySelectorAll('.detail-box p');
                if (detailBoxes.length > 0) {
                    detailBoxes[0].textContent = ticketDesc;
                }
            }
        });
    });
});

// FAQ Accordion Functionality
document.querySelectorAll('.faq-question').forEach(button => {
    button.addEventListener('click', () => {
        const faqItem = button.parentElement;
        faqItem.classList.toggle('open');
    });
});

// Page Navigation
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
        document.getElementById(pageId).classList.add('active');
    });
});

// Upload area file name display
document.querySelector('.upload-input')?.addEventListener('change', function () {
    const fileName = this.files[0]?.name;
    if (fileName) {
        this.parentElement.querySelector('.upload-text').textContent = fileName;
    }
});

// Form select placeholder styling
document.querySelectorAll('.form-select').forEach(select => {
    select.addEventListener('change', function () {
        if (this.value) {
            this.classList.remove('placeholder');
        }
    });
});

// Ticket Selection
document.querySelectorAll('.ticket-card').forEach(card => {
    card.addEventListener('click', () => {
        // Update active ticket
        document.querySelectorAll('.ticket-card').forEach(c => {
            c.classList.remove('active');
        });
        card.classList.add('active');

        // Update detail panel (in a real app, this would fetch ticket data)
        const ticketId = card.querySelector('.ticket-id').textContent;
        const ticketDesc = card.querySelector('.ticket-description').textContent;
        const detailPanel = document.querySelector('.ticket-detail-panel');

        if (detailPanel) {
            detailPanel.querySelector('.detail-id').textContent = ticketId.replace('ID: ', 'ID: ');
            detailPanel.querySelectorAll('.detail-box p')[0].textContent = ticketDesc;
        }
    });
});

// Live Chat Functionality
const chatInput = document.querySelector('.chat-input');
const sendBtn = document.querySelector('.send-btn');
const chatMessages = document.querySelector('.chat-messages');

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
    if (lowerMessage.includes('hello') || lowerMessage.includes('help') || lowerMessage.includes('hi')) {
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

            // Add bot response
            const botMessage = document.createElement('div');
            botMessage.className = 'message message-left';
            botMessage.innerHTML = `<p>Hello! Thank you for reaching out to SkillSwap support. My name is John Doe, how can I
                                assist you today?</p>`;
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