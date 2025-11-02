/**
 * Logger Manager Card - MVP
 * Custom Lovelace card for Home Assistant Logger Management
 * 
 * Provides visual interface for:
 * - Discovering available logger names
 * - Setting logger levels
 * - Viewing current managed loggers
 */

class LoggerManagerCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }

  // Required LovelaceCard interface
  setConfig(config) {
    if (!config) {
      throw new Error('Invalid configuration');
    }
    this._config = {
      title: 'Logger Manager',
      ...config
    };
    this.render();
  }

  set hass(hass) {
    this._hass = hass;
    this.render();
  }

  getCardSize() {
    return 3; // Height in card units
  }

  // Get available loggers from our sensor
  _getAvailableLoggers() {
    if (!this._hass) return [];
    
    const sensor = this._hass.states['sensor.logger_levels'];
    if (!sensor || !sensor.attributes) return [];
    
    return sensor.attributes.available_loggers || [];
  }

  // Get current level for a logger
  _getCurrentLevel(loggerName) {
    if (!this._hass) return 'notset';
    
    const sensor = this._hass.states['sensor.logger_levels'];
    if (!sensor || !sensor.attributes) return 'notset';
    
    const managed = sensor.attributes.managed_loggers || {};
    return managed[loggerName] || 'notset';
  }

  // Handle logger selection change
  _onLoggerChange(event) {
    const loggerName = event.target.value;
    const levelSelect = this.shadowRoot.querySelector('#level-select');
    
    if (loggerName && levelSelect) {
      const currentLevel = this._getCurrentLevel(loggerName);
      levelSelect.value = currentLevel;
      levelSelect.disabled = false;
    } else if (levelSelect) {
      levelSelect.disabled = true;
    }
  }

  // Handle level change and call service
  async _onLevelChange(event) {
    const loggerSelect = this.shadowRoot.querySelector('#logger-select');
    const loggerName = loggerSelect.value;
    const level = event.target.value;
    
    if (!loggerName || !level) return;
    
    try {
      // Call our apply_levels service
      await this._hass.callService('logger_manager', 'apply_levels', {
        level: level,
        loggers: [loggerName]
      });
      
      // Show success feedback
      this._showFeedback('success', `Set ${loggerName} to ${level.toUpperCase()}`);
    } catch (error) {
      console.error('Failed to set logger level:', error);
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
    
    setTimeout(() => {
      feedback.style.display = 'none';
    }, 3000);
  }

  render() {
    if (!this._config || !this._hass) return;
    
    const availableLoggers = this._getAvailableLoggers();
    const levels = ['debug', 'info', 'warning', 'error', 'critical', 'notset'];
    
    this.shadowRoot.innerHTML = `
      <style>
        ha-card {
          padding: 16px;
        }
        .card-header {
          font-size: 1.2em;
          font-weight: 500;
          margin-bottom: 16px;
          color: var(--primary-text-color);
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
        select {
          flex: 1;
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
          font-size: 12px;
          color: var(--secondary-text-color);
          margin-top: 8px;
        }
      </style>
      
      <ha-card>
        <div class="card-header">${this._config.title}</div>
        
        <div class="form-row">
          <label for="logger-select">Logger:</label>
          <select id="logger-select">
            <option value="">Select a logger...</option>
            ${availableLoggers.map(logger => `
              <option value="${logger}">${logger}</option>
            `).join('')}
          </select>
        </div>
        
        <div class="form-row">
          <label for="level-select">Level:</label>
          <select id="level-select" disabled>
            ${levels.map(level => `
              <option value="${level}">${level.toUpperCase()}</option>
            `).join('')}
          </select>
        </div>
        
        <div id="feedback" class="feedback"></div>
        
        <div class="info">
          ${availableLoggers.length} logger${availableLoggers.length !== 1 ? 's' : ''} available
        </div>
      </ha-card>
    `;
    
    // Attach event listeners
    const loggerSelect = this.shadowRoot.querySelector('#logger-select');
    const levelSelect = this.shadowRoot.querySelector('#level-select');
    
    if (loggerSelect && levelSelect) {
      loggerSelect.addEventListener('change', this._onLoggerChange.bind(this));
      levelSelect.addEventListener('change', this._onLevelChange.bind(this));
    }
  }
}

// Register the custom card
customElements.define('logger-manager-card', LoggerManagerCard);

// Register with HA's custom card system
window.customCards = window.customCards || [];
window.customCards.push({
  type: 'logger-manager-card',
  name: 'Logger Manager Card',
  description: 'Visual interface for managing Home Assistant logger levels',
  preview: false,
  documentationURL: 'https://github.com/gunnjr/ha-logger-manager',
});

console.info(
  '%c LOGGER-MANAGER-CARD %c v1.0.0 MVP ',
  'color: orange; font-weight: bold; background: black',
  'color: white; font-weight: bold; background: dimgray',
);