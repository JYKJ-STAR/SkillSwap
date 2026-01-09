// Youth Events Page JavaScript
// ========================================

document.addEventListener('DOMContentLoaded', function () {

    // Helper: Get URL Params
    function getUrlParams() {
        const params = new URLSearchParams(window.location.search);
        return {
            categories: params.get('category') ? params.get('category').split(',') : [],
            location: params.get('location') || 'all',
            search: params.get('search') || ''
        };
    }

    // Helper: Update URL
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

        // Search
        if (params.search) {
            url.searchParams.set('search', params.search);
        } else {
            url.searchParams.delete('search');
        }

        window.location.href = url.toString();
    }

    // ---------------------------------------------------------
    // Event Handlers
    // ---------------------------------------------------------

    // 1. Filter by Category (Multi-select Checkboxes)
    window.filterByCategory = function (category) {
        let { categories, location, search } = getUrlParams();

        // Toggle selection
        if (categories.includes(category)) {
            categories = categories.filter(c => c !== category);
        } else {
            categories.push(category);
        }

        updateUrl({ categories, location, search });
    };

    // 2. Filter by Location (Dropdown)
    window.filterByLocation = function (locValue) {
        let { categories, location, search } = getUrlParams();
        location = locValue;
        updateUrl({ categories, location, search });
    };

    // 3. Search
    const searchBox = document.querySelector('.search-box');
    if (searchBox) {
        window.searchEvents = function (term) {
            // Placeholder
        };

        searchBox.addEventListener('keypress', function (e) {
            if (e.key === 'Enter') {
                let { categories, location } = getUrlParams();
                updateUrl({ categories, location, search: this.value });
            }
        });
    }

    // 4. Reset Filters
    window.resetFilters = function () {
        window.location.href = window.location.pathname; // Reloads page without params
    };

    // ---------------------------------------------------------
    // Initialise UI & Apply Filters
    // ---------------------------------------------------------

    const { categories, location, search } = getUrlParams();

    // 1. Set Active Category Checkboxes
    document.querySelectorAll('.category-filters input[type="checkbox"]').forEach(box => {
        if (categories.includes(box.value)) {
            box.checked = true;
        } else {
            box.checked = false;
        }
    });

    // 2. Set Active Location Dropdown
    const locationDropdown = document.querySelector('.location-dropdown');
    if (locationDropdown) {
        locationDropdown.value = location;
    }

    // 3. Set Search Box Value
    if (searchBox && search) {
        searchBox.value = search;
    }

    // 4. APPLY FILTERING LOGIC (Visibility)
    const recSection = document.querySelector('[data-section="recommended"]');
    const bondSection = document.querySelector('[data-section="bond"]');
    const categorySections = document.querySelectorAll('.category-section');

    // Logic as requested:
    // If Location = All & No Categories -> Show all activities (Assuming this means "Default View" or "All Category Sections").
    // User phrasing "show all activities" implies they want to see the main list.
    // However, usually "Default" implies showing Recommendations. 
    // If filters are completely empty, let's show Recommendations as the "landing experience".
    // If filters are explicitly set, hide recommendations.

    const isFiltering = (location !== 'all') || (categories.length > 0) || (search !== '');

    if (!isFiltering) {
        // DEFAULT VIEW: Show Recs + Bond, Hide Category Sections (OR Show all if user meant that?)
        // Let's stick to standard behavior: No filter = Dashboard view (Recs).
        if (recSection) recSection.style.display = 'block';
        if (bondSection) bondSection.style.display = 'block';
        categorySections.forEach(sec => sec.style.display = 'none');

    } else {
        // FILTERED VIEW: Hide Recs, Show Matching
        if (recSection) recSection.style.display = 'none';
        if (bondSection) bondSection.style.display = 'none';

        categorySections.forEach(sec => {
            // Check Category Match
            // "If one/more categories selected... show activities in those categories"
            // "If no categories selected... show all activities" (implies category match is TRUE for all)
            const secCat = sec.dataset.section;

            // If categories is empty [], we match ALL sections.
            // If categories has items, we only match sections in that list.
            const categoryMatch = (categories.length === 0) || categories.includes(secCat);

            if (!categoryMatch) {
                sec.style.display = 'none';
                return;
            }

            // Check Location Match (Card Level)
            let visibleCardsCount = 0;
            const cards = sec.querySelectorAll('.event-card-compact');

            cards.forEach(card => {
                const cardLoc = card.dataset.location.toLowerCase();
                const cardTitle = card.querySelector('.event-card-title').textContent.toLowerCase();

                // Location Match
                // "If Location = All ... show all activities" (Match True)
                // "If Location = Specific ... show activities that match Location"
                const locMatch = (location === 'all') || cardLoc.includes(location.toLowerCase());

                // Search Match
                const searchMatch = !search || cardTitle.includes(search.toLowerCase());

                if (locMatch && searchMatch) {
                    card.style.display = 'block';
                    visibleCardsCount++;
                } else {
                    card.style.display = 'none';
                }
            });

            // Hide section if empty
            if (visibleCardsCount > 0) {
                sec.style.display = 'block';
            } else {
                sec.style.display = 'none';
            }
        });
    }

    // Language Selector
    const languageSelector = document.querySelector('.language-selector');
    if (languageSelector) {
        languageSelector.addEventListener('change', function () {
            localStorage.setItem('preferredLanguage', this.value);
        });
        const savedLanguage = localStorage.getItem('preferredLanguage');
        if (savedLanguage) languageSelector.value = savedLanguage;
    }
});
