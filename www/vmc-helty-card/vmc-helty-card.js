/**
 * VMC Helty Flow Control Card v2.1 - LitElement Implementation
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
 * - Configurable light and timer controls visibility (NEW in v2.1)
 *
 * @version 2.1.0
 * @author VMC Helty Integration Team
 */

console.info(
  `%c VMC HELTY CARD v2.1 LitElement %c Advanced VMC Helty Flow control with configurable light/timer controls`,
  "color: orange; font-weight: bold; background: black",
  "color: white; font-weight: normal;"
);

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

// VMC Helty Flow Control Card - LitElement Implementation
class VmcHeltyCard extends LitElement {
  _renderModeControls() {
    const deviceSlug = this._getDeviceSlug();
    const vmcState = this._getVmcState();
    if (!deviceSlug) return nothing;

    // Modalità speciali: stato letto dagli attributi della fan
    const fanState = this._getVmcState();
    const attrs = (fanState && fanState.attributes) || {};

    // Mappa modalità speciali: chiave, label, icona, attributo, valore fan speed
    const specialModes = [
      {
        key: 'hyperventilation',
        label: 'Iperventilazione',
        icon: 'mdi:fan-plus',
        attr: 'hyperventilation',
        speed: 6
      },
      {
        key: 'night_mode',
        label: 'Modalità Notte',
        icon: 'mdi:weather-night',
        attr: 'night_mode',
        speed: 5
      },
      {
        key: 'free_cooling',
        label: 'Free Cooling',
        icon: 'mdi:snowflake',
        attr: 'free_cooling',
        speed: 7
      }
    ];

    // Switch reali
    const panelLedEntity = `switch.vmc_helty_${deviceSlug}_panel_led`;
    const sensorsEntity = `switch.vmc_helty_${deviceSlug}_sensors`;
    const panelLedState = this._getEntityState(panelLedEntity);
    const sensorsState = this._getEntityState(sensorsEntity);
    console.debug('Panel LED state:', panelLedState);
    console.debug('Panel LED state.state:', panelLedState.state);
    console.debug('Sensors state:', sensorsState);
    console.debug('Sensors state.state:', sensorsState.state);
    console.debug('_loading:', this._loading );
    console.debug('vmcState state:', vmcState && vmcState.state === 'off');
    console.debug('hass:', this.hass);

    return html`
      <div class="controls-section">
        <div class="section-title">
          <ha-icon icon="mdi:cog"></ha-icon>
          <span>Modalità Speciali</span>
        </div>
        <ha-chip-set>
          ${specialModes.map(mode => {
            const isOn = !!attrs[mode.attr];
            return html`
              <ha-chip
                .selected=${isOn}
                @click=${() => this._setSpecialMode(mode)}
                aria-label="${mode.label}"
                ?disabled=${this._loading || (vmcState && vmcState.state === 'off')}
              >
                <ha-icon icon="${mode.icon}" slot="icon"></ha-icon>
                ${mode.label}
              </ha-chip>
            `;
          })}
        </ha-chip-set>
      </div>
      <div class="controls-section">
        <div class="section-title">
          <ha-icon icon="mdi:toggle-switch"></ha-icon>
          <span>Controlli Dispositivo</span>
        </div>
        <ha-settings-row>
          <span slot="heading">LED Pannello</span>
          <span slot="description">Controllo LED del pannello frontale ${panelLedState ? `(${panelLedState.state})` : '(non trovato)'}</span>
          <div slot="content">
            <mwc-switch
              .checked=${panelLedState && panelLedState.state === 'on'}
              @change=${(e) => this._toggleSwitch(panelLedEntity)}
              ?disabled=${this._loading || !panelLedState || panelLedState.state === 'unavailable'}
              style="border: 2px solid red; background: yellow;"
            ></mwc-switch>
          </div>
        </ha-settings-row>
        <ha-settings-row>
          <span slot="heading">Sensori</span>
          <span slot="description">Attivazione sensori ambientali ${sensorsState ? `(${sensorsState.state})` : '(non trovato)'}</span>
          <div slot="content">
            <mwc-switch
              .checked=${sensorsState && sensorsState.state === 'on'}
              @change=${(e) => this._toggleSwitch(sensorsEntity)}
              @click=${(e) => this._toggleSwitch(sensorsEntity)}
              ?disabled=${this._loading || (vmcState && vmcState.state === 'off') || !sensorsState || sensorsState.state === 'unavailable'}
              style="border: 2px solid red; background: yellow;"
            ></mwc-switch>
          </div>
        </ha-settings-row>
      </div>
    `;
  }

  /** Imposta la modalità speciale inviando la fan speed corrispondente */
  async _setSpecialMode(mode) {
    if (!this.hass || !this.config.entity) return;
    try {
      this._loading = true;
      await this.hass.callService("fan", "set_percentage", {
        entity_id: this.config.entity,
        // La fan speed speciale va da 5 a 7, la percentuale non è usata realmente ma Home Assistant la mappa
        percentage: mode.speed * 25,
      });
      fireEvent(this, "hass-notification", {
        message: `Modalità impostata: ${mode.label}`,
      });
      if ("vibrate" in navigator) navigator.vibrate(40);
    } catch (e) {
      fireEvent(this, "hass-notification", {
        message: `Errore: ${e.message}`,
      });
    } finally {
      this._loading = false;
    }
  }
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
      :host {
        display: block;
      }
      .controls-section {
        margin-bottom: 20px;
      }
      .section-title {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 12px;
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--primary-text-color);
        letter-spacing: 0.01em;
      }
      .fan-icon.spinning {
        animation: spin 2s linear infinite;
      }
      @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
      }
      .speed-status {
        margin-top: 4px;
        font-size: 1rem;
        font-weight: 500;
        color: var(--primary-color);
        text-align: left;
      }
      .sensor-card {
        border: 1px solid var(--divider-color, #e0e0e0);
        border-radius: var(--ha-card-border-radius, 8px);
        padding: 8px;
        display: flex;
        flex-direction: column;
        gap: 4px;
      }
      .comfort-excellent { color: var(--success-color, green); }
      .comfort-good { color: var(--primary-color, #03a9f4); }
      .comfort-fair { color: var(--warning-color, orange); }
      .comfort-poor { color: var(--error-color, red); }
      .advanced-toggle {
        display: flex;
        align-items: center;
        justify-content: space-between;
        cursor: pointer;
        padding: 8px 0;
      }
      .gauges-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(160px,1fr));
        gap: 16px;
      }
      .switch-control {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 12px 0;
        border-bottom: 1px solid var(--divider-color, #e0e0e0);
      }
      .switch-info {
        display: flex;
        flex-direction: column;
        gap: 4px;
      }
      .switch-heading {
        font-weight: 600;
        color: var(--primary-text-color);
      }
      .switch-description {
        font-size: 0.9rem;
        color: var(--secondary-text-color);
      }
    `;
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
      return 60; // Default room volume - should match DEFAULT_ROOM_VOLUME in Python const.py
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

  _getDeviceSlug() {
    if (!this.config.entity) return null;

    // Extract device slug from fan entity ID
    // Convert from "fan.vmc_<device_name_slug>" to "<device_name_slug>"
    const match = this.config.entity.match(/^fan\.vmc_helty_(.+)$/);
    return match ? match[1] : null;
  }

  // Fan control methods
  async _setFanSpeed(speed) {
    if (!this.hass || !this.config.entity) return;

    try {
      this._loading = true;
      try {
        await this.hass.callService("fan", "set_percentage", {
          entity_id: this.config.entity,
          percentage: speed * 25,
        });
        fireEvent(this, "hass-notification", {
          message: `Velocità impostata: ${speed * 25}%`,
        });
        // Evidenzia temporaneamente il chip attivo
        this._lastSpeedSet = speed;
        setTimeout(() => { this._lastSpeedSet = null; this.requestUpdate(); }, 800);
        if ("vibrate" in navigator) navigator.vibrate(40);
      } catch (e) {
        fireEvent(this, "hass-notification", {
          message: `Errore: ${e.message}`,
        });
      } finally {
        this._loading = false;
      }
    } finally {
      this._loading = false;
    }
  }

  async _toggleSwitch(entityId) {
    if (!this.hass || !entityId) return;

    try {
      this._loading = true;

      const state = this._getEntityState(entityId);
      const service = state && state.state === 'on' ? 'turn_off' : 'turn_on';

      await this.hass.callService("switch", service, {
        entity_id: entityId
      });

      // Provide haptic feedback on mobile
      if ('vibrate' in navigator) {
        navigator.vibrate(50);
      }

    } catch (error) {
      console.error("Error toggling switch:", error);
      this._error = `Failed to toggle switch: ${error.message}`;
    } finally {
      this._loading = false;
    }
  }

  async _toggleLight(entityId) {
    if (!this.hass || !entityId) return;

    try {
      this._loading = true;

      const state = this._getEntityState(entityId);
      const service = state && state.state === 'on' ? 'turn_off' : 'turn_on';

      await this.hass.callService("light", service, {
        entity_id: entityId
      });

      // Provide haptic feedback on mobile
      if ('vibrate' in navigator) {
        navigator.vibrate(50);
      }

    } catch (error) {
      console.error("Error toggling light:", error);
      this._error = `Failed to toggle light: ${error.message}`;
    } finally {
      this._loading = false;
    }
  }

  async _setLightBrightness(entityId, brightness) {
    if (!this.hass || !entityId) return;

    try {
      this._loading = true;

      const brightnessValue = Math.round((brightness / 100) * 255); // Convert 0-100 to 0-255

      await this.hass.callService("light", "turn_on", {
        entity_id: entityId,
        brightness: brightnessValue
      });

      // Provide haptic feedback on mobile
      if ('vibrate' in navigator) {
        navigator.vibrate(50);
      }

    } catch (error) {
      console.error("Error setting light brightness:", error);
      this._error = `Failed to set light brightness: ${error.message}`;
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

    const roomVolume = this.config.room_volume || 60; // Fallback matches DEFAULT_ROOM_VOLUME
    return Math.round((roomVolume / airflow) * 60 * 10) / 10; // minutes
  }

    _getComfortLevel(comfortIndex) {
    if (comfortIndex >= 80) return 'excellent';
    if (comfortIndex >= 60) return 'good';
    if (comfortIndex >= 40) return 'fair';
    return 'poor';
  }

  _getDewPointLevel(dewPoint) {
    if (dewPoint < 10) return 'excellent'; // Molto secco
    if (dewPoint < 13) return 'good';      // Secco
    if (dewPoint < 16) return 'fair';      // Confortevole
    if (dewPoint < 18) return 'good';      // Buono
    if (dewPoint < 21) return 'fair';      // Accettabile
    if (dewPoint < 24) return 'poor';      // Umido
    return 'poor';                         // Molto umido
  }

  _getHumidityLevel(absoluteHumidity) {
    if (absoluteHumidity < 7) return 'poor';      // Troppo secco
    if (absoluteHumidity < 9) return 'fair';      // Secco
    if (absoluteHumidity < 12) return 'excellent'; // Ottimale
    if (absoluteHumidity < 15) return 'good';      // Buono
    return 'poor';                                 // Troppo umido
  }

  _formatTimestamp(timestamp) {
    if (!timestamp) return 'N/A';

    try {
      const date = new Date(timestamp);
      const now = new Date();
      const diffMs = now - date;
      const diffMins = Math.floor(diffMs / 60000);

      if (diffMins < 1) return 'Ora';
      if (diffMins < 60) return `${diffMins} min fa`;
      if (diffMins < 1440) return `${Math.floor(diffMins / 60)} ore fa`;
      return date.toLocaleDateString('it-IT');
    } catch (e) {
      return timestamp;
    }
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
      ${this._renderModeControls()}
      ${this._renderLightControls()}
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

    // Discrete steps: 0-4, mapped to 0/25/50/75/100%
    const speedSteps = [
      { value: 0, pct: 0, icon: "mdi:fan-off", label: "Spento" },
      { value: 1, pct: 25, icon: "mdi:fan-speed-1", label: "Bassa" },
      { value: 2, pct: 50, icon: "mdi:fan-speed-2", label: "Media" },
      { value: 3, pct: 75, icon: "mdi:fan-speed-3", label: "Alta" },
      { value: 4, pct: 100, icon: "mdi:fan", label: "Massima" },
    ];
    const currentPercentage = parseFloat(vmcState.attributes.percentage || 0);
    // Find closest step
    const currentStep = speedSteps.reduce((prev, curr) => Math.abs(curr.pct - currentPercentage) < Math.abs(prev.pct - currentPercentage) ? curr : prev);

    // Track temporary slider value for optimistic UI
    const sliderValue = this._fanSliderValue !== undefined ? this._fanSliderValue : currentStep.value;
    const sliderStep = speedSteps[sliderValue] || currentStep;

    // Slider element: supporta sia ha-slider che ha-control-slider
    const slider =  html`<ha-control-slider
          min="0"
          max="4"
          step="1"
          .value="${sliderValue}"
          @input="${(e) => this._onFanSliderInput(e)}"
          @value-changed="${(e) => this._setFanSpeedDiscrete(e)}"
          ?disabled="${this._loading || vmcState.state === 'off'}"
          style="flex: 1;"
          dir="ltr"
        ></ha-control-slider>`;

    return html`
      <div class="controls-section">
        <div class="section-title">
          <ha-icon icon="mdi:fan"></ha-icon>
          <span>Velocità Ventilazione</span>
        </div>
        <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 8px;">
          <ha-icon icon="${sliderStep.icon}" style="font-size: 2rem;"></ha-icon>
          ${slider}
          <span style="min-width: 40px; text-align: right; font-weight: 600;">${sliderStep.pct}%</span>
        </div>
        <div class="speed-status">
          Velocità attuale: <b>${sliderStep.label}</b> (${sliderStep.pct}%)
        </div>
      </div>
    `;
  }

  // Track slider value for optimistic UI
  _onFanSliderInput(e) {
    const val = Number(e.target.value);
    if (!isNaN(val) && val >= 0 && val <= 4) {
      this._fanSliderValue = val;
      this.requestUpdate();
    }
  }

  // Handler for discrete slider
  async _setFanSpeedDiscrete(e) {
    const step = Number(e.target.value);
    if (!isNaN(step) && step >= 0 && step <= 4) {
      this._fanSliderValue = step;
      this.requestUpdate();
      let success = false;
      try {
        this._loading = true;
        await this._setFanSpeed(step);
        success = true;
      } catch (err) {
        let msg = "Errore: impossibile impostare la velocità.";
        if (err && err.message) msg += ` (${err.message})`;
        fireEvent(this, "hass-notification", { message: msg });
      } finally {
        this._loading = false;
        // Se errore, resetta slider allo stato entity
        if (!success) {
          this._fanSliderValue = undefined;
          this.requestUpdate();
        } else {
          // Su successo, lascia che il valore venga aggiornato dal backend
          setTimeout(() => {
            this._fanSliderValue = undefined;
            this.requestUpdate();
          }, 500);
        }
      }
    }
  }

  _renderLightControls() {
    const deviceSlug = this._getDeviceSlug();
    const vmcState = this._getVmcState();
    if (!deviceSlug) return nothing;

    const lightEntity = `light.vmc_helty_${deviceSlug}_light`;
    const timerEntity = `light.vmc_helty_${deviceSlug}_light_timer`;

    const lightState = this._getEntityState(lightEntity);
    const timerState = this._getEntityState(timerEntity);

    // Show light controls only if enabled in config and at least one light entity is available
    if (this.config.show_lights === false || (!lightState && !timerState)) return nothing;

    return html`
      <div class="controls-section">
        <div class="section-title">
          <ha-icon icon="mdi:lightbulb"></ha-icon>
          <span>Controlli Luci</span>
        </div>
        <div class="light-controls">
          ${lightState && this.config.show_lights !== false ? html`
            <div class="light-control">
              <ha-icon icon="mdi:lightbulb"></ha-icon>
              <span>Luminosità</span>
              <mwc-switch
                .checked="${lightState.state === 'on'}"
                @change="${() => this._toggleLight(lightEntity)}"
                ?disabled="${this._loading}"
              ></mwc-switch>
            </div>

            ${lightState.state === 'on' ? html`
              <div class="light-slider">
                <ha-icon icon="mdi:brightness-6"></ha-icon>
                <ha-control-slider
                  .value="${Math.round((lightState.attributes.brightness || 0) / 2.55)}"
                  min="0"
                  max="100"
                  step="25"
                  @value-changed="${(e) => this._setLightBrightness(lightEntity, e.target.value)}"
                  ?disabled="${this._loading || vmcState.state === 'off'}"
                ></ha-control-slider>
                <span class="brightness-value">${Math.round((lightState.attributes.brightness || 0) / 2.55)}%</span>
              </div>
            ` : nothing}
          ` : nothing}

          ${timerState && this.config.show_timer !== false ? html`
            <div class="light-control">
              <ha-icon icon="mdi:timer"></ha-icon>
              <span>Timer Luci</span>
              <mwc-switch
                .checked="${timerState.state === 'on'}"
                @change="${() => this._toggleLight(timerEntity)}"
                ?disabled="${this._loading}"
              ></mwc-switch>
            </div>

            ${timerState.state === 'on' && timerState.attributes.timer_seconds ? html`
              <div class="timer-info">
                <ha-icon icon="mdi:clock-outline"></ha-icon>
                <span>${Math.round(timerState.attributes.timer_seconds / 60)} min rimanenti</span>
              </div>
            ` : nothing}
          ` : nothing}
        </div>
      </div>
    `;
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

    // Sensori aggiuntivi configurabili
    const baseEntityId = this.config.entity.replace('fan.', '');

    // Portata d'aria
    if (this.config.show_airflow) {
      const airflowState = this._getEntityState(`sensor.${baseEntityId}_airflow`);
      if (airflowState) {
        sensors.push({
          label: 'Portata aria',
          icon: 'mdi:fan',
          value: this._formatSensorValue(airflowState.state, 'm³/h'),
          unit: 'm³/h',
          source: 'VMC'
        });
      }
    }

    // Ore filtro
    if (this.config.show_filter_hours) {
      const filterHoursState = this._getEntityState(`sensor.${baseEntityId}_filter_hours`);
      if (filterHoursState) {
        sensors.push({
          label: 'Ore filtro',
          icon: 'mdi:air-filter',
          value: this._formatSensorValue(filterHoursState.state, 'h'),
          unit: 'h',
          source: 'VMC'
        });
      }
    }

    // Stato dispositivo
    if (this.config.show_device_status) {
      const deviceState = this._getEntityState(`binary_sensor.${baseEntityId}_status`);
      if (deviceState) {
        sensors.push({
          label: 'Stato',
          icon: deviceState.state === 'on' ? 'mdi:power' : 'mdi:power-off',
          value: deviceState.state === 'on' ? 'Acceso' : 'Spento',
          unit: '',
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
          </div>
        `)}
      </div>
    `;
  }

  _renderAdvancedSensors() {
    const baseEntityId = this.config.entity.replace('fan.', '');
    const advancedSensors = [];

    // Sensori avanzati dall'integrazione (preferiti rispetto ai calcoli client-side)

    // Umidità assoluta
    const absoluteHumidityState = this._getEntityState(`sensor.${baseEntityId}_absolute_humidity`);
    if (absoluteHumidityState) {
      advancedSensors.push({
        label: 'Umidità assoluta',
        icon: 'mdi:water',
        value: this._formatSensorValue(absoluteHumidityState.state, 'g/m³'),
        unit: 'g/m³',
        comfort: this._getHumidityLevel(parseFloat(absoluteHumidityState.state))
      });
    }

    // Dew Point (sensore integrazione)
    const dewPointState = this._getEntityState(`sensor.${baseEntityId}_dew_point`);
    if (dewPointState) {
      advancedSensors.push({
        label: 'Punto di rugiada',
        icon: 'mdi:thermometer-water',
        value: this._formatSensorValue(dewPointState.state, '°C'),
        unit: '°C',
        comfort: this._getDewPointLevel(parseFloat(dewPointState.state))
      });
    }

    // Delta Dew Point
    const dewPointDeltaState = this._getEntityState(`sensor.${baseEntityId}_dew_point_delta`);
    if (dewPointDeltaState) {
      const delta = parseFloat(dewPointDeltaState.state);
      advancedSensors.push({
        label: 'Delta punto rugiada',
        icon: 'mdi:thermometer-minus',
        value: this._formatSensorValue(dewPointDeltaState.state, '°C'),
        unit: '°C',
        comfort: delta > 0 ? 'good' : 'poor'
      });
    }

    // Comfort Index (sensore integrazione)
    const comfortIndexState = this._getEntityState(`sensor.${baseEntityId}_comfort_index`);
    if (comfortIndexState) {
      advancedSensors.push({
        label: 'Indice comfort',
        icon: 'mdi:account-check',
        value: this._formatSensorValue(comfortIndexState.state, '%'),
        unit: '%',
        comfort: this._getComfortLevel(parseFloat(comfortIndexState.state))
      });
    }

    // Air Exchange Time (sensore integrazione)
    const airExchangeTimeState = this._getEntityState(`sensor.${baseEntityId}_air_exchange_time`);
    if (airExchangeTimeState) {
      const exchangeTime = parseFloat(airExchangeTimeState.state);
      let category = 'poor';
      if (exchangeTime <= 20) category = 'excellent';
      else if (exchangeTime <= 30) category = 'good';
      else if (exchangeTime <= 60) category = 'fair';

      advancedSensors.push({
        label: 'Tempo ricambio aria',
        icon: 'mdi:clock-time-four',
        value: this._formatSensorValue(airExchangeTimeState.state, 'min'),
        unit: 'min',
        comfort: category
      });
    }

    // Daily Air Changes
    const dailyAirChangesState = this._getEntityState(`sensor.${baseEntityId}_daily_air_changes`);
    if (dailyAirChangesState) {
      const dailyChanges = parseFloat(dailyAirChangesState.state);
      let category = 'poor';
      if (dailyChanges >= 20) category = 'excellent';
      else if (dailyChanges >= 15) category = 'good';
      else if (dailyChanges >= 10) category = 'fair';

      advancedSensors.push({
        label: 'Ricambi aria/giorno',
        icon: 'mdi:refresh',
        value: this._formatSensorValue(dailyAirChangesState.state, ''),
        unit: 'ricambi',
        comfort: category
      });
    }

    // Informazioni di rete (solo se abilitato)
    if (this.config.show_network_info) {
      // Ultima risposta
      const lastResponseState = this._getEntityState(`sensor.${baseEntityId}_last_response`);
      if (lastResponseState) {
        advancedSensors.push({
          label: 'Ultima comunicazione',
          icon: 'mdi:clock-outline',
          value: this._formatTimestamp(lastResponseState.state),
          unit: '',
          source: 'VMC'
        });
      }

      // Indirizzo IP
      const ipAddressState = this._getEntityState(`sensor.${baseEntityId}_ip_address`);
      if (ipAddressState) {
        advancedSensors.push({
          label: 'Indirizzo IP',
          icon: 'mdi:ip-network',
          value: ipAddressState.state,
          unit: '',
          source: 'VMC'
        });
      }
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
      room_volume: 60, // Should match DEFAULT_ROOM_VOLUME in Python const.py
      show_temperature: true,
      show_humidity: true,
      show_co2: true,
      show_voc: false,
      show_advanced: true,
      show_lights: true,
      show_timer: true,
      enable_comfort_calculations: true,
      enable_air_exchange: true
    };
  }

  setConfig(config) {
    this.config = config;
    this.requestUpdate();
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

console.info(`%c VMC HELTY CARD v2.1 LitElement %c Loaded successfully!`,
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
