// Senior Events Page JavaScript
// ========================================
// Filtering logic synced with Youth version
// Search bar kept unchanged (simple input filtering)

document.addEventListener('DOMContentLoaded', function () {

    // =========================================================
    // Helper: Get URL Params
    // =========================================================
    function getUrlParams() {
        const params = new URLSearchParams(window.location.search);
        return {
            categories: params.get('category') ? params.get('category').split(',') : [],
            location: params.get('location') || 'all'
        };
    }

    // =========================================================
    // Helper: Update URL (with page reload for simplicity)
    // =========================================================
    function updateUrl(params) {
        const url = new URL(window.location);

        // Category
        if (params.categories.length > 0) {
            url.searchParams.set('category', params.categories.join(','));
        } else {
            url.searchParams.delete('category');
        }

        // Location
        if (params.location && params.location !== 'all') {
            url.searchParams.set('location', params.location);
        } else {
            url.searchParams.delete('location');
        }

        // Reload page with new params
        window.location.href = url.toString();
    }

    // =========================================================
    // Core Filtering Logic
    // =========================================================
    function applyFilters(params) {
        const { categories, location } = params;

        // Sections
        const newSection = document.querySelector('[data-section="new"]');
        const recSection = document.querySelector('[data-section="recommended"]');
        const bondSection = document.querySelector('[data-section="bond"]');
        const categorySections = document.querySelectorAll('.category-section-senior');

        // Check if "All Activities" is selected
        const isAllActivities = categories.includes('all_activities');

        // Determine if we are in "Filtering Mode"
        const isFiltering = (location !== 'all') || (categories.length > 0);

        if (!isFiltering) {
            // DEFAULT VIEW: Show New + Recs + Bond, Hide Category Sections
            if (newSection) newSection.style.display = 'block';
            if (recSection) recSection.style.display = 'block';
            if (bondSection) bondSection.style.display = 'block';
            categorySections.forEach(sec => sec.style.display = 'none');
        } else {
            // FILTERED VIEW: Apply filters to New Events section
            if (newSection) {
                let visibleNewCount = 0;
                const newCards = newSection.querySelectorAll('.senior-event-card, .senior-event-card-new');

                newCards.forEach(card => {
                    const cardCat = card.dataset.category;
                    const cardLoc = card.dataset.location ? card.dataset.location.toLowerCase() : '';

                    // Category Match
                    const catMatch = isAllActivities || (categories.length === 0) || categories.includes(cardCat);

                    // Location Match
                    const locMatch = (location === 'all') || cardLoc.includes(location.toLowerCase());

                    if (catMatch && locMatch) {
                        card.style.display = 'block';
                        visibleNewCount++;
                    } else {
                        card.style.display = 'none';
                    }
                });

                // Show new section only if it has visible cards
                newSection.style.display = visibleNewCount > 0 ? 'block' : 'none';
            }

            // Hide Recs + Bond, Show Matching Categories
            if (recSection) recSection.style.display = 'none';
            if (bondSection) bondSection.style.display = 'none';

            categorySections.forEach(sec => {
                const secCat = sec.dataset.section;

                // Category Match
                const categoryMatch = isAllActivities || (categories.length === 0) || categories.includes(secCat);

                if (!categoryMatch) {
                    sec.style.display = 'none';
                    return;
                }

                // Check Cards inside this section for location match
                let visibleCardsCount = 0;
                const cards = sec.querySelectorAll('.senior-event-card');

                cards.forEach(card => {
                    const cardLoc = card.dataset.location ? card.dataset.location.toLowerCase() : '';

                    // Location Match
                    const locMatch = (location === 'all') || cardLoc.includes(location.toLowerCase());

                    if (locMatch) {
                        card.style.display = 'block';
                        visibleCardsCount++;
                    } else {
                        card.style.display = 'none';
                    }
                });

                // Show section only if it has visible cards
                if (visibleCardsCount > 0) {
                    sec.style.display = 'block';
                } else {
                    sec.style.display = 'none';
                }
            });
        }
    }

    // =========================================================
    // Event Handlers (Global Functions)
    // =========================================================

    // 1. Filter by Category
    window.filterByCategory = function (category) {
        let params = getUrlParams();

        if (params.categories.includes(category)) {
            params.categories = params.categories.filter(c => c !== category);
        } else {
            params.categories.push(category);
        }
        updateUrl(params);
    };

    // 2. Filter by Location
    window.filterByLocation = function (locValue) {
        let params = getUrlParams();
        params.location = locValue;
        updateUrl(params);
    };

    // 3. Reset Filters
    window.resetFilters = function () {
        window.location.href = window.location.pathname;
    };

    // =========================================================
    // Initialise UI
    // =========================================================
    const currentParams = getUrlParams();

    // 1. Set Checkboxes
    document.querySelectorAll('.category-filters-senior input[type="checkbox"]').forEach(box => {
        box.checked = currentParams.categories.includes(box.value);
    });

    // 2. Set Dropdown
    const locationDropdown = document.querySelector('.location-dropdown-senior');
    if (locationDropdown) {
        locationDropdown.value = currentParams.location;
    }

    // 3. Apply Filters on Load
    applyFilters(currentParams);

    // =========================================================
    // Search Bar (Kept Unchanged - Simple Input Filtering)
    // =========================================================
    const searchBox = document.getElementById('seniorSearch');

    if (searchBox) {
        searchBox.addEventListener('input', function () {
            const searchTerm = this.value.toLowerCase();
            const allCards = document.querySelectorAll('.senior-event-card');

            allCards.forEach(card => {
                const title = card.querySelector('.senior-event-title').textContent.toLowerCase();
                const description = card.querySelector('.senior-event-description').textContent.toLowerCase();
                const categoryBadge = card.querySelector('.event-category-badge-senior');
                const category = categoryBadge ? categoryBadge.textContent.toLowerCase() : '';
                const meta = card.querySelector('.senior-event-meta').textContent.toLowerCase();

                // Search in Title, Description, Category, and Meta (Time/Location)
                if (title.includes(searchTerm) ||
                    description.includes(searchTerm) ||
                    category.includes(searchTerm) ||
                    meta.includes(searchTerm)) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });

            // Hide empty sections
            document.querySelectorAll('.events-section-senior').forEach(section => {
                const visibleCards = Array.from(section.querySelectorAll('.senior-event-card')).filter(c => c.style.display !== 'none');
                if (visibleCards.length === 0) {
                    section.style.display = 'none';
                } else {
                    section.style.display = 'block';
                }
            });
        });
    }

    // Make text larger for better readability
    document.body.style.fontSize = '18px';
});
