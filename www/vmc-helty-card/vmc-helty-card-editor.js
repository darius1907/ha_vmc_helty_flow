/**
 * VMC Helty Flow Control Card Editor v2.1 - LitElement Implementation
 * Visual configuration editor for VMC Helty Flow Control Card
 *
 * ✅ Fully compliant with Home Assistant development guidelines:
 * - LitElement-based architecture for maximum compatibility
 * - Device selection dropdown with auto-discovery
 * - Custom sensor selection for temperature and humidity
 * - Room volume calculator with visual interface
 * - Real-time configuration validation
 * - Accessible form controls with proper labels
 * - Configurable light and timer controls visibility (NEW in v2.1)
 *
 * @version 2.1.0
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
      .section-title {
        font-size: 16px;
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
          state?.attributes?.integration === 'vmc_helty_flow'
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

    // Log di debug: entità VMC trovate
    console.debug('[VMC Editor] VMC trovati:', this._vmcEntities);

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

    // Log di debug: sensori temperatura trovati
    console.debug('[VMC Editor] Sensori temperatura:', this._temperatureSensors);

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

    // Log di debug: sensori umidità trovati
    console.debug('[VMC Editor] Sensori umidità:', this._humiditySensors);
  }

  _getDeviceRoomVolume() {
    if (!this.config.entity || !this.hass) {
      return this.config.room_volume || 60;
    }

    // Try to get room volume from any sensor of the same device
    const deviceEntities = Object.keys(this.hass.states).filter(entityId => 
      entityId.includes('vmc_helty') && 
      this.hass.states[entityId].attributes.device_id === 
      this.hass.states[this.config.entity]?.attributes.device_id
    );

    // Look for room_volume in sensor attributes
    for (const entityId of deviceEntities) {
      const entity = this.hass.states[entityId];
      if (entity.attributes && entity.attributes.room_volume) {
        // Parse room_volume from "75.0 m³" format
        const volumeStr = entity.attributes.room_volume;
        if (typeof volumeStr === 'string') {
          const match = volumeStr.match(/^([\d.]+)/);
          if (match) {
            return parseFloat(match[1]);
          }
        } else if (typeof volumeStr === 'number') {
          return volumeStr;
        }
      }
      
      // Also check for room_volume_m3 attribute
      if (entity.attributes && entity.attributes.room_volume_m3) {
        return parseFloat(entity.attributes.room_volume_m3);
      }
    }

    // Fallback to card config or default
    // NOTE: This value should match DEFAULT_ROOM_VOLUME in Python const.py (60 m³)
    return this.config.room_volume || 60;
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

    // If room_volume changed, sync with device configuration
    if (key === 'room_volume' && this.config.entity && value > 0) {
      this._syncRoomVolumeToDevice(value);
    }
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

    // Sync with device configuration
    if (this.config.entity && volume > 0) {
      this._syncRoomVolumeToDevice(volume);
    }
  }

  async _syncRoomVolumeToDevice(volume) {
    try {
      // Call the update_room_volume service to sync with device configuration
      await this.hass.callService('vmc_helty_flow', 'update_room_volume', {
        entity_id: this.config.entity,
        room_volume: volume
      });

      // Show success notification
      this._showNotification('Room volume updated successfully', 'success');
    } catch (error) {
      console.error('Failed to sync room volume with device:', error);
      // Show error notification
      this._showNotification(
        `Failed to update room volume: ${error.message || 'Unknown error'}`, 
        'error'
      );
    }
  }

  _showNotification(message, type = 'info') {
    // Create a toast notification event
    const event = new CustomEvent('hass-notification', {
      detail: {
        message: message,
        duration: type === 'error' ? 5000 : 3000
      },
      bubbles: true,
      composed: true
    });
    this.dispatchEvent(event);
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
      <ha-card header="Device Selection">
        <ha-icon icon="mdi:air-filter"></ha-icon>
        <ha-settings-row>
          <span slot="heading">VMC Device</span>
          <span slot="description">Select which VMC Helty Flow device this card should control</span>
          <ha-select
            .label=${"Choose VMC Device"}
            .value=${this.config.entity || ""}
            .configValue=${"entity"}
            @selected=${this._valueChanged}
            @closed=${(ev) => ev.stopPropagation()}
            slot="content"
          >
            ${this._vmcEntities.map(entity => html`
              <mwc-list-item .value=${entity.value}>
                ${entity.label}
              </mwc-list-item>
            `)}
          </ha-select>
        </ha-settings-row>
        <ha-settings-row>
          <span slot="heading">Card Name</span>
          <span slot="description">Display name for this card (optional)</span>
          <ha-textfield
            .label=${"Card Name"}
            .value=${this.config.name || ""}
            .configValue=${"name"}
            @input=${this._valueChanged}
            slot="content"
          ></ha-textfield>
        </ha-settings-row>
      </ha-card>
    `;
  }

  _renderSensorSelection() {
    return html`
      <ha-card>
        <div class="section-title">
          <ha-icon icon="mdi:thermometer"></ha-icon>
          Custom Sensor Selection
        </div>
        <ha-settings-row>
          <span slot="heading">Temperature Sensor</span>
          <span slot="description">Select a custom temperature sensor or leave empty to use VMC internal sensor</span>
          <ha-select
            .label=${"Temperature Sensor (Optional)"}
            .value=${this.config.temperature_entity || ""}
            .configValue=${"temperature_entity"}
            @selected=${this._valueChanged}
            @closed=${(ev) => ev.stopPropagation()}
            slot="content"
          >
            ${[html`<mwc-list-item value="">Use VMC Internal Sensor</mwc-list-item>`,
              ...this._temperatureSensors.map(sensor => html`<mwc-list-item value="${sensor.value}">${sensor.label}</mwc-list-item>`)
            ]}
          </ha-select>
        </ha-settings-row>
        ${this._renderSensorPreview(this.config.temperature_entity, this._temperatureSensors, '°C')}
        <ha-settings-row>
          <span slot="heading">Humidity Sensor</span>
          <span slot="description">Select a custom humidity sensor or leave empty to use VMC internal sensor</span>
          <ha-select
            .label=${"Humidity Sensor (Optional)"}
            .value=${this.config.humidity_entity || ""}
            .configValue=${"humidity_entity"}
            @selected=${this._valueChanged}
            @closed=${(ev) => ev.stopPropagation()}
            slot="content"
          >
            ${[html`<mwc-list-item value="">Use VMC Internal Sensor</mwc-list-item>`,
              ...this._humiditySensors.map(sensor => html`<mwc-list-item value="${sensor.value}">${sensor.label}</mwc-list-item>`)
            ]}
          </ha-select>
        </ha-settings-row>
        ${this._renderSensorPreview(this.config.humidity_entity, this._humiditySensors, '%')}
      </ha-card>
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
      <ha-card>
        <div class="section-title">
          <ha-icon icon="mdi:cube-outline"></ha-icon>
          Room Configuration
        </div>
        <ha-settings-row>
          <span slot="heading">
            Room Volume
            ${this.config.entity ? html`
              <ha-icon 
                icon="mdi:sync" 
                style="color: var(--success-color, #4caf50); margin-left: 8px; --mdc-icon-size: 16px;" 
                title="Volume will be synced with device configuration"
              ></ha-icon>
            ` : ''}
          </span>
          <span slot="description">
            Room volume in cubic meters (m³) for accurate air exchange calculations
            ${this.config.entity ? html`
              <br><small style="color: var(--success-color, #4caf50);">
                ✓ Showing current device volume - changes will sync with device configuration
              </small>
            ` : html`
              <br><small style="color: var(--warning-color, #ff9800);">
                ⚠ Select a device above to load current volume and enable sync
              </small>
            `}
          </span>
          <ha-textfield
            id="room_volume"
            .label=${"Room Volume (m³)"}
            .value=${this._getDeviceRoomVolume()}
            .configValue=${"room_volume"}
            type="number"
            min="1"
            max="10000"
            step="0.1"
            @input=${this._valueChanged}
            slot="content"
          ></ha-textfield>
        </ha-settings-row>

        <ha-settings-row>
          <span slot="heading">
            <ha-icon icon="mdi:calculator"></ha-icon>
            Room Volume Calculator
          </span>
          <span slot="description">
            Enter room dimensions to calculate volume
          </span>
          <div slot="content" class="dimensions-grid">
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
        </ha-settings-row>

        <ha-settings-row>
          <span slot="heading">
            <ha-icon icon="mdi:cube"></ha-icon>
            Calculated Volume
          </span>
          <span slot="description">
            Volume calculated from dimensions
          </span>
          <div slot="content" class="calculation-result">
            <span>${calculatedVolume} m³</span>
            <button class="use-calculated-button" @click=${this._useCalculatedVolume}>
              Use Calculated Volume
            </button>
          </div>
        </ha-settings-row>
      </ha-card>
    `;
  }

  _renderDisplayOptions() {
  return html`
      <ha-card header="Display Options">
        <span slot="header">
          <ha-icon icon="mdi:eye"></ha-icon>
        </span>
        <span slot="content">
        ${this._renderDisplaySwitchRow('Show Temperature', 'mdi:thermometer', 'show_temperature', this.config.show_temperature !== false)}
        ${this._renderDisplaySwitchRow('Show Humidity', 'mdi:water-percent', 'show_humidity', this.config.show_humidity !== false)}
        ${this._renderDisplaySwitchRow('Show CO₂', 'mdi:molecule-co2', 'show_co2', this.config.show_co2 !== false)}
        ${this._renderDisplaySwitchRow('Show VOC', 'mdi:air-filter', 'show_voc', this.config.show_voc === true)}
        ${this._renderDisplaySwitchRow('Show Advanced Sensors', 'mdi:chart-line', 'show_advanced', this.config.show_advanced !== false)}
        ${this._renderDisplaySwitchRow('Show Airflow', 'mdi:fan', 'show_airflow', this.config.show_airflow !== false)}
        ${this._renderDisplaySwitchRow('Show Filter Hours', 'mdi:air-filter', 'show_filter_hours', this.config.show_filter_hours !== false)}
        ${this._renderDisplaySwitchRow('Show Device Status', 'mdi:power', 'show_device_status', this.config.show_device_status !== false)}
        ${this._renderDisplaySwitchRow('Show Network Info', 'mdi:ip-network', 'show_network_info', this.config.show_network_info === true)}
        ${this._renderDisplaySwitchRow('Show Lights', 'mdi:lightbulb', 'show_lights', this.config.show_lights !== false)}
        ${this._renderDisplaySwitchRow('Show Timer', 'mdi:timer', 'show_timer', this.config.show_timer !== false)}
        </span>
        <span slot="footer">
          <strong>Show Lights:</strong> Display light controls (only for VMC models with lighting support)<br>
          <strong>Show Timer:</strong> Display light timer controls (only for VMC models with timer support)
        </span>
      </ha-card>
    `;
  }
  _renderDisplaySwitchRow(label, icon, configKey, checked) {
    return html`
      <ha-settings-row>
        <span slot="heading">
          <ha-icon icon="${icon}"></ha-icon>
          ${label}
        </span>
        <span slot="description"></span>
        <ha-switch
          slot="content"
          .checked=${checked}
          .configValue=${configKey}
          @change=${this._valueChanged}
        ></ha-switch>
      </ha-settings-row>
    `;
  }

  _renderAdvancedOptions() {
    return html`
      <ha-card header="Advanced Options">
        <span slot="header">
          <ha-icon icon="mdi:cog"></ha-icon>
        </span>
        <span slot="content">
        ${this._renderDisplaySwitchRow('Enable Comfort Calculations', 'mdi:emoticon-happy', 'enable_comfort_calculations', this.config.enable_comfort_calculations !== false)}
        ${this._renderDisplaySwitchRow('Enable Air Exchange Calculations', 'mdi:autorenew', 'enable_air_exchange', this.config.enable_air_exchange !== false)}
        </span>
        <span slot="footer">
          <strong>Comfort Calculations:</strong> Calculate dew point and comfort index using selected temperature/humidity sensors<br>
          <strong>Air Exchange Calculations:</strong> Calculate air exchange time based on room volume and fan speed
        </span>
      </ha-card>
    `;
  }
}

// Register the editor
customElements.define('vmc-helty-card-editor', VmcHeltyCardEditor);

console.info(`%c VMC HELTY CARD EDITOR v2.1 LitElement %c Loaded successfully! 🛠️`,
  "color: white; background: blue; font-weight: bold;",
  "color: blue; font-weight: normal;");
