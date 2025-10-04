/**
 * VMC Helty Advanced Sensors Card v1.0 - LitElement Implementation
 * Card dedicata alla visualizzazione e configurazione dei sensori avanzati VMC Helty Flow
 *
 * - Visualizza tutti i sensori avanzati disponibili
 * - Permette la selezione di sensori esterni di temperatura/umidità
 * - Permette la modifica del volume stanza per i calcoli
 * - Mobile-first, compatibile con Home Assistant
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

function fireEvent(node, type, detail, options) {
  options = options || {};
  detail = detail === null || detail === undefined ? {} : detail;
  const event = new Event(type, {
    bubbles: options.bubbles === undefined ? true : options.bubbles,
    cancelable: Boolean(options.cancelable),
    composed: options.composed === undefined ? true : options.composed,
  });
  event.detail = detail;
  node.dispatchEvent(event);
  return event;
}

class VmcHeltyAdvancedSensorsCard extends LitElement {
  static get properties() {
    return {
      hass: { type: Object },
      config: { type: Object },
      _entityStates: { type: Object, state: true },
      _error: { type: String, state: true },
      _roomVolume: { type: Number, state: true },
      _temperatureEntity: { type: String, state: true },
      _humidityEntity: { type: String, state: true },
    };
  }

  constructor() {
    super();
    this.config = {};
    this.hass = null;
    this._entityStates = {};
    this._error = null;
    this._roomVolume = 60;
    this._temperatureEntity = null;
    this._humidityEntity = null;
  }

  setConfig(config) {
    this.config = config;
    this._roomVolume = config.room_volume || 60;
    this._temperatureEntity = config.temperature_entity || null;
    this._humidityEntity = config.humidity_entity || null;
    this.requestUpdate();
  }

  _getEntityState(entityId) {
    if (!this.hass || !entityId) return null;
    return this.hass.states[entityId] || null;
  }

  _getBaseEntityId() {
    if (!this.config.entity) return null;
    return this.config.entity.replace('fan.', '');
  }

  _handleRoomVolumeChange(e) {
    const value = parseFloat(e.target.value);
    if (!isNaN(value) && value >= 1 && value <= 10000) {
      this._roomVolume = Math.round(value * 10) / 10;
      fireEvent(this, "config-changed", { room_volume: this._roomVolume });
    }
  }

  _handleSensorSelect(e, type) {
    const entityId = e.target.value;
    if (type === "temperature") {
      this._temperatureEntity = entityId;
      fireEvent(this, "config-changed", { temperature_entity: entityId });
    } else if (type === "humidity") {
      this._humidityEntity = entityId;
      fireEvent(this, "config-changed", { humidity_entity: entityId });
    }
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
    const selected = type === "temperature" ? this._temperatureEntity : this._humidityEntity;
    return html`
      <ha-settings-row>
        <span slot="heading">
          <ha-heading-badge type="text">
            <ha-icon slot="icon" icon="${type === "temperature" ? "mdi:thermometer" : "mdi:water-percent"}"></ha-icon>
            Seleziona sensore ${type === "temperature" ? "temperatura" : "umidità"}
          </ha-heading-badge>
        </span>
        <select @change="${e => this._handleSensorSelect(e, type)}" .value="${selected || ''}">
          <option value="">Predefinito VMC</option>
          ${entities.map(eid => html`<option value="${eid}">${this.hass.states[eid].attributes.friendly_name || eid}</option>`)}
        </select>
      </ha-settings-row>
    `;
  }

  _renderRoomVolumeInput() {
    return html`
      <ha-settings-row>
        <span slot="heading">
          <ha-heading-badge type="text">
            <ha-icon slot="icon" icon="mdi:ruler-square"></ha-icon>
            Volume stanza (m³)
          </ha-heading-badge>
        </span>
        <input type="number" min="1" max="10000" step="0.1" .value="${this._roomVolume}" @change="${e => this._handleRoomVolumeChange(e)}" />
      </ha-settings-row>
    `;
  }

  _renderAdvancedSensors() {
    const baseEntityId = this._getBaseEntityId();
    if (!baseEntityId) return nothing;
    const advEntities = [
      `sensor.${baseEntityId}_absolute_humidity`,
      `sensor.${baseEntityId}_dew_point`,
      `sensor.${baseEntityId}_dew_point_delta`,
      `sensor.${baseEntityId}_comfort_index`,
      `sensor.${baseEntityId}_air_exchange_time`,
      `sensor.${baseEntityId}_daily_air_changes`,
      `sensor.${baseEntityId}_last_response`,
      `sensor.${baseEntityId}_ip_address`,
    ];
    return html`
      <ha-heading-badge type="text">
        <ha-icon slot="icon" icon="mdi:chart-line"></ha-icon>
        Sensori Avanzati
      </ha-heading-badge>
      <div style="display: flex; flex-direction: column; gap: 8px;">
        ${advEntities.map(entityId => {
          const stateObj = this._getEntityState(entityId);
          if (!stateObj) return html`<div>Entità non trovata: ${entityId}</div>`;
          const name = stateObj.attributes.friendly_name || entityId;
          const value = stateObj.state;
          const unit = stateObj.attributes.unit_of_measurement || "";
          const icon = stateObj.attributes.icon || `mdi:${entityId.includes('dew_point') ? 'water' : entityId.includes('comfort_index') ? 'emoticon-happy' : entityId.includes('air_exchange_time') ? 'autorenew' : entityId.includes('absolute_humidity') ? 'water-percent' : 'gauge'}`;
          return html`
            <div class="entity-row" style="display: flex; align-items: center; gap: 12px; padding: 4px 0;">
              <ha-icon icon="${icon}" style="color: var(--state-icon-color);"></ha-icon>
              <div style="flex: 1;">
                <div style="font-weight: 500;">${name}</div>
                <div style="color: var(--secondary-text-color); font-size: 1.1em;">${value} ${unit}</div>
              </div>
            </div>
          `;
        })}
      </div>
    `;
  }

  render() {
    if (this._error) {
      return html`<div class="error-message"><ha-icon icon="mdi:alert-circle"></ha-icon><span>${this._error}</span></div>`;
    }
    return html`
      <ha-card>
        <ha-heading-badge type="text">
          <ha-icon slot="icon" icon="mdi:chart-line"></ha-icon>
          Sensori Avanzati VMC Helty
        </ha-heading-badge>
        ${this._renderRoomVolumeInput()}
        ${this._renderSensorSelect("temperature")}
        ${this._renderSensorSelect("humidity")}
        ${this._renderAdvancedSensors()}
      </ha-card>
    `;
  }

  static getConfigElement() {
    return document.createElement("vmc-helty-advanced-sensors-card-editor");
  }

  static getStubConfig() {
    return {
      entity: "",
      room_volume: 60,
      temperature_entity: "",
      humidity_entity: "",
    };
  }
}

customElements.define('vmc-helty-advanced-sensors-card', VmcHeltyAdvancedSensorsCard);

window.customCards = window.customCards || [];
window.customCards.push({
  type: 'vmc-helty-advanced-sensors-card',
  name: 'VMC Helty Advanced Sensors Card',
  description: 'Card dedicata ai sensori avanzati e configurazione stanza per VMC Helty Flow',
  preview: true,
  documentationURL: 'https://github.com/your-repo/vmc-helty-card',
});
