class LoggerManagerCardV2 extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._selectedLoggers = [];
  }

  setConfig(config) {
    if (!config) {
      throw new Error('Invalid configuration');
    }
    this._config = {
      title: 'Logger Manager',
      ...config
    };
  }

  set hass(hass) {
    this._hass = hass;
    this.render();
  }

  // Get available loggers from our sensor
  getAvailableLoggers() {
    if (!this._hass) {
      console.log('Logger Manager Card V2: No hass instance');
      return [];
    }
    
    const sensor = this._hass.states['sensor.logger_manager'];
    if (!sensor) {
      console.log('Logger Manager Card V2: sensor.logger_manager not found');
      return [];
    }
    
    if (!sensor.attributes) {
      console.log('Logger Manager Card V2: Sensor has no attributes');
      return [];
    }
    
    console.log('Logger Manager Card V2: Sensor attributes:', sensor.attributes);
    
    // Get loggers from sensor samples
    const samples = sensor.attributes.logger_samples || {};
    console.log('Logger Manager Card V2: Logger samples:', samples);
    
    const loggers = [
      ...(samples.homeassistant_sample || []),
      ...(samples.custom_sample || []),
      ...(samples.library_sample || [])
    ];
    
    console.log('Logger Manager Card V2: Extracted loggers from samples:', loggers);
    
    // Add some common loggers that users often need
    const common_loggers = [
      "homeassistant.core",
      "homeassistant.components", 
      "homeassistant.components.automation",
      "homeassistant.components.script",
      "homeassistant.components.template",
      "homeassistant.helpers",
      "custom_components.logger_manager"
    ];
    
    // Combine and dedupe
    const allLoggers = [...new Set([...loggers, ...common_loggers])];
    console.log('Logger Manager Card V2: Final logger list:', allLoggers);
    return allLoggers.sort();
  }

  // Get current level for a logger
  _getCurrentLevel(loggerName) {
    // Default to DEBUG if we can't determine current level
    // In a full implementation, we'd query the actual logger state
    return 'debug';
  }

  // Remove a logger from selected list
  _removeLogger(loggerName) {
    this._selectedLoggers = this._selectedLoggers.filter(logger => logger !== loggerName);
    this.render();
  }

  // Add a logger to selected list
  _addLogger(loggerName) {
    if (loggerName && !this._selectedLoggers.includes(loggerName)) {
      this._selectedLoggers = [...this._selectedLoggers, loggerName];
      this.render();
    }
  }

  // Handle logger addition from generic picker
  _onLoggerAdd(event) {
    const loggerName = event.detail.value;
    console.log('Logger added:', loggerName);
    if (loggerName) {
      this._addLogger(loggerName);
      // Clear the picker value
      const picker = this.shadowRoot.querySelector('ha-generic-picker');
      if (picker) {
        picker.value = '';
      }
    }
  }

  // Handle level change and call service
  async _onLevelChange(event) {
    const level = event.target.value;
    
    if (!this._selectedLoggers.length || !level) {
      return;
    }
    
    try {
      // Call our apply_levels service for all selected loggers
      await this._hass.callService('logger_manager', 'apply_levels', {
        level: level,
        loggers: this._selectedLoggers
      });
      
      // Show success feedback
      this._showFeedback('success', `Set ${this._selectedLoggers.length} logger(s) to ${level.toUpperCase()}`);
    } catch (error) {
      console.error('Failed to set logger levels:', error);
      this._showFeedback('error', `Failed: ${error.message}`);
    }
  }

  // Show user feedback
  _showFeedback(type, message) {
    const feedback = this.shadowRoot.querySelector('#feedback');
    if (!feedback) return;
    
    feedback.textContent = message;
    feedback.className = `feedback ${type}`;
    feedback.style.display = 'block';
    
    // Auto-hide after 3 seconds
    setTimeout(() => {
      feedback.style.display = 'none';
    }, 3000);
  }

  // Create logger picker items for ha-generic-picker
  _getLoggerItems() {
    const availableLoggers = this.getAvailableLoggers();
    
    return availableLoggers
      .filter(logger => !this._selectedLoggers.includes(logger))
      .map(logger => ({
        value: logger,
        label: logger,
        primary: logger,
        secondary: this._getLoggerDescription(logger)
      }));
  }

  // Get description for a logger
  _getLoggerDescription(logger) {
    if (logger.startsWith('homeassistant.core')) return 'Core Home Assistant functionality';
    if (logger.startsWith('homeassistant.components.')) {
      const component = logger.split('.').pop();
      return `${component} integration`;
    }
    if (logger.startsWith('homeassistant.helpers')) return 'Home Assistant helpers';
    if (logger.startsWith('custom_components.')) {
      const component = logger.split('.')[1];
      return `Custom: ${component}`;
    }
    return 'Logger';
  }

  // Render logger item in dropdown
  _rowRenderer(item) {
    return `
      <div style="padding: 8px 12px; display: flex; flex-direction: column;">
        <span style="font-weight: 500;">${item.primary}</span>
        <span style="font-size: 12px; color: var(--secondary-text-color);">${item.secondary}</span>
      </div>
    `;
  }

  // Search function for filtering loggers
  _searchFunction(search, items) {
    if (!search) return items;
    
    const searchLower = search.toLowerCase();
    return items.filter(item => 
      item.label.toLowerCase().includes(searchLower) ||
      item.secondary.toLowerCase().includes(searchLower)
    );
  }

  render() {
    if (!this._hass || !this._config) {
      return;
    }

    const availableLoggers = this.getAvailableLoggers();
    const loggerItems = this._getLoggerItems();
    const levels = ['debug', 'info', 'warning', 'error', 'critical'];

    this.shadowRoot.innerHTML = `
      <style>
        :host {
          display: block;
        }
        ha-card {
          padding: 16px;
        }
        .card-header {
          font-size: 1.2em;
          font-weight: 500;
          margin-bottom: 16px;
          color: var(--primary-text-color);
        }
        .selected-loggers {
          margin-bottom: 16px;
        }
        .logger-chip {
          display: inline-flex;
          align-items: center;
          background: var(--primary-color);
          color: var(--text-primary-color);
          padding: 4px 8px;
          margin: 4px 4px 4px 0;
          border-radius: 16px;
          font-size: 14px;
          max-width: 100%;
        }
        .logger-chip span {
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
          flex: 1;
          min-width: 0;
        }
        .logger-chip button {
          background: none;
          border: none;
          color: inherit;
          cursor: pointer;
          margin-left: 8px;
          padding: 0;
          font-size: 16px;
          line-height: 1;
          opacity: 0.8;
        }
        .logger-chip button:hover {
          opacity: 1;
        }
        .form-row {
          display: flex;
          align-items: center;
          margin-bottom: 12px;
          gap: 12px;
        }
        label {
          min-width: 70px;
          font-weight: 500;
          color: var(--primary-text-color);
        }
        select, ha-generic-picker {
          flex: 1;
          --mdc-theme-primary: var(--primary-color);
        }
        select {
          padding: 8px 12px;
          border: 1px solid var(--divider-color);
          border-radius: 4px;
          background: var(--card-background-color);
          color: var(--primary-text-color);
          font-size: 14px;
        }
        select:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }
        .feedback {
          padding: 8px 12px;
          border-radius: 4px;
          margin-top: 12px;
          font-size: 14px;
          display: none;
        }
        .feedback.success {
          background: var(--success-color, #4caf50);
          color: white;
        }
        .feedback.error {
          background: var(--error-color, #f44336);
          color: white;
        }
        .info {
          color: var(--secondary-text-color);
          font-size: 14px;
          margin-top: 8px;
        }
        .empty-state {
          color: var(--secondary-text-color);
          font-style: italic;
          padding: 8px 0;
        }
      </style>
      
      <ha-card>
        <div class="card-header">${this._config.title}</div>
        
        <div class="selected-loggers">
          ${this._selectedLoggers.length > 0 ? 
            this._selectedLoggers.map(logger => `
              <div class="logger-chip">
                <span title="${logger}">${logger}</span>
                <button type="button" @click="${() => this._removeLogger(logger)}">&times;</button>
              </div>
            `).join('') :
            '<div class="empty-state">No loggers selected</div>'
          }
        </div>
        
        <div class="form-row">
          <label for="logger-picker">Add Logger:</label>
          <ha-generic-picker
            id="logger-picker"
            label=""
            placeholder="Search for a logger..."
            .hass="${this._hass}"
            .items="${loggerItems}"
            .rowRenderer="${this._rowRenderer.bind(this)}"
            .searchFn="${this._searchFunction.bind(this)}"
            allow-custom-value
            @value-changed="${this._onLoggerAdd.bind(this)}"
          ></ha-generic-picker>
        </div>
        
        <div class="form-row">
          <label for="level-select">Level:</label>
          <select id="level-select" ${this._selectedLoggers.length === 0 ? 'disabled' : ''}>
            ${levels.map(level => `
              <option value="${level}">${level.toUpperCase()}</option>
            `).join('')}
          </select>
        </div>
        
        <div id="feedback" class="feedback"></div>
        
        <div class="info">
          ${this._selectedLoggers.length} logger${this._selectedLoggers.length !== 1 ? 's' : ''} selected
          | ${availableLoggers.length} available
        </div>
      </ha-card>
    `;
    
    // Attach event listener for level changes
    const levelSelect = this.shadowRoot.querySelector('#level-select');
    if (levelSelect) {
      levelSelect.addEventListener('change', this._onLevelChange.bind(this));
    }

    // Handle logger chip remove buttons
    this.shadowRoot.querySelectorAll('.logger-chip button').forEach((button, index) => {
      button.addEventListener('click', () => {
        this._removeLogger(this._selectedLoggers[index]);
      });
    });
  }
}

// Register the custom card
customElements.define('logger-manager-card-v2', LoggerManagerCardV2);

// Register with HA's custom card system
window.customCards = window.customCards || [];
window.customCards.push({
  type: 'logger-manager-card-v2',
  name: 'Logger Manager Card V2',
  description: 'Multi-select logger management with search functionality',
  preview: false,
  documentationURL: 'https://github.com/gunnjr/ha-logger-manager',
});

console.info(
  '%c LOGGER-MANAGER-CARD-V2 %c v2.0.0 ',
  'color: orange; font-weight: bold; background: black',
  'color: white; font-weight: bold; background: dimgray',
);