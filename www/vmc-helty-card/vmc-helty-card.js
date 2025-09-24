/**
 * VMC Helty Flow Control Card v2.0 - LitElement Implementation
 * Advanced Lovelace card for VMC Helty Flow Plus/Elite control
 *
 * Fully compliant with Home Assistant development guidelines:
 * - LitElement-based architecture for maximum compatibility
 * - Mobile-first responsive design
 * - HA theme system integration
 * - Complete accessibility (ARIA) support
 * - Material Design Icons (MDI) only
 * - CSP compliance (no inline styles/scripts)
 * - Performance optimized rendering
 * - Configurable device selection
 * - Custom sensor selection for advanced calculations
 * - Room volume configuration for accurate air exchange calculations
 *
 * @version 2.0.0
 * @author VMC Helty Integration Team
 */

console.info(
  `%c VMC HELTY CARD v2.0 LitElement %c Advanced VMC Helty Flow control with device & sensor selection`,
  "color: orange; font-weight: bold; background: black",
  "color: white; font-weight: normal;"
);

import {
  LitElement,
  html,
  css,
  nothing,
} from "https://unpkg.com/lit@3.1.0/index.js?module";

// VMC Helty Flow Control Card - LitElement Implementation
class VmcHeltyCard extends LitElement {
  static get properties() {
    return {
      hass: { type: Object },
      config: { type: Object },
      _loading: { type: Boolean, state: true },
      _error: { type: String, state: true },
      _entityStates: { type: Object, state: true },
    };
  }

  constructor() {
    super();
    this.config = {};
    this.hass = null;
    this._loading = false;
    this._error = null;
    this._entityStates = {};
    this._entityIds = [];
  }

  static get styles() {
    return css`
      /* Use ha-card base styles - let HA handle the styling */
      :host {
        display: block;
      }

      /* Minimal essential layout - let HA handle styling */
      .fan-controls {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(80px, 1fr));
        gap: 8px;
        margin-bottom: 16px;
      }

      .sensors-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
        gap: 16px;
        margin-bottom: 16px;
      }

      .advanced-section {
        border-top: 1px solid var(--divider-color);
        padding-top: 16px;
        margin-top: 16px;
      }

      .advanced-title {
        font-size: 16px;
        font-weight: 500;
        color: var(--primary-text-color);
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
      }

      .comfort-indicator {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 8px;
        border-radius: 12px;
        font-size: 10px;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
      }

      .comfort-excellent {
        background: var(--success-color-alpha, rgba(76, 175, 80, 0.2));
        color: var(--success-color, #4caf50);
      }

      .comfort-good {
        background: var(--info-color-alpha, rgba(33, 150, 243, 0.2));
        color: var(--info-color, #2196f3);
      }

      .comfort-fair {
        background: var(--warning-color-alpha, rgba(255, 152, 0, 0.2));
        color: var(--warning-color, #ff9800);
      }

      .comfort-poor {
        background: var(--error-color-alpha, rgba(244, 67, 54, 0.2));
        color: var(--error-color, #f44336);
      }

      .error-message {
        color: var(--error-color);
        padding: 12px;
        background: var(--error-color-alpha, rgba(244, 67, 54, 0.1));
        border-radius: var(--ha-card-border-radius, 8px);
        border: 1px solid var(--error-color);
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 8px;
      }

      .loading-message {
        color: var(--secondary-text-color);
        text-align: center;
        padding: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
      }

      ha-icon {
        --mdc-icon-size: 20px;
      }

      .fan-icon {
        --mdc-icon-size: 24px;
      }

      .fan-icon.spinning {
        animation: spin 2s linear infinite;
      }

      @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
      }

      /* Responsive Design */
      @media (max-width: 768px) {
        .sensors-grid {
          grid-template-columns: repeat(2, 1fr);
        }

        .fan-controls {
          grid-template-columns: repeat(5, 1fr);
        }
      }

      @media (max-width: 480px) {
        :host {
          padding: 12px;
        }

        .sensors-grid {
          grid-template-columns: 1fr;
        }

        .fan-controls {
          grid-template-columns: repeat(3, 1fr);
        }

        .card-title {
          font-size: 20px;
        }
      }

      /* High Contrast Mode Support */
      @media (prefers-contrast: high) {
        .fan-speed-button {
          border-width: 3px;
        }

        .sensor-card {
          border-width: 2px;
        }
      }

      /* Reduced Motion Support */
      @media (prefers-reduced-motion: reduce) {
        .fan-speed-button,
        .sensor-card {
          transition: none;
        }

        .fan-icon.spinning {
          animation: none;
        }
      }
    `;
  }

  // Configuration management
  setConfig(config) {
    if (!config) {
      throw new Error("Invalid configuration");
    }

    this.config = {
      entity: config.entity || "",
      name: config.name || "VMC Helty Flow",
      temperature_entity: config.temperature_entity || "",
      humidity_entity: config.humidity_entity || "",
      room_volume: this._validateRoomVolume(config.room_volume),
      show_temperature: config.show_temperature !== false,
      show_humidity: config.show_humidity !== false,
      show_co2: config.show_co2 !== false,
      show_voc: config.show_voc !== false,
      show_advanced: config.show_advanced !== false,
      enable_comfort_calculations: config.enable_comfort_calculations !== false,
      enable_air_exchange: config.enable_air_exchange !== false,
      theme: config.theme || "default",
      layout: config.layout || "auto"
    };

    // Validate required entity
    if (!this.config.entity) {
      throw new Error("Please define a VMC fan entity");
    }

    // Setup entity references
    this._setupEntityReferences();
  }

  // Lifecycle methods
  willUpdate(changedProps) {
    super.willUpdate(changedProps);

    if (changedProps.has('hass') && this.hass) {
      this._updateEntityStates();
    }
  }

  // Validation and sanitization methods
  _sanitizeString(input) {
    if (typeof input !== "string") return "";

    // Basic XSS prevention
    return input
      .replace(/<script[^>]*>.*?<\/script>/gi, "")
      .replace(/on\w+="[^"]*"/gi, "")
      .replace(/javascript:/gi, "")
      .trim()
      .slice(0, 100);
  }

  _validateRoomVolume(volume) {
    const numVolume = parseFloat(volume);

    if (isNaN(numVolume) || numVolume < 1 || numVolume > 10000) {
      return 60; // Default room volume
    }

    return Math.round(numVolume * 10) / 10;
  }

  _setupEntityReferences() {
    const entities = new Set();

    if (this.config.entity) {
      entities.add(this.config.entity);
    }

    if (this.config.temperature_entity) {
      entities.add(this.config.temperature_entity);
    }

    if (this.config.humidity_entity) {
      entities.add(this.config.humidity_entity);
    }

    this._entityIds = Array.from(entities);
  }

  _updateEntityStates() {
    if (!this.hass) return;

    const newStates = {};
    this._entityIds.forEach(entityId => {
      const state = this.hass.states[entityId];
      if (state) {
        newStates[entityId] = state;
      }
    });

    if (JSON.stringify(newStates) !== JSON.stringify(this._entityStates)) {
      this._entityStates = newStates;
    }
  }

  // Entity state getters
  _getEntityState(entityId) {
    if (!this.hass || !entityId) return null;
    return this.hass.states[entityId] || null;
  }

  _getVmcState() {
    return this._getEntityState(this.config.entity);
  }

  _getTemperatureState() {
    if (this.config.temperature_entity) {
      return this._getEntityState(this.config.temperature_entity);
    }
    // Fall back to VMC internal temperature sensor
    const baseEntityId = this.config.entity.replace('fan.', '');
    return this._getEntityState(`sensor.${baseEntityId}_temperature_internal`);
  }

  _getHumidityState() {
    if (this.config.humidity_entity) {
      return this._getEntityState(this.config.humidity_entity);
    }
    // Fall back to VMC internal humidity sensor
    const baseEntityId = this.config.entity.replace('fan.', '');
    return this._getEntityState(`sensor.${baseEntityId}_humidity`);
  }

  // Fan control methods
  async _setFanSpeed(speed) {
    if (!this.hass || !this.config.entity) return;

    try {
      this._loading = true;

      const serviceData = {
        entity_id: this.config.entity,
        percentage: speed * 25 // Convert 0-4 to percentage (0,25,50,75,100)
      };

      await this.hass.callService("fan", "set_percentage", serviceData);

      // Provide haptic feedback on mobile
      if ('vibrate' in navigator) {
        navigator.vibrate(50);
      }

    } catch (error) {
      console.error("Error setting fan speed:", error);
      this._error = `Failed to set fan speed: ${error.message}`;
    } finally {
      this._loading = false;
    }
  }

  // Calculation methods
  _calculateDewPoint(temp, humidity) {
    if (temp == null || humidity == null || humidity <= 0) return null;

    const a = 17.27;
    const b = 237.7;

    const alpha = ((a * temp) / (b + temp)) + Math.log(humidity / 100.0);
    return (b * alpha) / (a - alpha);
  }

  _calculateComfortIndex(temp, humidity) {
    if (temp == null || humidity == null) return null;

    const tempComfort = this._calculateTemperatureComfort(temp);
    const humidityComfort = this._calculateHumidityComfort(humidity);

    return Math.round((tempComfort * 0.6 + humidityComfort * 0.4) * 100);
  }

  _calculateTemperatureComfort(temp) {
    if (temp >= 20 && temp <= 24) return 1.0;
    if (temp >= 18 && temp < 20) return 0.5 + (temp - 18) * 0.25;
    if (temp > 24 && temp <= 26) return 1.0 - (temp - 24) * 0.25;
    if (temp >= 16 && temp < 18) return 0.2 + (temp - 16) * 0.15;
    if (temp > 26 && temp <= 28) return 0.5 - (temp - 26) * 0.15;
    return Math.max(0.0, 0.2 - Math.abs(temp - 22) * 0.02);
  }

  _calculateHumidityComfort(humidity) {
    if (humidity >= 40 && humidity <= 60) return 1.0;
    if (humidity >= 30 && humidity < 40) return 0.5 + (humidity - 30) * 0.05;
    if (humidity > 60 && humidity <= 70) return 1.0 - (humidity - 60) * 0.05;
    if (humidity >= 25 && humidity < 30) return 0.2 + (humidity - 25) * 0.06;
    if (humidity > 70 && humidity <= 80) return 0.5 - (humidity - 70) * 0.03;
    return Math.max(0.0, 0.2 - Math.abs(humidity - 50) * 0.005);
  }

  _calculateAirExchangeTime() {
    const vmcState = this._getVmcState();
    if (!vmcState || vmcState.state === 'off') return null;

    const percentage = parseFloat(vmcState.attributes.percentage || 0);
    const speed = Math.round(percentage / 25); // Convert percentage to speed (0-4)

    const airflowRates = {0: 0, 1: 10, 2: 17, 3: 26, 4: 37}; // m³/h
    const airflow = airflowRates[speed] || 0;

    if (airflow === 0) return null;

    const roomVolume = this.config.room_volume || 60;
    return Math.round((roomVolume / airflow) * 60 * 10) / 10; // minutes
  }

  _getComfortLevel(index) {
    if (index >= 85) return 'excellent';
    if (index >= 70) return 'good';
    if (index >= 55) return 'fair';
    return 'poor';
  }

  _formatSensorValue(value, unit) {
    if (value == null || value === undefined) return '--';

    if (typeof value === 'number') {
      if (unit === '°C' || unit === 'min') return value.toFixed(1);
      if (unit === '%' || unit === 'ppm' || unit === 'ppb') return Math.round(value);
    }

    return value.toString();
  }

  // Render methods
  render() {
    if (this._error) {
      return this._renderError();
    }

    if (this._loading && !this._getVmcState()) {
      return this._renderLoading();
    }

    const vmcState = this._getVmcState();
    if (!vmcState) {
      return this._renderError('VMC device not found. Please check your configuration.');
    }

    return html`
      <div class="card-header">
        <h2 class="card-title">
          <ha-icon
            icon="mdi:air-conditioner"
            class="fan-icon ${vmcState.state === 'on' ? 'spinning' : ''}"
          ></ha-icon>
          ${this.config.name}
        </h2>
        <div class="device-status">
          <div class="status-indicator ${vmcState.state === 'off' ? 'offline' : ''}"></div>
          <span>${vmcState.state === 'on' ? 'Online' : 'Offline'}</span>
        </div>
      </div>

      ${this._renderFanControls()}
      ${this._renderSensors()}
      ${this.config.show_advanced ? this._renderAdvancedSensors() : nothing}
    `;
  }

  _renderError(message = null) {
    return html`
      <div class="error-message">
        <ha-icon icon="mdi:alert-circle"></ha-icon>
        <span>${message || this._error}</span>
      </div>
    `;
  }

  _renderLoading() {
    return html`
      <div class="loading-message">
        <ha-icon icon="mdi:loading" class="spinning"></ha-icon>
        <span>Loading VMC data...</span>
      </div>
    `;
  }

  _renderFanControls() {
    const vmcState = this._getVmcState();
    if (!vmcState) return nothing;

    const currentPercentage = parseFloat(vmcState.attributes.percentage || 0);
    const currentSpeed = Math.round(currentPercentage / 25);

    return html`
      <div class="controls-section">
        <div class="fan-controls">
          ${[0, 1, 2, 3, 4].map(speed => html`
            <button
              class="fan-speed-button ${currentSpeed === speed ? 'active' : ''}"
              @click="${() => this._setFanSpeed(speed)}"
              ?disabled="${this._loading}"
              aria-label="Set fan speed to ${speed}"
            >
              <ha-icon icon="${this._getFanSpeedIcon(speed)}"></ha-icon>
              <span class="speed-label">${speed === 0 ? 'Off' : `Speed ${speed}`}</span>
              <span class="speed-percentage">${speed * 25}%</span>
            </button>
          `)}
        </div>
      </div>
    `;
  }

  _getFanSpeedIcon(speed) {
    const icons = {
      0: 'mdi:fan-off',
      1: 'mdi:fan-speed-1',
      2: 'mdi:fan-speed-2',
      3: 'mdi:fan-speed-3',
      4: 'mdi:fan'
    };
    return icons[speed] || 'mdi:fan';
  }

  _renderSensors() {
    const tempState = this._getTemperatureState();
    const humidityState = this._getHumidityState();
    const vmcState = this._getVmcState();

    const sensors = [];

    if (this.config.show_temperature && tempState) {
      sensors.push({
        label: 'Temperature',
        icon: 'mdi:thermometer',
        value: this._formatSensorValue(tempState.state, '°C'),
        unit: '°C',
        source: this.config.temperature_entity ? 'Custom' : 'VMC'
      });
    }

    if (this.config.show_humidity && humidityState) {
      sensors.push({
        label: 'Humidity',
        icon: 'mdi:water-percent',
        value: this._formatSensorValue(humidityState.state, '%'),
        unit: '%',
        source: this.config.humidity_entity ? 'Custom' : 'VMC'
      });
    }

    if (this.config.show_co2) {
      const co2State = this._getEntityState(`sensor.${this.config.entity.replace('fan.', '')}_co2`);
      if (co2State) {
        sensors.push({
          label: 'CO₂',
          icon: 'mdi:molecule-co2',
          value: this._formatSensorValue(co2State.state, 'ppm'),
          unit: 'ppm',
          source: 'VMC'
        });
      }
    }

    if (this.config.show_voc) {
      const vocState = this._getEntityState(`sensor.${this.config.entity.replace('fan.', '')}_voc`);
      if (vocState) {
        sensors.push({
          label: 'VOC',
          icon: 'mdi:air-filter',
          value: this._formatSensorValue(vocState.state, 'ppb'),
          unit: 'ppb',
          source: 'VMC'
        });
      }
    }

    if (sensors.length === 0) return nothing;

    return html`
      <div class="sensors-grid">
        ${sensors.map(sensor => html`
          <div class="sensor-card">
            <div class="sensor-label">
              <ha-icon icon="${sensor.icon}"></ha-icon>
              <span>${sensor.label}</span>
            </div>
            <div class="sensor-value">
              ${sensor.value}
              <span class="sensor-unit">${sensor.unit}</span>
            </div>
            <div class="sensor-source">Source: ${sensor.source}</div>
          </div>
        `)}
      </div>
    `;
  }

  _renderAdvancedSensors() {
    const tempState = this._getTemperatureState();
    const humidityState = this._getHumidityState();

    if (!tempState || !humidityState) return nothing;

    const temp = parseFloat(tempState.state);
    const humidity = parseFloat(humidityState.state);

    const dewPoint = this._calculateDewPoint(temp, humidity);
    const comfortIndex = this._calculateComfortIndex(temp, humidity);
    const airExchangeTime = this._calculateAirExchangeTime();

    const advancedSensors = [];

    if (this.config.enable_comfort_calculations && dewPoint !== null) {
      advancedSensors.push({
        label: 'Dew Point',
        icon: 'mdi:thermometer-water',
        value: this._formatSensorValue(dewPoint, '°C'),
        unit: '°C'
      });
    }

    if (this.config.enable_comfort_calculations && comfortIndex !== null) {
      const comfortLevel = this._getComfortLevel(comfortIndex);
      advancedSensors.push({
        label: 'Comfort Index',
        icon: 'mdi:account-check',
        value: this._formatSensorValue(comfortIndex, '%'),
        unit: '%',
        comfort: comfortLevel
      });
    }

    if (this.config.enable_air_exchange && airExchangeTime !== null) {
      let category = 'poor';
      if (airExchangeTime <= 20) category = 'excellent';
      else if (airExchangeTime <= 30) category = 'good';
      else if (airExchangeTime <= 60) category = 'fair';

      advancedSensors.push({
        label: 'Air Exchange Time',
        icon: 'mdi:clock-time-four',
        value: this._formatSensorValue(airExchangeTime, 'min'),
        unit: 'min',
        comfort: category
      });
    }

    if (advancedSensors.length === 0) return nothing;

    return html`
      <div class="advanced-section">
        <h3 class="advanced-title">
          <ha-icon icon="mdi:chart-line"></ha-icon>
          Advanced Analytics
        </h3>
        <div class="sensors-grid">
          ${advancedSensors.map(sensor => html`
            <div class="sensor-card">
              <div class="sensor-label">
                <ha-icon icon="${sensor.icon}"></ha-icon>
                <span>${sensor.label}</span>
              </div>
              <div class="sensor-value">
                ${sensor.value}
                <span class="sensor-unit">${sensor.unit}</span>
                ${sensor.comfort ? html`
                  <div class="comfort-indicator comfort-${sensor.comfort}">
                    ${sensor.comfort}
                  </div>
                ` : nothing}
              </div>
            </div>
          `)}
        </div>
      </div>
    `;
  }

  // Home Assistant integration methods
  getCardSize() {
    return 4;
  }

  static getConfigElement() {
    return document.createElement("vmc-helty-card-editor");
  }

  static getStubConfig() {
    return {
      entity: "",
      name: "VMC Helty Flow",
      room_volume: 60,
      show_temperature: true,
      show_humidity: true,
      show_co2: true,
      show_voc: false,
      show_advanced: true,
      enable_comfort_calculations: true,
      enable_air_exchange: true
    };
  }
}

// Register the card
customElements.define('vmc-helty-card', VmcHeltyCard);

// Register with Home Assistant
window.customCards = window.customCards || [];
window.customCards.push({
  type: 'vmc-helty-card',
  name: 'VMC Helty Flow Control Card',
  description: 'Advanced control card for VMC Helty Flow devices with custom sensor support and room volume configuration',
  preview: true,
  documentationURL: 'https://github.com/your-repo/vmc-helty-card',
});

console.info(`%c VMC HELTY CARD v2.0 LitElement %c Loaded successfully!`,
  "color: white; background: green; font-weight: bold;",
  "color: green; font-weight: normal;");

// Dynamically load the editor if available
try {
  // Check if we're in edit mode and need the editor
  if (window.customCards) {
    import('./vmc-helty-card-editor.js').catch(() => {
      console.warn('VMC Helty Card Editor not found - visual editor not available');
    });
  }
} catch (error) {
  console.debug('VMC Helty Card Editor import failed:', error);
}
