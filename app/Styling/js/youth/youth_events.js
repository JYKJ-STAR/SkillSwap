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

    // Helper: Update URL (without reload)
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

        // Update URL without reloading
        window.history.pushState({}, '', url);

        // Re-run filtering
        applyFilters(params);
    }

    // ---------------------------------------------------------
    // Core Filtering Logic
    // ---------------------------------------------------------
    function applyFilters(params) {
        const { categories, location, search } = params;
        const normalizedSearch = search.toLowerCase();

        // Sections
        const newSection = document.querySelector('[data-section="new"]');
        const recSection = document.querySelector('[data-section="recommended"]');
        const bondSection = document.querySelector('[data-section="bond"]');
        const categorySections = document.querySelectorAll('.category-section');

        // Check if "All Activities" is selected
        const isAllActivities = categories.includes('all_activities');

        // Determine if we are in "Filtering Mode"
        // If "All Activities" is checked, we ARE filtering (filtering for "Everything" view)
        const isFiltering = (location !== 'all') || (categories.length > 0) || (search !== '');

        if (!isFiltering) {
            // DEFAULT VIEW (No filters): Show New + Recs + Bond, Hide Category Sections
            if (newSection) newSection.style.display = 'block';
            if (recSection) recSection.style.display = 'block';
            if (bondSection) bondSection.style.display = 'block';
            categorySections.forEach(sec => sec.style.display = 'none');
        } else {
            // FILTERED VIEW:
            // Apply filters to New Events section
            if (newSection) {
                let visibleNewCount = 0;
                const newCards = newSection.querySelectorAll('.event-card-compact, .event-card-new');

                newCards.forEach(card => {
                    const cardCat = card.dataset.category;
                    const cardLoc = card.dataset.location ? card.dataset.location.toLowerCase() : '';
                    const cardTitle = card.querySelector('.event-card-title').textContent.toLowerCase();
                    const cardDesc = card.querySelector('.event-card-description').textContent.toLowerCase();

                    // Category Match
                    const catMatch = isAllActivities || (categories.length === 0) || categories.includes(cardCat);

                    // Location Match
                    const locMatch = (location === 'all') || cardLoc.includes(location.toLowerCase());

                    // Search Match
                    const searchMatch = !normalizedSearch ||
                        cardTitle.includes(normalizedSearch) ||
                        cardDesc.includes(normalizedSearch);

                    if (catMatch && locMatch && searchMatch) {
                        card.style.display = 'block';
                        visibleNewCount++;
                    } else {
                        card.style.display = 'none';
                    }
                });

                // Show new section only if it has visible cards
                newSection.style.display = visibleNewCount > 0 ? 'block' : 'none';
            }

            // Hide Recs and Bond in filtered view
            if (recSection) recSection.style.display = 'none';
            if (bondSection) bondSection.style.display = 'none';

            categorySections.forEach(sec => {
                const secCat = sec.dataset.section;

                // 1. Check Section Category Match
                // If "All Activities" is selected, we match ALL sections.
                // If specific categories selected, only show those sections.
                // If no categories selected (but other filters exist like search/loc), show ALL sections.
                const categoryMatch = isAllActivities || (categories.length === 0) || categories.includes(secCat);

                if (!categoryMatch) {
                    sec.style.display = 'none';
                    return;
                }

                // 2. Check Cards inside this section
                let visibleCardsCount = 0;
                const cards = sec.querySelectorAll('.event-card-compact');

                cards.forEach(card => {
                    const cardLoc = card.dataset.location ? card.dataset.location.toLowerCase() : '';
                    const cardTitle = card.querySelector('.event-card-title').textContent.toLowerCase();
                    const cardDesc = card.querySelector('.event-card-description').textContent.toLowerCase();
                    // Get category from dataset or badge text
                    const cardCatBadge = card.querySelector('.event-category-badge');
                    const cardCatText = cardCatBadge ? cardCatBadge.textContent.toLowerCase() : '';

                    // Location Match
                    const locMatch = (location === 'all') || cardLoc.includes(location.toLowerCase());

                    // Search Match (Keywords in Title, Description, or Category Name)
                    const searchMatch = !normalizedSearch ||
                        cardTitle.includes(normalizedSearch) ||
                        cardDesc.includes(normalizedSearch) ||
                        cardCatText.includes(normalizedSearch);

                    if (locMatch && searchMatch) {
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

    // ---------------------------------------------------------
    // Event Handlers
    // ---------------------------------------------------------

    // 1. Filter by Category
    window.filterByCategory = function (category) {
        let params = getUrlParams();

        // Logic: specific to All Activities button vs others
        // If user clicks "All Activities", should we clear others? Or just add it?
        // User request: "When 'All Activities' is selected... Show: All activities".
        // Let's allow multi-select but "All Activities" overrides others in visibility logic.
        // However, better UX might be: toggle behavior. 
        // Simple toggle for now.

        if (params.categories.includes(category)) {
            params.categories = params.categories.filter(c => c !== category);
        } else {
            // If "All Activities" is clicked, we could clear others to be clean, but simple add is safer.
            // Let's just push it.
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

    // 3. Search (Real-time)
    window.searchEvents = function (term) {
        let params = getUrlParams();
        params.search = term;
        updateUrl(params);
    };

    // 4. Reset Filters
    window.resetFilters = function () {
        // Clear URL params
        const url = new URL(window.location);
        url.search = '';
        window.history.pushState({}, '', url);

        // Reset UI inputs
        document.querySelectorAll('.category-filters input[type="checkbox"]').forEach(box => box.checked = false);
        const locDropdown = document.querySelector('.location-dropdown');
        if (locDropdown) locDropdown.value = 'all';
        const searchBox = document.querySelector('.search-box');
        if (searchBox) searchBox.value = '';

        // Apply empty filter (returns to default view)
        applyFilters({ categories: [], location: 'all', search: '' });
    };

    // ---------------------------------------------------------
    // Initialise UI
    // ---------------------------------------------------------

    const currentParams = getUrlParams();

    // 1. Set Checkboxes
    document.querySelectorAll('.category-filters input[type="checkbox"]').forEach(box => {
        box.checked = currentParams.categories.includes(box.value);
    });

    // 2. Set Dropdown
    const locationDropdown = document.querySelector('.location-dropdown');
    if (locationDropdown) {
        locationDropdown.value = currentParams.location;
    }

    // 3. Set Search Box
    const searchBox = document.querySelector('.search-box');
    if (searchBox && currentParams.search) {
        searchBox.value = currentParams.search;
    }

    // 4. Initial Apply
    applyFilters(currentParams);
});

