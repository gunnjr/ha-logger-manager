/**
 * Home Assistant Logger Manager Multi-Select Card
 * Version: 3.0-step3
 */

class HaLoggerMultiselectCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._allLoggers = [];
    this._loading = false;
    this._error = null;
    this._version = null;
    this._searchQuery = '';
    this._filteredLoggers = [];
    this._selectedLoggers = new Set();
    this._debounceTimer = null;
    this._focusedIndex = -1;
  }

  set hass(hass) {
    this._hass = hass;
    if (!this._initialized) {
      this._initialized = true;
      this._fetchLoggers();
    }
  }

  async _fetchLoggers() {
    if (!this._hass) return;
    
    this._loading = true;
    this._error = null;
    this.render();

    try {
      const result = await this._hass.callWS({
        type: 'logger_manager/get_loggers'
      });
      
      this._allLoggers = result.loggers || [];
      this._version = result.cache_age || 0;
      this._loading = false;
      this._error = null;
      
      // Initial filter (empty query shows all)
      this._filterLoggers();
      
      console.log(`Logger Manager: Loaded ${this._allLoggers.length} loggers`);
      
    } catch (error) {
      console.error('Logger Manager: Failed to fetch loggers', error);
      this._loading = false;
      this._error = error.message || 'Failed to load loggers';
      this._allLoggers = [];
    }
    
    this.render();
  }

  _filterLoggers() {
    if (!this._allLoggers) {
      this._filteredLoggers = [];
      return;
    }

    const query = this._searchQuery.toLowerCase().trim();
    
    // Filter based on search query and exclude already selected items
    let filtered;
    if (!query) {
      filtered = [...this._allLoggers];
    } else {
      filtered = this._allLoggers.filter(logger => 
        logger.toLowerCase().includes(query)
      );
    }
    
    // Exclude already selected loggers from results
    this._filteredLoggers = filtered.filter(logger => !this._selectedLoggers.has(logger));
  }

  _onSearchInput(event) {
    this._searchQuery = event.target.value;
    
    // Clear existing debounce timer
    if (this._debounceTimer) {
      clearTimeout(this._debounceTimer);
    }
    
    // Debounce filter execution by 200ms
    this._debounceTimer = setTimeout(() => {
      this._filterLoggers();
      this._updateMatchCount();
      this._updateResultsList();
      this._focusedIndex = -1; // Reset focus when results change
    }, 200);
  }

  _updateMatchCount() {
    const matchCountElement = this.shadowRoot?.querySelector('.match-count');
    if (matchCountElement) {
      matchCountElement.textContent = `${this._filteredLoggers.length} matches`;
    }
  }

  _updateResultsList() {
    const resultsContainer = this.shadowRoot?.querySelector('.results-list');
    if (!resultsContainer) return;

    // Show up to 25 items to accommodate more sub-loggers
    const maxVisible = Math.min(25, this._filteredLoggers.length);
    
    resultsContainer.innerHTML = this._filteredLoggers.slice(0, maxVisible).map((logger, index) => `
      <div class="result-item" data-logger="${logger}" data-index="${index}" tabindex="0">
        <span class="logger-name">${logger}</span>
      </div>
    `).join('');

    if (this._filteredLoggers.length > maxVisible) {
      resultsContainer.innerHTML += `
        <div class="more-results">
          ... and ${this._filteredLoggers.length - maxVisible} more (scroll or narrow search)
        </div>
      `;
    }

    // Add event listeners for clicks and keyboard navigation
    resultsContainer.querySelectorAll('.result-item').forEach((item, index) => {
      item.addEventListener('keydown', (e) => this._onResultKeydown(e, index));
      item.addEventListener('click', (e) => {
        const loggerName = item.dataset.logger;
        this._onLoggerSelect(loggerName);
      });
    });
  }

  _onLoggerSelect(loggerName) {
    // Add to selection
    this._selectedLoggers.add(loggerName);

    // Re-filter to remove selected items from results
    this._filterLoggers();
    this._updateMatchCount();
    this._updateResultsList();
  }

  _onResultKeydown(event, index) {
    switch (event.key) {
      case 'ArrowDown':
        event.preventDefault();
        this._focusResultItem(index + 1);
        break;
      case 'ArrowUp':
        event.preventDefault();
        this._focusResultItem(index - 1);
        break;
      case 'Enter':
      case ' ':
        event.preventDefault();
        const loggerName = event.target.dataset.logger;
        if (loggerName) {
          this._onLoggerSelect(loggerName);
        }
        break;
      case 'Escape':
        event.preventDefault();
        const searchInput = this.shadowRoot.querySelector('.search-input');
        if (searchInput) {
          searchInput.focus();
        }
        break;
    }
  }

  _focusResultItem(index) {
    const items = this.shadowRoot.querySelectorAll('.result-item');
    if (index >= 0 && index < items.length) {
      this._focusedIndex = index;
      items[index].focus();
    }
  }

  setConfig(config) {
    this._config = config;
  }

  getCardSize() {
    return 6; // Standard card height units
  }

  render() {
    if (!this.shadowRoot) return;

    // Determine status message
    let statusContent = '';
    let statusClass = '';
    
    if (this._loading) {
      statusContent = 'Loading loggers...';
      statusClass = 'loading';
    } else if (this._error) {
      statusContent = `Error: ${this._error}`;
      statusClass = 'error';
    } else if (this._allLoggers.length > 0) {
      statusContent = `Loaded ${this._allLoggers.length} loggers`;
      statusClass = 'success';
    } else {
      statusContent = 'No loggers found';
      statusClass = 'empty';
    }

    // Show search input and match count if data is loaded
    const showSearch = !this._loading && !this._error && this._allLoggers.length > 0;
    const matchCount = showSearch ? this._filteredLoggers.length : 0;

    this.shadowRoot.innerHTML = `
      <style>
        :host {
          display: block;
          background: var(--ha-card-background, var(--card-background-color, white));
          border-radius: var(--ha-card-border-radius, 12px);
          border: var(--ha-card-border-width, 1px) solid var(--ha-card-border-color, var(--divider-color));
          box-shadow: var(--ha-card-box-shadow, var(--shadow-elevation-2dp));
          padding: 0;
          overflow: hidden;
        }

        .card-header {
          padding: 16px;
          border-bottom: 1px solid var(--divider-color);
          background: var(--ha-card-header-background, transparent);
        }

        .card-title {
          margin: 0;
          font-size: 20px;
          font-weight: 500;
          color: var(--primary-text-color);
          font-family: var(--paper-font-headline_-_font-family);
        }

        .version-info {
          font-size: 10px;
          color: var(--secondary-text-color);
          opacity: 0.5;
          margin-top: 4px;
        }

        .card-content {
          padding: 16px;
          color: var(--primary-text-color);
        }

        .search-section {
          margin-bottom: 16px;
        }

        .search-input {
          width: 100%;
          padding: 12px;
          border: 1px solid var(--divider-color);
          border-radius: var(--control-border-radius, 8px);
          background: var(--card-background-color, white);
          color: var(--primary-text-color);
          font-family: inherit;
          font-size: 14px;
          box-sizing: border-box;
        }

        .search-input:focus {
          outline: none;
          border-color: var(--primary-color);
          box-shadow: 0 0 0 2px var(--primary-color)22;
        }

        .search-input::placeholder {
          color: var(--secondary-text-color);
        }

        .match-count {
          margin-top: 8px;
          font-size: 12px;
          color: var(--secondary-text-color);
        }

        .results-section {
          margin-top: 16px;
        }

        .results-list {
          max-height: 300px;
          overflow-y: auto;
          border: 1px solid var(--divider-color);
          border-radius: var(--control-border-radius, 8px);
          background: var(--card-background-color, white);
        }

        .result-item {
          padding: 12px 16px;
          border-bottom: 1px solid var(--divider-color);
          cursor: pointer;
          outline: none;
          transition: background-color 0.2s ease;
        }

        .result-item:last-child {
          border-bottom: none;
        }

        .result-item:hover {
          background: var(--secondary-background-color, #f5f5f5);
        }

        .result-item:focus {
          background: var(--primary-color)11;
          border-left: 3px solid var(--primary-color);
        }

        .logger-name {
          display: block;
          font-size: 14px;
          color: var(--primary-text-color);
          font-family: var(--code-font-family, monospace);
          word-break: break-all;
        }

        .more-results {
          padding: 8px 12px;
          font-size: 12px;
          color: var(--secondary-text-color);
          font-style: italic;
          text-align: center;
          background: var(--secondary-background-color, #f5f5f5);
        }

        .status-section {
          min-height: 100px;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .status-text {
          color: var(--secondary-text-color);
          font-size: 14px;
          text-align: center;
        }

        .status-text.loading {
          color: var(--primary-color);
        }

        .status-text.success {
          color: var(--success-color, var(--green-color, #4caf50));
        }

        .status-text.error {
          color: var(--error-color, var(--red-color, #f44336));
        }

        .status-text.empty {
          color: var(--warning-color, var(--orange-color, #ff9800));
        }

        /* Responsive design */
        @media (max-width: 768px) {
          .card-header {
            padding: 12px;
          }
          
          .card-content {
            padding: 12px;
          }
          
          .card-title {
            font-size: 18px;
          }
        }

        /* Dark mode compatibility */
        .status-text {
          opacity: 0.7;
        }
      </style>

      <div class="card-header">
        <h2 class="card-title">Logger Picker</h2>
        <div class="version-info">v3.3-longer-list</div>
      </div>
      
      <div class="card-content">
        ${showSearch ? `
          <div class="search-section">
            <input 
              type="text" 
              class="search-input" 
              placeholder="Search loggers..." 
              value="${this._searchQuery}"
            />
            <div class="match-count">
              <span>${matchCount} matches</span>
            </div>
          </div>
          
          ${matchCount > 0 ? `
            <div class="results-section">
              <div class="results-list"></div>
            </div>
          ` : ''}
        ` : ''}
        
        ${!showSearch ? `
          <div class="status-section">
            <div class="status-text ${statusClass}">
              ${statusContent}
            </div>
          </div>
        ` : ''}
      </div>
    `;

    // Add event listeners for search input
    if (showSearch) {
      const searchInput = this.shadowRoot.querySelector('.search-input');
      if (searchInput) {
        searchInput.addEventListener('input', (e) => this._onSearchInput(e));
        
        // Handle Enter key to focus first result
        searchInput.addEventListener('keydown', (e) => {
          if (e.key === 'Enter') {
            e.preventDefault();
            this._focusResultItem(0);
          }
        });
      }

      // Initialize results list if we have matches
      if (matchCount > 0) {
        this._updateResultsList();
      }
    }
  }
}

// Register the custom card
(function() {
  if (!customElements.get('ha-logger-multiselect-card')) {
    customElements.define('ha-logger-multiselect-card', HaLoggerMultiselectCard);
  }
})();

// Register with HA's card picker
window.customCards = window.customCards || [];
window.customCards.push({
  type: 'ha-logger-multiselect-card',
  name: 'Logger Manager Card',
  description: 'Multi-select logger management interface',
  preview: false,
  documentationURL: 'https://github.com/gunnjr/ha-logger-manager'
});

console.info('Logger Manager Card loaded');