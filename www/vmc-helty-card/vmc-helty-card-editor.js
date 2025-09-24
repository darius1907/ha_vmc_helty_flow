/**
 * VMC Helty Card Editor
 * Configuration editor for the VMC Helty control card
 */

class VmcHeltyCardEditor extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._config = {};
    this._hass = {};
  }

  setConfig(config) {
    this._config = { ...config };
    this.render();
  }

  set hass(hass) {
    this._hass = hass;
    this.updateEntityOptions();
  }

  render() {
    this.shadowRoot.innerHTML = `
      <style>
        ${this._getStyles()}
      </style>
      <div class="card-config">
        <div class="config-section">
          <label class="config-label">Entity (Required)</label>
          <select class="config-input" id="entitySelect">
            <option value="">Select VMC Fan Entity</option>
          </select>
          <small class="config-help">Choose the main fan entity for your VMC Helty device</small>
        </div>

        <div class="config-section">
          <label class="config-label">Card Name</label>
          <input type="text" class="config-input" id="nameInput" 
                 placeholder="VMC Helty" value="${this._config.name || ''}">
          <small class="config-help">Display name for the card header</small>
        </div>

        <div class="config-section">
          <label class="config-label">Display Options</label>
          <div class="config-options">
            <label class="option-item">
              <input type="checkbox" id="showTemperature" 
                     ${this._config.show_temperature !== false ? 'checked' : ''}>
              <span>Show Temperature Sensors</span>
            </label>
            <label class="option-item">
              <input type="checkbox" id="showHumidity" 
                     ${this._config.show_humidity !== false ? 'checked' : ''}>
              <span>Show Humidity Sensor</span>
            </label>
            <label class="option-item">
              <input type="checkbox" id="showCO2" 
                     ${this._config.show_co2 !== false ? 'checked' : ''}>
              <span>Show CO₂ Sensor (Elite only)</span>
            </label>
            <label class="option-item">
              <input type="checkbox" id="showVOC" 
                     ${this._config.show_voc !== false ? 'checked' : ''}>
              <span>Show VOC Sensor (Elite only)</span>
            </label>
            <label class="option-item">
              <input type="checkbox" id="showLights" 
                     ${this._config.show_lights !== false ? 'checked' : ''}>
              <span>Show Light Controls</span>
            </label>
            <label class="option-item">
              <input type="checkbox" id="showAdvanced" 
                     ${this._config.show_advanced === true ? 'checked' : ''}>
              <span>Show Advanced Sensors</span>
            </label>
          </div>
        </div>

        <div class="config-section">
          <label class="config-label">Theme</label>
          <select class="config-input" id="themeSelect">
            <option value="default" ${this._config.theme === 'default' ? 'selected' : ''}>Default</option>
            <option value="compact" ${this._config.theme === 'compact' ? 'selected' : ''}>Compact</option>
            <option value="minimal" ${this._config.theme === 'minimal' ? 'selected' : ''}>Minimal</option>
          </select>
          <small class="config-help">Choose card layout theme</small>
        </div>

        <div class="config-section">
          <label class="config-label">Advanced Configuration</label>
          <textarea class="config-textarea" id="advancedConfig" 
                    placeholder="Additional YAML configuration...">${this._getAdvancedConfigText()}</textarea>
          <small class="config-help">Advanced options in YAML format</small>
        </div>
      </div>
    `;

    this._attachEventListeners();
    this.updateEntityOptions();
  }

  updateEntityOptions() {
    const entitySelect = this.shadowRoot.getElementById('entitySelect');
    if (!entitySelect || !this._hass) return;

    // Clear existing options (keep placeholder)
    entitySelect.innerHTML = '<option value="">Select VMC Fan Entity</option>';

    // Get all fan entities
    const fanEntities = Object.keys(this._hass.states)
      .filter(entityId => entityId.startsWith('fan.'))
      .filter(entityId => {
        const entity = this._hass.states[entityId];
        const friendlyName = entity.attributes.friendly_name || entityId;
        return friendlyName.toLowerCase().includes('vmc') || 
               friendlyName.toLowerCase().includes('helty') ||
               entityId.includes('vmc') ||
               entityId.includes('helty');
      })
      .sort();

    // Add VMC/Helty fan entities
    fanEntities.forEach(entityId => {
      const entity = this._hass.states[entityId];
      const friendlyName = entity.attributes.friendly_name || entityId;
      
      const option = document.createElement('option');
      option.value = entityId;
      option.textContent = `${friendlyName} (${entityId})`;
      option.selected = entityId === this._config.entity;
      
      entitySelect.appendChild(option);
    });

    // Add separator and all fan entities if no VMC entities found
    if (fanEntities.length === 0) {
      const separator = document.createElement('option');
      separator.disabled = true;
      separator.textContent = '--- All Fan Entities ---';
      entitySelect.appendChild(separator);

      Object.keys(this._hass.states)
        .filter(entityId => entityId.startsWith('fan.'))
        .sort()
        .forEach(entityId => {
          const entity = this._hass.states[entityId];
          const friendlyName = entity.attributes.friendly_name || entityId;
          
          const option = document.createElement('option');
          option.value = entityId;
          option.textContent = `${friendlyName} (${entityId})`;
          option.selected = entityId === this._config.entity;
          
          entitySelect.appendChild(option);
        });
    }
  }

  _attachEventListeners() {
    // Entity selection
    const entitySelect = this.shadowRoot.getElementById('entitySelect');
    entitySelect.addEventListener('change', (e) => {
      this._updateConfig({ entity: e.target.value });
    });

    // Name input
    const nameInput = this.shadowRoot.getElementById('nameInput');
    nameInput.addEventListener('input', (e) => {
      this._updateConfig({ name: e.target.value });
    });

    // Display options
    const checkboxes = [
      'showTemperature',
      'showHumidity', 
      'showCO2',
      'showVOC',
      'showLights',
      'showAdvanced'
    ];

    checkboxes.forEach(id => {
      const checkbox = this.shadowRoot.getElementById(id);
      if (checkbox) {
        checkbox.addEventListener('change', (e) => {
          const configKey = id.replace('show', 'show_').toLowerCase();
          this._updateConfig({ [configKey]: e.target.checked });
        });
      }
    });

    // Theme selection
    const themeSelect = this.shadowRoot.getElementById('themeSelect');
    themeSelect.addEventListener('change', (e) => {
      this._updateConfig({ theme: e.target.value });
    });

    // Advanced configuration
    const advancedConfig = this.shadowRoot.getElementById('advancedConfig');
    advancedConfig.addEventListener('input', (e) => {
      try {
        const yamlConfig = this._parseYAML(e.target.value);
        this._updateConfig(yamlConfig);
      } catch (error) {
        // Invalid YAML - don't update config
        console.warn('Invalid YAML configuration:', error);
      }
    });
  }

  _updateConfig(updates) {
    this._config = { ...this._config, ...updates };
    
    // Dispatch configuration change event
    const event = new CustomEvent('config-changed', {
      detail: { config: this._config },
      bubbles: true,
      composed: true
    });
    this.dispatchEvent(event);
  }

  _getAdvancedConfigText() {
    const advancedKeys = ['volume_m3', 'location', 'custom_entities'];
    const advancedConfig = {};
    
    advancedKeys.forEach(key => {
      if (this._config[key] !== undefined) {
        advancedConfig[key] = this._config[key];
      }
    });

    if (Object.keys(advancedConfig).length === 0) {
      return '';
    }

    return this._stringifyYAML(advancedConfig);
  }

  _parseYAML(yamlString) {
    if (!yamlString.trim()) return {};
    
    // Simple YAML parser for basic key-value pairs
    const lines = yamlString.split('\n');
    const config = {};
    
    lines.forEach(line => {
      line = line.trim();
      if (line && !line.startsWith('#')) {
        const colonIndex = line.indexOf(':');
        if (colonIndex > 0) {
          const key = line.substring(0, colonIndex).trim();
          const value = line.substring(colonIndex + 1).trim();
          
          // Parse value type
          if (value === 'true' || value === 'false') {
            config[key] = value === 'true';
          } else if (!isNaN(value) && value !== '') {
            config[key] = parseFloat(value);
          } else {
            config[key] = value.replace(/['"]/g, '');
          }
        }
      }
    });
    
    return config;
  }

  _stringifyYAML(obj) {
    return Object.entries(obj)
      .map(([key, value]) => {
        if (typeof value === 'string') {
          return `${key}: "${value}"`;
        }
        return `${key}: ${value}`;
      })
      .join('\n');
  }

  _getStyles() {
    return `
      .card-config {
        padding: 16px;
      }

      .config-section {
        margin-bottom: 24px;
      }

      .config-label {
        display: block;
        margin-bottom: 8px;
        font-weight: 500;
        color: var(--primary-text-color, #212121);
      }

      .config-input,
      .config-textarea {
        width: 100%;
        padding: 8px 12px;
        border: 1px solid var(--divider-color, #e0e0e0);
        border-radius: 4px;
        background: var(--card-background-color, white);
        color: var(--primary-text-color, #212121);
        font-family: inherit;
        font-size: 14px;
        box-sizing: border-box;
      }

      .config-input:focus,
      .config-textarea:focus {
        outline: none;
        border-color: var(--primary-color, #2196f3);
        box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.2);
      }

      .config-textarea {
        min-height: 100px;
        font-family: monospace;
        resize: vertical;
      }

      .config-help {
        display: block;
        margin-top: 4px;
        color: var(--secondary-text-color, #757575);
        font-size: 12px;
      }

      .config-options {
        display: flex;
        flex-direction: column;
        gap: 8px;
      }

      .option-item {
        display: flex;
        align-items: center;
        gap: 8px;
        cursor: pointer;
      }

      .option-item input[type="checkbox"] {
        width: auto;
        margin: 0;
      }

      .option-item:hover {
        background: var(--secondary-background-color, #fafafa);
        padding: 4px;
        border-radius: 4px;
        margin: -4px;
      }
    `;
  }
}

customElements.define('vmc-helty-card-editor', VmcHeltyCardEditor);