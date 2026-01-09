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
