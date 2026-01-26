document.addEventListener('DOMContentLoaded', function () {
    console.log('Senior Schedule JS loaded');

    // Handle "Remove Event" buttons
    const removeButtons = document.querySelectorAll('.btn-remove');
    removeButtons.forEach(button => {
        button.addEventListener('click', function (e) {
            e.preventDefault();
            const card = this.closest('.event-card');
            const title = card.querySelector('.event-title').textContent;

            if (confirm(`Are you sure you want to remove "${title}"?`)) {
                // In a real app, this would make an API call
                console.log(`Removing event: ${title}`);
                card.remove();
                // Optionally show a toast message here
            }
        });
    });

    // Handle "Complete Event" buttons
    const completeButtons = document.querySelectorAll('.btn-complete');
    completeButtons.forEach(button => {
        button.addEventListener('click', function (e) {
            e.preventDefault();
            const card = this.closest('.event-card');
            const title = card.querySelector('.event-title').textContent;

            // In a real app, this would make an API call and move the card to the 'Completed' column
            console.log(`Completing event: ${title}`);
            alert(`Marked "${title}" as complete! Points added.`);

            // For now, just remove it to simulate action
            card.remove();
        });
    });
});
