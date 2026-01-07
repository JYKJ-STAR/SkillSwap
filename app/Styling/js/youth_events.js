// Youth Events Page JavaScript
// ========================================

document.addEventListener('DOMContentLoaded', function () {

    // Filter by Category
    window.filterByCategory = function (category) {
        // Remove active class from all buttons
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.classList.remove('active');
        });

        // Add active class to clicked button
        event.target.classList.add('active');

        console.log('Filtering by category:', category);

        // Reload page with filter parameter
        const url = new URL(window.location);
        if (category === 'all') {
            url.searchParams.delete('category');
        } else {
            url.searchParams.set('category', category);
        }
        window.location.href = url.toString();
    };

    // Filter by Location
    window.filterByLocation = function (location) {
        console.log('Filtering by location:', location);

        const url = new URL(window.location);
        if (location === 'all') {
            url.searchParams.delete('location');
        } else {
            url.searchParams.set('location', location);
        }
        window.location.href = url.toString();
    };

    // Reset Filters
    window.resetFilters = function () {
        window.location.href = window.location.pathname;
    };

    // Search functionality
    const searchBox = document.querySelector('.search-box');
    if (searchBox) {
        searchBox.addEventListener('keypress', function (e) {
            if (e.key === 'Enter') {
                const searchTerm = this.value;
                const url = new URL(window.location);
                if (searchTerm) {
                    url.searchParams.set('search', searchTerm);
                } else {
                    url.searchParams.delete('search');
                }
                window.location.href = url.toString();
            }
        });
    }

    // Set active filter from URL on page load
    const urlParams = new URLSearchParams(window.location.search);

    const categoryParam = urlParams.get('category');
    if (categoryParam) {
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.classList.remove('active');
            if (btn.dataset.category === categoryParam) {
                btn.classList.add('active');
            }
        });
    }

    const locationParam = urlParams.get('location');
    if (locationParam) {
        const locationDropdown = document.querySelector('.location-dropdown');
        if (locationDropdown) {
            locationDropdown.value = locationParam;
        }
    }

    // Language selector
    const languageSelector = document.querySelector('.language-selector');
    if (languageSelector) {
        languageSelector.addEventListener('change', function () {
            localStorage.setItem('preferredLanguage', this.value);
            console.log('Language changed to:', this.value);
        });

        const savedLanguage = localStorage.getItem('preferredLanguage');
        if (savedLanguage) {
            languageSelector.value = savedLanguage;
        }
    }
});
