/**
 * VMC Helty Control Card
 * Custom Lovelace card for VMC Helty Flow Plus/Elite control
 * 
 * Features:
 * - Real-time environmental monitoring
 * - Fan speed control with visual feedback
 * - Advanced sensors display (temperature, humidity, CO2, VOC)
 * - Automation status and controls
 * - Responsive design for mobile/desktop
 */

class VmcHeltyCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._config = {};
    this._hass = {};
    this._entities = {};
  }

  /**
   * Set configuration from YAML
   */
  setConfig(config) {
    if (!config) {
      throw new Error('Invalid configuration');
    }

    // Required configuration validation
    if (!config.entity) {
      throw new Error('Please define a fan entity');
    }

    this._config = {
      entity: config.entity,
      name: config.name || 'VMC Helty',
      show_temperature: config.show_temperature !== false,
      show_humidity: config.show_humidity !== false,
      show_co2: config.show_co2 !== false,
      show_voc: config.show_voc !== false,
      show_lights: config.show_lights !== false,
      show_advanced: config.show_advanced !== false,
      theme: config.theme || 'default',
      ...config
    };

    this._setupEntityReferences();
    this.render();
  }

  /**
   * Setup entity references based on configuration
   */
  _setupEntityReferences() {
    const baseDomain = this._config.entity.split('.')[0];
    const deviceId = this._config.entity.split('.')[1];
    
    this._entities = {
      fan: this._config.entity,
      temperature_internal: `sensor.${deviceId}_temperature_internal`,
      temperature_external: `sensor.${deviceId}_temperature_external`, 
      humidity: `sensor.${deviceId}_humidity`,
      co2: `sensor.${deviceId}_co2`,
      voc: `sensor.${deviceId}_voc`,
      dew_point: `sensor.${deviceId}_dew_point`,
      comfort_index: `sensor.${deviceId}_comfort_index`,
      air_exchange_time: `sensor.${deviceId}_air_exchange_time`,
      daily_air_changes: `sensor.${deviceId}_daily_air_changes`,
      light: `light.${deviceId}_lights`,
      light_timer: `light.${deviceId}_lights_timer`,
      night_mode: `switch.${deviceId}_night_mode`,
      hyperventilation: `switch.${deviceId}_hyperventilation`,
      free_cooling: `switch.${deviceId}_free_cooling`,
      panel_led: `switch.${deviceId}_panel_led`,
      sensors_enabled: `switch.${deviceId}_sensors`
    };
  }

  /**
   * Set Home Assistant object
   */
  set hass(hass) {
    const oldHass = this._hass;
    this._hass = hass;

    // Update only if entities have changed
    if (!oldHass || this._entitiesChanged(oldHass, hass)) {
      this.updateContent();
    }
  }

  /**
   * Check if any tracked entities have changed
   */
  _entitiesChanged(oldHass, newHass) {
    return Object.values(this._entities).some(entityId => {
      return oldHass.states[entityId] !== newHass.states[entityId];
    });
  }

  /**
   * Main render method
   */
  render() {
    this.shadowRoot.innerHTML = `
      <style>
        ${this._getStyles()}
      </style>
      <ha-card>
        <div class="card-header">
          <div class="header-title">
            <ha-icon icon="mdi:fan"></ha-icon>
            <span>${this._config.name}</span>
          </div>
          <div class="header-status" id="connectionStatus">
            <ha-icon icon="mdi:wifi" class="status-icon"></ha-icon>
          </div>
        </div>
        
        <div class="card-content">
          <!-- Fan Control Section -->
          <div class="control-section">
            <div class="fan-control">
              <div class="fan-display" id="fanDisplay">
                <div class="fan-icon-container">
                  <ha-icon icon="mdi:fan" class="fan-icon" id="fanIcon"></ha-icon>
                </div>
                <div class="fan-info">
                  <div class="fan-speed" id="fanSpeed">0</div>
                  <div class="fan-status" id="fanStatus">OFF</div>
                </div>
              </div>
              
              <div class="speed-controls">
                <button class="speed-btn" data-speed="0">
                  <ha-icon icon="mdi:power"></ha-icon>
                  <span>OFF</span>
                </button>
                <button class="speed-btn" data-speed="1">
                  <ha-icon icon="mdi:fan-speed-1"></ha-icon>
                  <span>1</span>
                </button>
                <button class="speed-btn" data-speed="2">
                  <ha-icon icon="mdi:fan-speed-2"></ha-icon>
                  <span>2</span>
                </button>
                <button class="speed-btn" data-speed="3">
                  <ha-icon icon="mdi:fan-speed-3"></ha-icon>
                  <span>3</span>
                </button>
                <button class="speed-btn" data-speed="4">
                  <ha-icon icon="mdi:fan-plus"></ha-icon>
                  <span>MAX</span>
                </button>
              </div>
            </div>
          </div>

          <!-- Environmental Sensors Section -->
          <div class="sensors-section" id="sensorsSection">
            <h3>Environmental Monitor</h3>
            <div class="sensors-grid">
              <!-- Temperature sensors will be populated by updateContent -->
            </div>
          </div>

          <!-- Special Modes Section -->
          <div class="modes-section" id="modesSection">
            <h3>Special Modes</h3>
            <div class="modes-grid">
              <!-- Mode controls will be populated by updateContent -->
            </div>
          </div>

          <!-- Advanced Controls Section -->
          <div class="advanced-section" id="advancedSection" style="display: none;">
            <h3>Advanced Controls</h3>
            <div class="advanced-grid">
              <!-- Advanced controls will be populated by updateContent -->
            </div>
          </div>
        </div>
      </ha-card>
    `;

    this._attachEventListeners();
    this.updateContent();
  }

  /**
   * Update dynamic content based on current state
   */
  updateContent() {
    if (!this._hass) return;

    this._updateFanStatus();
    this._updateSensors();
    this._updateModes();
    this._updateAdvancedControls();
    this._updateConnectionStatus();
  }

  /**
   * Update fan status display
   */
  _updateFanStatus() {
    const fanEntity = this._hass.states[this._entities.fan];
    if (!fanEntity) return;

    const fanIcon = this.shadowRoot.getElementById('fanIcon');
    const fanSpeed = this.shadowRoot.getElementById('fanSpeed');
    const fanStatus = this.shadowRoot.getElementById('fanStatus');
    const fanDisplay = this.shadowRoot.getElementById('fanDisplay');

    const speed = fanEntity.attributes.percentage || 0;
    const speedLevel = this._percentageToSpeedLevel(speed);
    const isRunning = fanEntity.state === 'on' && speed > 0;

    // Update display
    fanSpeed.textContent = speedLevel;
    fanStatus.textContent = this._getSpeedDescription(speedLevel);
    
    // Update visual states
    fanDisplay.className = `fan-display speed-${speedLevel}`;
    fanIcon.className = `fan-icon ${isRunning ? 'rotating' : ''}`;
    
    // Update speed button states
    this.shadowRoot.querySelectorAll('.speed-btn').forEach(btn => {
      const btnSpeed = parseInt(btn.dataset.speed);
      btn.className = `speed-btn ${btnSpeed === speedLevel ? 'active' : ''}`;
    });
  }

  /**
   * Update environmental sensors display
   */
  _updateSensors() {
    const sensorsGrid = this.shadowRoot.querySelector('.sensors-grid');
    if (!sensorsGrid) return;

    const sensors = [];

    // Temperature sensors
    if (this._config.show_temperature) {
      const tempInternal = this._hass.states[this._entities.temperature_internal];
      const tempExternal = this._hass.states[this._entities.temperature_external];
      
      if (tempInternal) {
        sensors.push(this._createSensorCard('temp_internal', {
          name: 'Internal Temp',
          value: tempInternal.state,
          unit: tempInternal.attributes.unit_of_measurement,
          icon: 'mdi:thermometer',
          className: this._getTemperatureClass(parseFloat(tempInternal.state))
        }));
      }
      
      if (tempExternal) {
        sensors.push(this._createSensorCard('temp_external', {
          name: 'External Temp', 
          value: tempExternal.state,
          unit: tempExternal.attributes.unit_of_measurement,
          icon: 'mdi:thermometer-lines',
          className: this._getTemperatureClass(parseFloat(tempExternal.state))
        }));
      }
    }

    // Humidity sensor
    if (this._config.show_humidity) {
      const humidity = this._hass.states[this._entities.humidity];
      if (humidity) {
        sensors.push(this._createSensorCard('humidity', {
          name: 'Humidity',
          value: humidity.state,
          unit: humidity.attributes.unit_of_measurement,
          icon: 'mdi:water-percent',
          className: this._getHumidityClass(parseFloat(humidity.state))
        }));
      }
    }

    // CO2 sensor (Elite only)
    if (this._config.show_co2) {
      const co2 = this._hass.states[this._entities.co2];
      if (co2 && co2.state !== 'unavailable') {
        sensors.push(this._createSensorCard('co2', {
          name: 'CO₂',
          value: co2.state,
          unit: co2.attributes.unit_of_measurement,
          icon: 'mdi:molecule-co2',
          className: this._getCO2Class(parseFloat(co2.state))
        }));
      }
    }

    // VOC sensor (Elite only)
    if (this._config.show_voc) {
      const voc = this._hass.states[this._entities.voc];
      if (voc && voc.state !== 'unavailable') {
        sensors.push(this._createSensorCard('voc', {
          name: 'VOC',
          value: voc.state,
          unit: voc.attributes.unit_of_measurement,
          icon: 'mdi:chart-line-variant',
          className: this._getVOCClass(parseFloat(voc.state))
        }));
      }
    }

    // Advanced sensors
    if (this._config.show_advanced) {
      const dewPoint = this._hass.states[this._entities.dew_point];
      if (dewPoint) {
        sensors.push(this._createSensorCard('dew_point', {
          name: 'Dew Point',
          value: dewPoint.state,
          unit: dewPoint.attributes.unit_of_measurement,
          icon: 'mdi:water',
          className: 'sensor-info'
        }));
      }

      const comfortIndex = this._hass.states[this._entities.comfort_index];
      if (comfortIndex) {
        sensors.push(this._createSensorCard('comfort', {
          name: 'Comfort',
          value: comfortIndex.state,
          unit: '',
          icon: 'mdi:account-heart',
          className: this._getComfortClass(comfortIndex.state)
        }));
      }
    }

    sensorsGrid.innerHTML = sensors.join('');
  }

  /**
   * Create sensor card HTML
   */
  _createSensorCard(id, sensor) {
    return `
      <div class="sensor-card ${sensor.className}" id="sensor_${id}">
        <div class="sensor-icon">
          <ha-icon icon="${sensor.icon}"></ha-icon>
        </div>
        <div class="sensor-info">
          <div class="sensor-name">${sensor.name}</div>
          <div class="sensor-value">
            ${sensor.value}${sensor.unit ? ' ' + sensor.unit : ''}
          </div>
        </div>
      </div>
    `;
  }

  /**
   * Update special modes display
   */
  _updateModes() {
    const modesGrid = this.shadowRoot.querySelector('.modes-grid');
    if (!modesGrid) return;

    const modes = [];

    // Night mode
    const nightMode = this._hass.states[this._entities.night_mode];
    if (nightMode) {
      modes.push(this._createModeButton('night_mode', {
        name: 'Night Mode',
        icon: 'mdi:sleep',
        state: nightMode.state === 'on',
        entity: this._entities.night_mode
      }));
    }

    // Hyperventilation
    const hypervent = this._hass.states[this._entities.hyperventilation];
    if (hypervent) {
      modes.push(this._createModeButton('hyperventilation', {
        name: 'Boost',
        icon: 'mdi:fast-forward',
        state: hypervent.state === 'on',
        entity: this._entities.hyperventilation
      }));
    }

    // Free cooling
    const freeCooling = this._hass.states[this._entities.free_cooling];
    if (freeCooling) {
      modes.push(this._createModeButton('free_cooling', {
        name: 'Free Cooling',
        icon: 'mdi:snowflake',
        state: freeCooling.state === 'on',
        entity: this._entities.free_cooling
      }));
    }

    modesGrid.innerHTML = modes.join('');
    this._attachModeListeners();
  }

  /**
   * Create mode button HTML
   */
  _createModeButton(id, mode) {
    return `
      <button class="mode-btn ${mode.state ? 'active' : ''}" 
              data-entity="${mode.entity}" 
              data-mode="${id}">
        <ha-icon icon="${mode.icon}"></ha-icon>
        <span>${mode.name}</span>
      </button>
    `;
  }

  /**
   * Update connection status
   */
  _updateConnectionStatus() {
    const statusIcon = this.shadowRoot.querySelector('.status-icon');
    const fanEntity = this._hass.states[this._entities.fan];
    
    if (fanEntity && fanEntity.state !== 'unavailable') {
      statusIcon.icon = 'mdi:wifi';
      statusIcon.className = 'status-icon connected';
    } else {
      statusIcon.icon = 'mdi:wifi-off';
      statusIcon.className = 'status-icon disconnected';
    }
  }

  /**
   * Attach event listeners
   */
  _attachEventListeners() {
    // Speed control buttons
    this.shadowRoot.querySelectorAll('.speed-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const speed = parseInt(e.currentTarget.dataset.speed);
        this._setFanSpeed(speed);
      });
    });
  }

  /**
   * Attach mode button listeners
   */
  _attachModeListeners() {
    this.shadowRoot.querySelectorAll('.mode-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const entity = e.currentTarget.dataset.entity;
        const currentState = this._hass.states[entity];
        const newState = currentState.state === 'on' ? 'off' : 'on';
        
        this._hass.callService('switch', newState === 'on' ? 'turn_on' : 'turn_off', {
          entity_id: entity
        });
      });
    });
  }

  /**
   * Set fan speed
   */
  _setFanSpeed(speedLevel) {
    const percentage = this._speedLevelToPercentage(speedLevel);
    
    if (speedLevel === 0) {
      this._hass.callService('fan', 'turn_off', {
        entity_id: this._entities.fan
      });
    } else {
      this._hass.callService('fan', 'set_percentage', {
        entity_id: this._entities.fan,
        percentage: percentage
      });
    }
  }

  /**
   * Helper methods for speed conversion
   */
  _percentageToSpeedLevel(percentage) {
    if (percentage === 0) return 0;
    if (percentage <= 25) return 1;
    if (percentage <= 50) return 2;
    if (percentage <= 75) return 3;
    return 4;
  }

  _speedLevelToPercentage(speedLevel) {
    const speedMap = { 0: 0, 1: 25, 2: 50, 3: 75, 4: 100 };
    return speedMap[speedLevel] || 0;
  }

  _getSpeedDescription(speedLevel) {
    const descriptions = {
      0: 'OFF',
      1: 'Minimum',
      2: 'Low',
      3: 'Medium',
      4: 'Maximum'
    };
    return descriptions[speedLevel] || 'Unknown';
  }

  /**
   * CSS class helpers for sensor states
   */
  _getTemperatureClass(temp) {
    if (temp < 18) return 'sensor-cold';
    if (temp > 26) return 'sensor-hot';
    return 'sensor-optimal';
  }

  _getHumidityClass(humidity) {
    if (humidity < 30) return 'sensor-low';
    if (humidity > 70) return 'sensor-high';
    return 'sensor-optimal';
  }

  _getCO2Class(co2) {
    if (co2 < 800) return 'sensor-good';
    if (co2 < 1000) return 'sensor-moderate';
    if (co2 < 1200) return 'sensor-poor';
    return 'sensor-critical';
  }

  _getVOCClass(voc) {
    if (voc < 100) return 'sensor-good';
    if (voc < 200) return 'sensor-moderate';
    if (voc < 300) return 'sensor-poor';
    return 'sensor-critical';
  }

  _getComfortClass(comfort) {
    const comfortLower = comfort.toLowerCase();
    if (comfortLower.includes('optimal') || comfortLower.includes('good')) return 'sensor-good';
    if (comfortLower.includes('acceptable')) return 'sensor-moderate';
    return 'sensor-poor';
  }

  /**
   * Get card styles
   */
  _getStyles() {
    return `
      :host {
        display: block;
      }

      ha-card {
        padding: 16px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
      }

      .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
        border-bottom: 1px solid var(--divider-color, #e0e0e0);
        padding-bottom: 12px;
      }

      .header-title {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 1.25rem;
        font-weight: 500;
      }

      .header-title ha-icon {
        color: var(--primary-color, #2196f3);
      }

      .header-status {
        display: flex;
        align-items: center;
      }

      .status-icon.connected {
        color: var(--success-color, #4caf50);
      }

      .status-icon.disconnected {
        color: var(--error-color, #f44336);
      }

      .control-section {
        margin-bottom: 24px;
      }

      .fan-control {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 20px;
      }

      .fan-display {
        display: flex;
        align-items: center;
        gap: 16px;
        padding: 16px;
        border-radius: 12px;
        background: var(--primary-color, #2196f3);
        color: white;
        transition: all 0.3s ease;
      }

      .fan-display.speed-0 { background: var(--disabled-color, #9e9e9e); }
      .fan-display.speed-1 { background: var(--info-color, #2196f3); }
      .fan-display.speed-2 { background: var(--success-color, #4caf50); }
      .fan-display.speed-3 { background: var(--warning-color, #ff9800); }
      .fan-display.speed-4 { background: var(--error-color, #f44336); }

      .fan-icon-container {
        position: relative;
      }

      .fan-icon {
        font-size: 48px;
        transition: transform 0.3s ease;
      }

      .fan-icon.rotating {
        animation: rotate 2s linear infinite;
      }

      @keyframes rotate {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
      }

      .fan-info {
        text-align: center;
      }

      .fan-speed {
        font-size: 2rem;
        font-weight: bold;
        margin-bottom: 4px;
      }

      .fan-status {
        font-size: 0.9rem;
        opacity: 0.9;
      }

      .speed-controls {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        justify-content: center;
      }

      .speed-btn {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 4px;
        padding: 12px 16px;
        border: 2px solid var(--divider-color, #e0e0e0);
        border-radius: 8px;
        background: var(--card-background-color, white);
        cursor: pointer;
        transition: all 0.2s ease;
        font-size: 0.8rem;
        min-width: 60px;
      }

      .speed-btn:hover {
        border-color: var(--primary-color, #2196f3);
        background: var(--primary-color, #2196f3);
        color: white;
      }

      .speed-btn.active {
        border-color: var(--primary-color, #2196f3);
        background: var(--primary-color, #2196f3);
        color: white;
      }

      .speed-btn ha-icon {
        font-size: 20px;
      }

      .sensors-section,
      .modes-section {
        margin-bottom: 24px;
      }

      .sensors-section h3,
      .modes-section h3 {
        margin: 0 0 12px 0;
        font-size: 1.1rem;
        font-weight: 500;
        color: var(--primary-text-color, #212121);
      }

      .sensors-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
        gap: 12px;
      }

      .sensor-card {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px;
        border-radius: 8px;
        background: var(--card-background-color, white);
        border: 1px solid var(--divider-color, #e0e0e0);
        transition: all 0.2s ease;
      }

      .sensor-card:hover {
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
      }

      .sensor-icon {
        font-size: 24px;
      }

      .sensor-info {
        flex: 1;
        min-width: 0;
      }

      .sensor-name {
        font-size: 0.8rem;
        color: var(--secondary-text-color, #757575);
        margin-bottom: 2px;
      }

      .sensor-value {
        font-size: 1rem;
        font-weight: 500;
        color: var(--primary-text-color, #212121);
      }

      /* Sensor state colors */
      .sensor-good { border-left: 4px solid var(--success-color, #4caf50); }
      .sensor-optimal { border-left: 4px solid var(--success-color, #4caf50); }
      .sensor-moderate { border-left: 4px solid var(--warning-color, #ff9800); }
      .sensor-poor { border-left: 4px solid var(--error-color, #f44336); }
      .sensor-critical { border-left: 4px solid var(--error-color, #f44336); }
      .sensor-cold { border-left: 4px solid var(--info-color, #2196f3); }
      .sensor-hot { border-left: 4px solid var(--error-color, #f44336); }
      .sensor-low { border-left: 4px solid var(--warning-color, #ff9800); }
      .sensor-high { border-left: 4px solid var(--error-color, #f44336); }
      .sensor-info { border-left: 4px solid var(--info-color, #2196f3); }

      .modes-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
        gap: 12px;
      }

      .mode-btn {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 8px;
        padding: 16px 12px;
        border: 2px solid var(--divider-color, #e0e0e0);
        border-radius: 8px;
        background: var(--card-background-color, white);
        cursor: pointer;
        transition: all 0.2s ease;
        font-size: 0.9rem;
      }

      .mode-btn:hover {
        border-color: var(--primary-color, #2196f3);
      }

      .mode-btn.active {
        border-color: var(--primary-color, #2196f3);
        background: var(--primary-color, #2196f3);
        color: white;
      }

      .mode-btn ha-icon {
        font-size: 24px;
      }

      /* Responsive design */
      @media (max-width: 768px) {
        .sensors-grid {
          grid-template-columns: 1fr 1fr;
        }
        
        .modes-grid {
          grid-template-columns: 1fr 1fr;
        }
        
        .speed-controls {
          justify-content: stretch;
        }
        
        .speed-btn {
          flex: 1;
          min-width: auto;
        }
      }

      @media (max-width: 480px) {
        .fan-display {
          flex-direction: column;
          text-align: center;
        }
        
        .sensors-grid {
          grid-template-columns: 1fr;
        }
      }
    `;
  }

  /**
   * Update advanced controls (if enabled)
   */
  _updateAdvancedControls() {
    if (!this._config.show_advanced) return;
    
    const advancedSection = this.shadowRoot.getElementById('advancedSection');
    if (advancedSection) {
      advancedSection.style.display = 'block';
      // Implementation for advanced controls...
    }
  }

  /**
   * Return card configuration editor
   */
  static getConfigElement() {
    return document.createElement('vmc-helty-card-editor');
  }

  /**
   * Return card stub configuration
   */
  static getStubConfig() {
    return {
      entity: 'fan.vmc_helty',
      name: 'VMC Helty',
      show_temperature: true,
      show_humidity: true,
      show_co2: true,
      show_voc: true
    };
  }
}

// Register the custom card
customElements.define('vmc-helty-card', VmcHeltyCard);

// Register with card picker
window.customCards = window.customCards || [];
window.customCards.push({
  type: 'vmc-helty-card',
  name: 'VMC Helty Card',
  description: 'Advanced control card for VMC Helty Flow Plus/Elite',
  preview: true
});

console.info(
  '%c VMC-HELTY-CARD %c v1.0.0 ',
  'color: orange; font-weight: bold; background: black',
  'color: white; font-weight: bold; background: dimgray'
);