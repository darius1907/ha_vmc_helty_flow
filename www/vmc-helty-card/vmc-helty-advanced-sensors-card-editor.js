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
