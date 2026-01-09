// Senior Events Page JavaScript
// ========================================

document.addEventListener('DOMContentLoaded', function () {
    // Simple search functionality for each section
    function setupSearch(searchBoxId, sectionSelector) {
        const searchBox = document.getElementById(searchBoxId);
        if (searchBox) {
            searchBox.addEventListener('input', function () {
                const searchTerm = this.value.toLowerCase();
                const section = searchBox.closest('.events-section');
                const cards = section.querySelectorAll('.senior-event-card');

                cards.forEach(card => {
                    const title = card.querySelector('.senior-event-title').textContent.toLowerCase();
                    const description = card.querySelector('.senior-event-description').textContent.toLowerCase();

                    if (title.includes(searchTerm) || description.includes(searchTerm)) {
                        card.style.display = 'block';
                    } else {
                        card.style.display = 'none';
                    }
                });
            });
        }
    }

    // Setup search for both sections
    setupSearch('searchBox1', '.events-section:first-of-type');
    setupSearch('searchBox2', '.events-section:last-of-type');

    // Make text larger for better readability
    document.body.style.fontSize = '18px';
});
