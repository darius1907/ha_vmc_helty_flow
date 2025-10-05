/**
 * VMC Helty Advanced Sensors Card Editor v1.0
 * Editor visuale per la configurazione della card sensori avanzati VMC Helty Flow
 *
 * Permette di:
 * - Selezionare l'entità VMC
 * - Modificare il volume stanza
 * - Selezionare sensori esterni di temperatura/umidità
 *
 * @version 1.0.0
 * @author VMC Helty Integration Team
 */

import {
  LitElement,
  html,
  css,
  nothing,
} from "https://unpkg.com/lit@3.1.0/index.js?module";

class VmcHeltyAdvancedSensorsCardEditor extends LitElement {
  static get properties() {
    return {
      hass: { type: Object },
      config: { type: Object },
    };
  }

  constructor() {
    super();
    this.hass = null;
    this.config = {};
  }

  setConfig(config) {
    this.config = config;
    this.requestUpdate();
  }

  _updateConfig(changes) {
    this.config = { ...this.config, ...changes };
    this.dispatchEvent(new CustomEvent('config-changed', { detail: { config: this.config } }));
  }

  _renderEntitySelect() {
    if (!this.hass) return nothing;
    const fanEntities = Object.keys(this.hass.states).filter(eid => eid.startsWith('fan.vmc_helty_'));
    return html`
      <label for="entity">Entità VMC</label>
      <select id="entity" @change="${e => this._updateConfig({ entity: e.target.value })}" .value="${this.config.entity || ''}">
        <option value="">Seleziona...</option>
        ${fanEntities.map(eid => html`<option value="${eid}">${this.hass.states[eid].attributes.friendly_name || eid}</option>`)}
      </select>
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
          <label class="form-label">
            Room Volume
            ${this.config.entity ? html`
              <ha-icon 
                icon="mdi:sync" 
                style="color: var(--success-color, #4caf50); margin-left: 8px; --mdc-icon-size: 16px;" 
                title="Volume will be synced with device configuration"
              ></ha-icon>
            ` : ''}
          </label>
          <div class="form-description">
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
          </div>
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

  _renderRoomVolumeInput() {
    return html`
      <label for="room_volume">Volume stanza (m³)</label>
      <input id="room_volume" type="number" min="1" max="10000" step="0.1" .value="${this.config.room_volume || 60}" @change="${e => this._updateConfig({ room_volume: parseFloat(e.target.value) })}" />
    `;
  }

  _renderSensorSelect(type) {
    if (!this.hass) return nothing;
    const entities = Object.keys(this.hass.states).filter(eid => {
      if (type === "temperature") {
        return eid.startsWith("sensor.") && (this.hass.states[eid].attributes.device_class === "temperature");
      }
      if (type === "humidity") {
        return eid.startsWith("sensor.") && (this.hass.states[eid].attributes.device_class === "humidity");
      }
      return false;
    });
    const selected = this.config[type + '_entity'] || '';
    return html`
      <label for="${type}_entity">Sensore ${type === "temperature" ? "temperatura" : "umidità"}</label>
      <select id="${type}_entity" @change="${e => this._updateConfig({ [type + '_entity']: e.target.value })}" .value="${selected}">
        <option value="">Predefinito VMC</option>
        ${entities.map(eid => html`<option value="${eid}">${this.hass.states[eid].attributes.friendly_name || eid}</option>`)}
      </select>
    `;
  }

  render() {
    return html`
      <div style="display: flex; flex-direction: column; gap: 16px;">
        ${this._renderEntitySelect()}
        ${this._renderRoomVolumeInput()}
        ${this._renderSensorSelect("temperature")}
        ${this._renderSensorSelect("humidity")}
      </div>
    `;
  }

  static get styles() {
    return css`
      label {
        font-weight: 500;
        margin-bottom: 4px;
        display: block;
      }
      select, input {
        width: 100%;
        padding: 6px;
        margin-bottom: 12px;
        border-radius: 4px;
        border: 1px solid #ccc;
        font-size: 1em;
      }
    `;
  }
}

customElements.define('vmc-helty-advanced-sensors-card-editor', VmcHeltyAdvancedSensorsCardEditor);
