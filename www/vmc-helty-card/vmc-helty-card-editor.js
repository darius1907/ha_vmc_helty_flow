/**
 * VMC Helty Flow Control Card Editor v2.0 - LitElement Implementation
 * Visual configuration editor for VMC Helty Flow Control Card
 *
 * ✅ Fully compliant with Home Assistant development guidelines:
 * - LitElement-based architecture for maximum compatibility
 * - Device selection dropdown with auto-discovery
 * - Custom sensor selection for temperature and humidity
 * - Room volume calculator with visual interface
 * - Real-time configuration validation
 * - Accessible form controls with proper labels
 *
 * @version 2.0.0
 * @author VMC Helty Integration Team
 */

import {
  LitElement,
  html,
  css,
  nothing,
} from "https://unpkg.com/lit@3.1.0/index.js?module";

class VmcHeltyCardEditor extends LitElement {
  static get properties() {
    return {
      hass: { type: Object },
      config: { type: Object },
      _vmcEntities: { type: Array, state: true },
      _temperatureSensors: { type: Array, state: true },
      _humiditySensors: { type: Array, state: true },
      _roomDimensions: { type: Object, state: true },
    };
  }

  constructor() {
    super();
    this.config = {};
    this.hass = null;
    this._vmcEntities = [];
    this._temperatureSensors = [];
    this._humiditySensors = [];
    this._roomDimensions = { length: 6, width: 5, height: 2.4 };
  }

  static get styles() {
    return css`
      :host {
        display: block;
        padding: 16px;
        background: var(--card-background-color);
        border-radius: var(--ha-card-border-radius, 8px);
        font-family: var(--ha-card-font-family, inherit);
      }

      .config-section {
        margin-bottom: 24px;
        padding-bottom: 16px;
        border-bottom: 1px solid var(--divider-color);
      }

      .config-section:last-child {
        border-bottom: none;
        margin-bottom: 0;
      }

      .section-title {
        font-size: 16px;
        font-weight: 500;
        color: var(--primary-text-color);
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
      }

      .form-group {
        margin-bottom: 16px;
      }

      .form-label {
        display: block;
        font-size: 14px;
        font-weight: 500;
        color: var(--primary-text-color);
        margin-bottom: 8px;
      }

      .form-description {
        font-size: 12px;
        color: var(--secondary-text-color);
        margin-bottom: 8px;
        line-height: 1.4;
      }

      ha-textfield,
      ha-select,
      ha-switch {
        width: 100%;
        --mdc-theme-primary: var(--accent-color);
      }

      ha-textfield {
        --mdc-text-field-fill-color: var(--secondary-background-color);
      }

      .room-calculator {
        background: var(--secondary-background-color);
        border-radius: var(--ha-card-border-radius, 8px);
        padding: 16px;
        margin-top: 8px;
      }

      .calculator-title {
        font-size: 14px;
        font-weight: 500;
        color: var(--primary-text-color);
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
      }

      .dimensions-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 12px;
        margin-bottom: 12px;
      }

      .calculation-result {
        background: var(--accent-color);
        color: var(--text-primary-color);
        padding: 12px;
        border-radius: var(--ha-card-border-radius, 8px);
        text-align: center;
        font-weight: 500;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
      }

      .use-calculated-button {
        background: var(--primary-color);
        color: var(--text-primary-color);
        border: none;
        border-radius: var(--ha-card-border-radius, 8px);
        padding: 8px 16px;
        font-size: 14px;
        font-weight: 500;
        cursor: pointer;
        margin-top: 8px;
        width: 100%;
        transition: all 0.2s ease;
      }

      .use-calculated-button:hover {
        opacity: 0.8;
      }

      .sensor-preview {
        background: var(--secondary-background-color);
        border: 1px solid var(--divider-color);
        border-radius: var(--ha-card-border-radius, 8px);
        padding: 8px 12px;
        margin-top: 8px;
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 12px;
      }

      .sensor-preview.available {
        border-color: var(--success-color);
        background: var(--success-color-alpha, rgba(76, 175, 80, 0.1));
      }

      .sensor-preview.unavailable {
        border-color: var(--error-color);
        background: var(--error-color-alpha, rgba(244, 67, 54, 0.1));
      }

      .current-value {
        color: var(--accent-color);
        font-weight: 500;
      }

      .toggle-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 12px;
      }

      .toggle-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 8px;
        background: var(--secondary-background-color);
        border-radius: var(--ha-card-border-radius, 8px);
      }

      .toggle-label {
        font-size: 14px;
        color: var(--primary-text-color);
      }

      .error-message {
        background: var(--error-color-alpha, rgba(244, 67, 54, 0.1));
        color: var(--error-color);
        padding: 12px;
        border-radius: var(--ha-card-border-radius, 8px);
        border: 1px solid var(--error-color);
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 14px;
      }

      ha-icon {
        --mdc-icon-size: 20px;
      }

      /* Responsive */
      @media (max-width: 768px) {
        .dimensions-grid {
          grid-template-columns: 1fr;
        }

        .toggle-grid {
          grid-template-columns: 1fr;
        }
      }
    `;
  }

  setConfig(config) {
    this.config = { ...config };
    this._discoverEntities();
  }

  willUpdate(changedProps) {
    super.willUpdate(changedProps);

    if (changedProps.has('hass') && this.hass) {
      this._discoverEntities();
    }
  }

  _discoverEntities() {
    if (!this.hass) return;

    // Discover VMC entities - look for all fan entities first, then filter by integration
    this._vmcEntities = Object.keys(this.hass.states)
      .filter(entityId => {
        if (!entityId.startsWith('fan.')) return false;
        
        const state = this.hass.states[entityId];
        // Check if it's from our VMC Helty integration by looking at attributes
        return (
          entityId.startsWith('fan.vmc_helty_') || // Prioritize new vmc_{name} prefix
          entityId.includes('vmc_helty') ||
          entityId.includes('helty') ||
          state?.attributes?.integration === 'vmc_helty_flow' ||
          state?.entity_id?.includes('_fan')
        );
      })
      .map(entityId => ({
        value: entityId,
        label: this.hass.states[entityId]?.attributes?.friendly_name || entityId
      }));

    // If no VMC-specific entities found, show all fan entities as fallback
    if (this._vmcEntities.length === 0) {
      this._vmcEntities = Object.keys(this.hass.states)
        .filter(entityId => entityId.startsWith('fan.'))
        .map(entityId => ({
          value: entityId,
          label: this.hass.states[entityId]?.attributes?.friendly_name || entityId
        }));
    }

    // Discover temperature sensors
    this._temperatureSensors = Object.keys(this.hass.states)
      .filter(entityId => {
        const state = this.hass.states[entityId];
        return entityId.startsWith('sensor.') && (
          state.attributes.device_class === 'temperature' ||
          state.attributes.unit_of_measurement === '°C'
        );
      })
      .map(entityId => ({
        value: entityId,
        label: this.hass.states[entityId]?.attributes?.friendly_name || entityId,
        currentValue: this.hass.states[entityId]?.state,
        available: this.hass.states[entityId]?.state !== 'unavailable'
      }));

    // Discover humidity sensors
    this._humiditySensors = Object.keys(this.hass.states)
      .filter(entityId => {
        const state = this.hass.states[entityId];
        return entityId.startsWith('sensor.') && (
          state.attributes.device_class === 'humidity' ||
          state.attributes.unit_of_measurement === '%'
        );
      })
      .map(entityId => ({
        value: entityId,
        label: this.hass.states[entityId]?.attributes?.friendly_name || entityId,
        currentValue: this.hass.states[entityId]?.state,
        available: this.hass.states[entityId]?.state !== 'unavailable'
      }));
  }

  _valueChanged(ev) {
    const target = ev.target;
    const key = target.configValue;

    if (!key) return;

    let value = target.value;

    // Handle different input types
    if (target.type === 'checkbox' || target.tagName === 'HA-SWITCH') {
      value = target.checked;
    } else if (target.type === 'number') {
      value = parseFloat(value);
    }

    // Update config
    const newConfig = { ...this.config, [key]: value };
    this.config = newConfig;

    // Fire config change event
    this._fireConfigChanged();
  }

  _fireConfigChanged() {
    const event = new CustomEvent('config-changed', {
      detail: { config: this.config },
      bubbles: true,
      composed: true,
    });
    this.dispatchEvent(event);
  }

  _calculateRoomVolume() {
    const { length, width, height } = this._roomDimensions;
    return Math.round(length * width * height * 10) / 10; // Round to 1 decimal
  }

  _updateDimension(dimension, value) {
    this._roomDimensions = {
      ...this._roomDimensions,
      [dimension]: parseFloat(value) || 0
    };
  }

  _useCalculatedVolume() {
    const volume = this._calculateRoomVolume();
    const newConfig = { ...this.config, room_volume: volume };
    this.config = newConfig;
    this._fireConfigChanged();

    // Update the textfield value
    const volumeField = this.shadowRoot.querySelector('#room_volume');
    if (volumeField) {
      volumeField.value = volume;
    }
  }

  render() {
    if (!this.hass) {
      return html`
        <div class="error-message">
          <ha-icon icon="mdi:loading"></ha-icon>
          <span>Loading Home Assistant data...</span>
        </div>
      `;
    }

    return html`
      ${this._renderDeviceSelection()}
      ${this._renderSensorSelection()}
      ${this._renderRoomConfiguration()}
      ${this._renderDisplayOptions()}
      ${this._renderAdvancedOptions()}
    `;
  }

  _renderDeviceSelection() {
    if (this._vmcEntities.length === 0) {
      return html`
        <div class="error-message">
          <ha-icon icon="mdi:alert-circle"></ha-icon>
          <span>No fan entities found. Please ensure your VMC Helty Flow integration is running and has created the fan entities.</span>
        </div>
      `;
    }

    return html`
      <div class="config-section">
        <div class="section-title">
          <ha-icon icon="mdi:air-conditioner"></ha-icon>
          Device Selection
        </div>

        <div class="form-group">
          <label class="form-label">VMC Device</label>
          <div class="form-description">
            Select which VMC Helty Flow device this card should control
          </div>
          <ha-select
            .label=${"Choose VMC Device"}
            .value=${this.config.entity || ""}
            .configValue=${"entity"}
            @selected=${this._valueChanged}
            @closed=${(ev) => ev.stopPropagation()}
          >
            ${this._vmcEntities.map(entity => html`
              <mwc-list-item .value=${entity.value}>
                ${entity.label}
              </mwc-list-item>
            `)}
          </ha-select>
        </div>

        <div class="form-group">
          <label class="form-label">Card Name</label>
          <div class="form-description">
            Display name for this card (optional)
          </div>
          <ha-textfield
            .label=${"Card Name"}
            .value=${this.config.name || ""}
            .configValue=${"name"}
            @input=${this._valueChanged}
          ></ha-textfield>
        </div>
      </div>
    `;
  }

  _renderSensorSelection() {
    return html`
      <div class="config-section">
        <div class="section-title">
          <ha-icon icon="mdi:thermometer"></ha-icon>
          Custom Sensor Selection
        </div>

        <div class="form-group">
          <label class="form-label">Temperature Sensor</label>
          <div class="form-description">
            Select a custom temperature sensor or leave empty to use VMC internal sensor
          </div>
          <ha-select
            .label=${"Temperature Sensor (Optional)"}
            .value=${this.config.temperature_entity || ""}
            .configValue=${"temperature_entity"}
            @selected=${this._valueChanged}
            @closed=${(ev) => ev.stopPropagation()}
          >
            <mwc-list-item value="">Use VMC Internal Sensor</mwc-list-item>
            ${this._temperatureSensors.map(sensor => html`
              <mwc-list-item .value=${sensor.value}>
                ${sensor.label}
              </mwc-list-item>
            `)}
          </ha-select>
          ${this._renderSensorPreview(this.config.temperature_entity, this._temperatureSensors, '°C')}
        </div>

        <div class="form-group">
          <label class="form-label">Humidity Sensor</label>
          <div class="form-description">
            Select a custom humidity sensor or leave empty to use VMC internal sensor
          </div>
          <ha-select
            .label=${"Humidity Sensor (Optional)"}
            .value=${this.config.humidity_entity || ""}
            .configValue=${"humidity_entity"}
            @selected=${this._valueChanged}
            @closed=${(ev) => ev.stopPropagation()}
          >
            <mwc-list-item value="">Use VMC Internal Sensor</mwc-list-item>
            ${this._humiditySensors.map(sensor => html`
              <mwc-list-item .value=${sensor.value}>
                ${sensor.label}
              </mwc-list-item>
            `)}
          </ha-select>
          ${this._renderSensorPreview(this.config.humidity_entity, this._humiditySensors, '%')}
        </div>
      </div>
    `;
  }

  _renderSensorPreview(entityId, sensors, unit) {
    if (!entityId) return nothing;

    const sensor = sensors.find(s => s.value === entityId);
    if (!sensor) return nothing;

    return html`
      <div class="sensor-preview ${sensor.available ? 'available' : 'unavailable'}">
        <ha-icon icon="${sensor.available ? 'mdi:check-circle' : 'mdi:alert-circle'}"></ha-icon>
        <span>Current value: <span class="current-value">${sensor.currentValue}${unit}</span></span>
      </div>
    `;
  }

  _renderRoomConfiguration() {
    const calculatedVolume = this._calculateRoomVolume();

    return html`
      <div class="config-section">
        <div class="section-title">
          <ha-icon icon="mdi:cube-outline"></ha-icon>
          Room Configuration
        </div>

        <div class="form-group">
          <label class="form-label">Room Volume</label>
          <div class="form-description">
            Room volume in cubic meters (m³) for accurate air exchange calculations
          </div>
          <ha-textfield
            id="room_volume"
            .label=${"Room Volume (m³)"}
            .value=${this.config.room_volume || 60}
            .configValue=${"room_volume"}
            type="number"
            min="1"
            max="10000"
            step="0.1"
            @input=${this._valueChanged}
          ></ha-textfield>
        </div>

        <div class="room-calculator">
          <div class="calculator-title">
            <ha-icon icon="mdi:calculator"></ha-icon>
            Room Volume Calculator
          </div>

          <div class="dimensions-grid">
            <ha-textfield
              .label=${"Length (m)"}
              .value=${this._roomDimensions.length}
              type="number"
              min="0.1"
              step="0.1"
              @input=${(ev) => this._updateDimension('length', ev.target.value)}
            ></ha-textfield>

            <ha-textfield
              .label=${"Width (m)"}
              .value=${this._roomDimensions.width}
              type="number"
              min="0.1"
              step="0.1"
              @input=${(ev) => this._updateDimension('width', ev.target.value)}
            ></ha-textfield>

            <ha-textfield
              .label=${"Height (m)"}
              .value=${this._roomDimensions.height}
              type="number"
              min="0.1"
              step="0.1"
              @input=${(ev) => this._updateDimension('height', ev.target.value)}
            ></ha-textfield>
          </div>

          <div class="calculation-result">
            <ha-icon icon="mdi:cube"></ha-icon>
            <span>Calculated Volume: ${calculatedVolume} m³</span>
          </div>

          <button class="use-calculated-button" @click=${this._useCalculatedVolume}>
            Use Calculated Volume
          </button>
        </div>
      </div>
    `;
  }

  _renderDisplayOptions() {
    return html`
      <div class="config-section">
        <div class="section-title">
          <ha-icon icon="mdi:eye"></ha-icon>
          Display Options
        </div>

        <div class="toggle-grid">
          <div class="toggle-item">
            <span class="toggle-label">Show Temperature</span>
            <ha-switch
              .checked=${this.config.show_temperature !== false}
              .configValue=${"show_temperature"}
              @change=${this._valueChanged}
            ></ha-switch>
          </div>

          <div class="toggle-item">
            <span class="toggle-label">Show Humidity</span>
            <ha-switch
              .checked=${this.config.show_humidity !== false}
              .configValue=${"show_humidity"}
              @change=${this._valueChanged}
            ></ha-switch>
          </div>

          <div class="toggle-item">
            <span class="toggle-label">Show CO₂</span>
            <ha-switch
              .checked=${this.config.show_co2 !== false}
              .configValue=${"show_co2"}
              @change=${this._valueChanged}
            ></ha-switch>
          </div>

          <div class="toggle-item">
            <span class="toggle-label">Show VOC</span>
            <ha-switch
              .checked=${this.config.show_voc === true}
              .configValue=${"show_voc"}
              @change=${this._valueChanged}
            ></ha-switch>
          </div>

          <div class="toggle-item">
            <span class="toggle-label">Show Advanced Sensors</span>
            <ha-switch
              .checked=${this.config.show_advanced !== false}
              .configValue=${"show_advanced"}
              @change=${this._valueChanged}
            ></ha-switch>
          </div>

          <div class="toggle-item">
            <span class="toggle-label">Show Airflow</span>
            <ha-switch
              .checked=${this.config.show_airflow !== false}
              .configValue=${"show_airflow"}
              @change=${this._valueChanged}
            ></ha-switch>
          </div>

          <div class="toggle-item">
            <span class="toggle-label">Show Filter Hours</span>
            <ha-switch
              .checked=${this.config.show_filter_hours !== false}
              .configValue=${"show_filter_hours"}
              @change=${this._valueChanged}
            ></ha-switch>
          </div>

          <div class="toggle-item">
            <span class="toggle-label">Show Device Status</span>
            <ha-switch
              .checked=${this.config.show_device_status !== false}
              .configValue=${"show_device_status"}
              @change=${this._valueChanged}
            ></ha-switch>
          </div>

          <div class="toggle-item">
            <span class="toggle-label">Show Network Info</span>
            <ha-switch
              .checked=${this.config.show_network_info === true}
              .configValue=${"show_network_info"}
              @change=${this._valueChanged}
            ></ha-switch>
          </div>
        </div>
      </div>
    `;
  }

  _renderAdvancedOptions() {
    return html`
      <div class="config-section">
        <div class="section-title">
          <ha-icon icon="mdi:cog"></ha-icon>
          Advanced Features
        </div>

        <div class="toggle-grid">
          <div class="toggle-item">
            <span class="toggle-label">Enable Comfort Calculations</span>
            <ha-switch
              .checked=${this.config.enable_comfort_calculations !== false}
              .configValue=${"enable_comfort_calculations"}
              @change=${this._valueChanged}
            ></ha-switch>
          </div>

          <div class="toggle-item">
            <span class="toggle-label">Enable Air Exchange Calculations</span>
            <ha-switch
              .checked=${this.config.enable_air_exchange !== false}
              .configValue=${"enable_air_exchange"}
              @change=${this._valueChanged}
            ></ha-switch>
          </div>
        </div>

        <div class="form-description" style="margin-top: 12px;">
          <strong>Comfort Calculations:</strong> Calculate dew point and comfort index using selected temperature/humidity sensors<br>
          <strong>Air Exchange Calculations:</strong> Calculate air exchange time based on room volume and fan speed
        </div>
      </div>
    `;
  }
}

// Register the editor
customElements.define('vmc-helty-card-editor', VmcHeltyCardEditor);

console.info(`%c VMC HELTY CARD EDITOR v2.0 LitElement %c Loaded successfully! 🛠️`,
  "color: white; background: blue; font-weight: bold;",
  "color: blue; font-weight: normal;");
