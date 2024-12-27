// Search functionality with enhanced features
function initSearch() {
    return {
        searchQuery: '',
        searchResults: [],
        showResults: false,
        isLoading: false,
        searchIndex: null,
        selectedIndex: -1,
        recentSearches: [],
        maxRecentSearches: 5,

        async init() {
            // Load search index
            try {
                const response = await fetch('/search-index.json');
                this.searchIndex = await response.json();
                
                // Load recent searches from localStorage
                const stored = localStorage.getItem('recentSearches');
                if (stored) {
                    this.recentSearches = JSON.parse(stored);
                }
            } catch (error) {
                console.error('Failed to load search index:', error);
            }
        },

        async search() {
            if (!this.searchQuery.trim()) {
                this.searchResults = [];
                this.showResults = false;
                return;
            }

            this.isLoading = true;
            this.showResults = true;
            this.selectedIndex = -1;

            // Simulate search delay
            await new Promise(resolve => setTimeout(resolve, 300));

            const query = this.searchQuery.toLowerCase();
            
            // Fuzzy search implementation
            this.searchResults = this.searchIndex
                .map(item => {
                    const titleScore = this.fuzzyMatch(query, item.title.toLowerCase());
                    const contentScore = this.fuzzyMatch(query, item.content.toLowerCase());
                    const tagScore = Math.max(...item.tags.map(tag => this.fuzzyMatch(query, tag.toLowerCase())));
                    
                    return {
                        ...item,
                        score: Math.max(titleScore * 2, contentScore, tagScore) // Title matches are weighted more
                    };
                })
                .filter(item => item.score > 0.3) // Minimum score threshold
                .sort((a, b) => b.score - a.score)
                .slice(0, 10); // Limit to 10 results

            this.isLoading = false;
        },

        fuzzyMatch(pattern, str) {
            pattern = pattern.toLowerCase();
            str = str.toLowerCase();
            
            if (str.includes(pattern)) return 1.0; // Exact substring match
            
            let score = 0;
            let patternIdx = 0;
            let strIdx = 0;
            let prevMatchIdx = -1;
            
            while (patternIdx < pattern.length && strIdx < str.length) {
                if (pattern[patternIdx] === str[strIdx]) {
                    score += 1;
                    if (prevMatchIdx !== -1) {
                        // Reduce score for gaps between matches
                        score -= (strIdx - prevMatchIdx - 1) * 0.1;
                    }
                    prevMatchIdx = strIdx;
                    patternIdx++;
                }
                strIdx++;
            }
            
            return patternIdx === pattern.length ? score / pattern.length : 0;
        },

        handleKeyDown(event) {
            if (!this.showResults) return;

            switch (event.key) {
                case 'ArrowDown':
                    event.preventDefault();
                    this.selectedIndex = Math.min(this.selectedIndex + 1, this.searchResults.length - 1);
                    this.scrollSelectedIntoView();
                    break;
                case 'ArrowUp':
                    event.preventDefault();
                    this.selectedIndex = Math.max(this.selectedIndex - 1, -1);
                    this.scrollSelectedIntoView();
                    break;
                case 'Enter':
                    event.preventDefault();
                    if (this.selectedIndex >= 0) {
                        this.navigateToResult(this.searchResults[this.selectedIndex]);
                    }
                    break;
                case 'Escape':
                    event.preventDefault();
                    this.showResults = false;
                    break;
            }
        },

        scrollSelectedIntoView() {
            if (this.selectedIndex >= 0) {
                const selected = document.querySelector(`[data-result-index="${this.selectedIndex}"]`);
                if (selected) {
                    selected.scrollIntoView({ block: 'nearest' });
                }
            }
        },

        navigateToResult(result) {
            // Add to recent searches
            if (!this.recentSearches.includes(this.searchQuery)) {
                this.recentSearches.unshift(this.searchQuery);
                this.recentSearches = this.recentSearches.slice(0, this.maxRecentSearches);
                localStorage.setItem('recentSearches', JSON.stringify(this.recentSearches));
            }

            window.location.href = result.url;
        },

        highlightMatch(text) {
            if (!this.searchQuery) return text;
            
            const regex = new RegExp(`(${this.escapeRegExp(this.searchQuery)})`, 'gi');
            return text.replace(regex, '<mark class="bg-yellow-200">$1</mark>');
        },

        escapeRegExp(string) {
            return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        }
    };
}

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Press '/' to focus search
    if (e.key === '/' && !e.ctrlKey && !e.metaKey && !e.target.closest('input, textarea')) {
        e.preventDefault();
        document.querySelector('#search-input')?.focus();
    }
});
