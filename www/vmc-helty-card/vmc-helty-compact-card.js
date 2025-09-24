/**
 * VMC Helty Compact Card
 * Compact version of the VMC Helty control card for smaller layouts
 */

class VmcHeltyCompactCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._config = {};
    this._hass = {};
    this._entities = {};
  }

  setConfig(config) {
    if (!config || !config.entity) {
      throw new Error('Please define a fan entity');
    }

    this._config = {
      entity: config.entity,
      name: config.name || 'VMC',
      ...config
    };

    this._setupEntityReferences();
    this.render();
  }

  _setupEntityReferences() {
    const deviceId = this._config.entity.split('.')[1];
    this._entities = {
      fan: this._config.entity,
      temperature_internal: `sensor.${deviceId}_temperature_internal`,
      humidity: `sensor.${deviceId}_humidity`,
      co2: `sensor.${deviceId}_co2`,
    };
  }

  set hass(hass) {
    const oldHass = this._hass;
    this._hass = hass;

    if (!oldHass || this._entitiesChanged(oldHass, hass)) {
      this.updateContent();
    }
  }

  _entitiesChanged(oldHass, newHass) {
    return Object.values(this._entities).some(entityId => {
      return oldHass.states[entityId] !== newHass.states[entityId];
    });
  }

  render() {
    this.shadowRoot.innerHTML = `
      <style>
        ${this._getCompactStyles()}
      </style>
      <ha-card class="compact-card">
        <div class="compact-header">
          <div class="compact-title">
            <ha-icon icon="mdi:fan" class="title-icon" id="fanIcon"></ha-icon>
            <span>${this._config.name}</span>
          </div>
          <div class="compact-status" id="fanSpeed">0</div>
        </div>
        
        <div class="compact-content">
          <div class="compact-sensors" id="compactSensors">
            <!-- Sensors will be populated dynamically -->
          </div>
          
          <div class="compact-controls">
            <button class="compact-btn" data-speed="0">
              <ha-icon icon="mdi:power"></ha-icon>
            </button>
            <button class="compact-btn" data-speed="1">1</button>
            <button class="compact-btn" data-speed="2">2</button>
            <button class="compact-btn" data-speed="3">3</button>
            <button class="compact-btn" data-speed="4">4</button>
          </div>
        </div>
      </ha-card>
    `;

    this._attachEventListeners();
    this.updateContent();
  }

  updateContent() {
    if (!this._hass) return;
    this._updateFanStatus();
    this._updateCompactSensors();
  }

  _updateFanStatus() {
    const fanEntity = this._hass.states[this._entities.fan];
    if (!fanEntity) return;

    const fanIcon = this.shadowRoot.getElementById('fanIcon');
    const fanSpeed = this.shadowRoot.getElementById('fanSpeed');
    
    const speed = fanEntity.attributes.percentage || 0;
    const speedLevel = this._percentageToSpeedLevel(speed);
    const isRunning = fanEntity.state === 'on' && speed > 0;

    fanSpeed.textContent = speedLevel;
    fanIcon.className = `title-icon ${isRunning ? 'rotating' : ''}`;
    
    // Update button states
    this.shadowRoot.querySelectorAll('.compact-btn').forEach(btn => {
      const btnSpeed = btn.dataset.speed ? parseInt(btn.dataset.speed) : 0;
      btn.className = `compact-btn ${btnSpeed === speedLevel ? 'active' : ''}`;
    });
  }

  _updateCompactSensors() {
    const sensorsContainer = this.shadowRoot.getElementById('compactSensors');
    const sensors = [];

    // Temperature
    const tempInternal = this._hass.states[this._entities.temperature_internal];
    if (tempInternal) {
      sensors.push(`
        <div class="sensor-compact">
          <ha-icon icon="mdi:thermometer"></ha-icon>
          <span>${tempInternal.state}°</span>
        </div>
      `);
    }

    // Humidity
    const humidity = this._hass.states[this._entities.humidity];
    if (humidity) {
      sensors.push(`
        <div class="sensor-compact">
          <ha-icon icon="mdi:water-percent"></ha-icon>
          <span>${humidity.state}%</span>
        </div>
      `);
    }

    // CO2 (if available)
    const co2 = this._hass.states[this._entities.co2];
    if (co2 && co2.state !== 'unavailable') {
      sensors.push(`
        <div class="sensor-compact ${this._getCO2Class(parseFloat(co2.state))}">
          <ha-icon icon="mdi:molecule-co2"></ha-icon>
          <span>${co2.state}</span>
        </div>
      `);
    }

    sensorsContainer.innerHTML = sensors.join('');
  }

  _attachEventListeners() {
    this.shadowRoot.querySelectorAll('.compact-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const speed = e.currentTarget.dataset.speed ? parseInt(e.currentTarget.dataset.speed) : 0;
        this._setFanSpeed(speed);
      });
    });
  }

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

  _getCO2Class(co2) {
    if (co2 < 800) return 'good';
    if (co2 < 1000) return 'moderate';
    if (co2 < 1200) return 'poor';
    return 'critical';
  }

  _getCompactStyles() {
    return `
      :host {
        display: block;
      }

      .compact-card {
        padding: 12px;
        border-radius: 8px;
        min-height: auto;
      }

      .compact-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
      }

      .compact-title {
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 1rem;
        font-weight: 500;
      }

      .title-icon {
        font-size: 20px;
        color: var(--primary-color, #2196f3);
        transition: transform 0.3s ease;
      }

      .title-icon.rotating {
        animation: rotate 2s linear infinite;
      }

      @keyframes rotate {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
      }

      .compact-status {
        font-size: 1.5rem;
        font-weight: bold;
        color: var(--primary-color, #2196f3);
        min-width: 24px;
        text-align: center;
      }

      .compact-content {
        display: flex;
        flex-direction: column;
        gap: 12px;
      }

      .compact-sensors {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
      }

      .sensor-compact {
        display: flex;
        align-items: center;
        gap: 4px;
        padding: 4px 8px;
        border-radius: 12px;
        background: var(--secondary-background-color, #f5f5f5);
        font-size: 0.85rem;
        border-left: 3px solid var(--success-color, #4caf50);
      }

      .sensor-compact.good {
        border-left-color: var(--success-color, #4caf50);
      }

      .sensor-compact.moderate {
        border-left-color: var(--warning-color, #ff9800);
      }

      .sensor-compact.poor {
        border-left-color: var(--error-color, #f44336);
      }

      .sensor-compact.critical {
        border-left-color: var(--error-color, #f44336);
        background: rgba(244, 67, 54, 0.1);
      }

      .sensor-compact ha-icon {
        font-size: 16px;
      }

      .compact-controls {
        display: flex;
        gap: 4px;
        justify-content: space-between;
      }

      .compact-btn {
        flex: 1;
        padding: 8px 4px;
        border: 1px solid var(--divider-color, #e0e0e0);
        border-radius: 6px;
        background: var(--card-background-color, white);
        cursor: pointer;
        font-size: 0.85rem;
        font-weight: 500;
        transition: all 0.2s ease;
        display: flex;
        align-items: center;
        justify-content: center;
      }

      .compact-btn:hover {
        border-color: var(--primary-color, #2196f3);
        background: var(--primary-color, #2196f3);
        color: white;
      }

      .compact-btn.active {
        border-color: var(--primary-color, #2196f3);
        background: var(--primary-color, #2196f3);
        color: white;
      }

      .compact-btn ha-icon {
        font-size: 16px;
      }

      /* Mobile adjustments */
      @media (max-width: 480px) {
        .compact-card {
          padding: 8px;
        }

        .compact-sensors {
          justify-content: center;
        }

        .sensor-compact {
          padding: 2px 6px;
          font-size: 0.8rem;
        }
      }
    `;
  }

  static getConfigElement() {
    return document.createElement('vmc-helty-card-editor');
  }

  static getStubConfig() {
    return {
      entity: 'fan.vmc_helty',
      name: 'VMC'
    };
  }
}

customElements.define('vmc-helty-compact-card', VmcHeltyCompactCard);

// Register compact card variant
window.customCards = window.customCards || [];
window.customCards.push({
  type: 'vmc-helty-compact-card',
  name: 'VMC Helty Compact Card',
  description: 'Compact version of VMC Helty control card',
  preview: true
});