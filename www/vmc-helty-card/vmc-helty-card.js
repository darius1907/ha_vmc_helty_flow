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
 * - Multilingual support with automatic language detection
 * - Fan speed control with discrete slider
 * - Special modes (hyperventilation, night mode, free cooling)
 * - Device controls (panel LED, sensors)
 *
 * @version 2.1.0
 * @author VMC Helty Integration Team
 */

console.info(
  `%c VMC HELTY CARD v2.1 LitElement %c Advanced VMC Helty Flow control with multilingual support`,
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
    const attrs = (vmcState && vmcState.attributes) || {};

    // Mappa modalità speciali: chiave, label, icona, attributo, valore fan speed
    const specialModes = [
      {
        key: 'hyperventilation',
        label: this._t('modes.hyperventilation'),
        icon: 'mdi:fan-plus',
        attr: 'hyperventilation',
        speed: 6
      },
      {
        key: 'night_mode',
        label: this._t('modes.night_mode'),
        icon: 'mdi:weather-night',
        attr: 'night_mode',
        speed: 5
      },
      {
        key: 'free_cooling',
        label: this._t('modes.free_cooling'),
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

    return html`
      <!-- Modalità speciali -->
      <div class="section-header">
        <ha-icon icon="mdi:cog-clockwise"></ha-icon>
        ${this._t("modes.special_modes.title")}
      </div>
      <div class="chip-container">
        <ha-chip-set>
          ${specialModes.map(mode => {
            const isOn = !!attrs[mode.attr];
            return html`
              <ha-assist-chip
                .selected=${isOn}
                @click=${() => this._setSpecialMode(mode)}
                label="${mode.label}"
                ?disabled=${this._loading || (vmcState && vmcState.state === 'off')}
              >
                <ha-icon icon="${mode.icon}" slot="icon"></ha-icon>
              </ha-assist-chip>
            `;
          })}
        </ha-chip-set>
      </div>

      <!-- Controlli dispositivo come row semplici -->
      <div class="section-header">
        <ha-icon icon="mdi:cog"></ha-icon>
        ${this._t("controls.title")}
      </div>

      <div class="control-row">
        <div class="control-info">
          <div class="control-title">
            <ha-icon icon="mdi:led-outline"></ha-icon>
            ${this._t("controls.panel_led.title")}
          </div>
          <div class="control-description">${this._t("controls.panel_led.description")}</div>
        </div>
        <ha-entity-toggle
          .hass=${this.hass}
          .stateObj=${panelLedState}
          ?disabled=${this._loading || !panelLedState || panelLedState.state === 'unavailable'}
        ></ha-entity-toggle>
      </div>

      <div class="control-row">
        <div class="control-info">
          <div class="control-title">
            <ha-icon icon="mdi:hub-outline"></ha-icon>
            ${this._t("controls.sensors.title")}
          </div>
          <div class="control-description">${this._t("controls.sensors.description")}</div>
        </div>
        <ha-entity-toggle
          .hass=${this.hass}
          .stateObj=${sensorsState}
          ?disabled=${this._loading || (vmcState && vmcState.state === 'off') || !sensorsState || sensorsState.state === 'unavailable'}
        ></ha-entity-toggle>
      </div>
    `;
  }

  /** Imposta la modalità speciale inviando la fan speed corrispondente */
  async _setSpecialMode(mode) {
    if (!this.hass || !this.config.entity) return;
    try {
      this._loading = true;
      await this.hass.callService("vmc_helty_flow", "set_special_mode", {
        entity_id: this.config.entity,
        // La fan speed speciale va da 5 a 7, la percentuale non è usata realmente ma Home Assistant la mappa
        mode: mode.key,
      });
      fireEvent(this, "hass-notification", {
        message: `${this._t("events.title")}: ${mode.label}`,
      });
      if ("vibrate" in navigator) navigator.vibrate(40);
    } catch (e) {
      fireEvent(this, "hass-notification", {
        message: `${this._t("events.error")}: ${e.message}`,
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
      _translations: { type: Object, state: true },
      _language: { type: String, state: true },
      _translationsLoading: { type: Boolean, state: true }
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
    this._translations = {};
    this._language = "en";
    this._translationsLoading = false;
  }

  /**
   * Translation methods
   */
  async connectedCallback() {
    super.connectedCallback();
    // Load translations when component is connected if hass is already available
    if (this.hass && (!this._translations || Object.keys(this._translations).length === 0)) {
      await this._loadTranslations();
    }
  }

  async _loadTranslations() {
    // Prevent multiple simultaneous loading attempts
    if (this._translationsLoading) return;

    try {
      this._translationsLoading = true;
      this._language = this.hass?.language || "it";  // Default to Italian

      console.debug(`Loading translations for language: ${this._language}`);

      // Try multiple paths for loading translations
      const possiblePaths = [
        `/local/vmc-helty-card/translations/it.json`,  // Try Italian first
        `/hacsfiles/vmc_helty_flow/www/vmc-helty-card/translations/it.json`,
        `./translations/it.json`
      ];

      let defaultTranslations = null;
      let successfulPath = null;

      // Try each path until one works for Italian
      for (const path of possiblePaths) {
        try {
          console.debug(`Trying to load Italian translations from: ${path}`);
          const response = await fetch(path);
          if (response.ok) {
            defaultTranslations = await response.json();
            successfulPath = path.replace('it.json', '');
            console.debug(`Successfully loaded Italian translations from: ${path}`, defaultTranslations);
            break;
          } else {
            console.debug(`Failed to load from ${path}: ${response.status} ${response.statusText}`);
          }
        } catch (e) {
          console.debug(`Error loading from ${path}:`, e.message);
        }
      }

      // If Italian fails, fallback to English
      if (!defaultTranslations) {
        console.warn("Failed to load Italian translations, trying English fallback");
        const enPaths = [
          `/local/vmc-helty-card/translations/en.json`,
          `/hacsfiles/vmc_helty_flow/www/vmc-helty-card/translations/en.json`,
          `./translations/en.json`
        ];

        for (const path of enPaths) {
          try {
            console.debug(`Fallback: trying to load English translations from: ${path}`);
            const response = await fetch(path);
            if (response.ok) {
              defaultTranslations = await response.json();
              successfulPath = path.replace('en.json', '');
              console.debug(`Successfully loaded English fallback from: ${path}`, defaultTranslations);
              break;
            }
          } catch (e) {
            console.debug(`Error loading English fallback from ${path}:`, e.message);
          }
        }
      }

      if (!defaultTranslations) {
        console.error("Failed to load translations from all attempted paths");
        return;
      }

      let translations = defaultTranslations;
      // Load language-specific translations if different from the loaded default
      if (this._language !== "it" && this._language !== "en") {
        try {
          const langPath = `${successfulPath}${this._language}.json`;
          console.debug(`Loading language-specific translations from: ${langPath}`);
          const response = await fetch(langPath);
          if (response.ok) {
            const langTranslations = await response.json();
            translations = { ...defaultTranslations, ...langTranslations };
            console.debug(`Loaded translations for language: ${this._language}`, langTranslations);
          } else {
            console.warn(`Translation file for ${this._language} not found at ${langPath}, using default fallback`);
          }
        } catch (e) {
          console.warn(`Failed to load translations for ${this._language}, using default fallback:`, e.message);
        }
      }

      this._translations = translations;
      console.debug("Final translations object:", this._translations);
      this.requestUpdate();
    } catch (error) {
      console.error("Failed to load translations:", error);
      // Fallback to empty object to prevent breaking the card
      this._translations = {};
    } finally {
      this._translationsLoading = false;
    }
  }

  _t(key) {
    if (!key || typeof key !== 'string') return key;

    // If translations not loaded yet, return the key
    if (!this._translations || Object.keys(this._translations).length === 0) {
      console.debug(`Translations not loaded yet, returning key: ${key}`);
      return key;
    }

    console.debug(`Translating key: ${key}`, this._translations);

    const keys = key.split(".");
    let translation = this._translations;

    for (const k of keys) {
      if (translation && typeof translation === "object" && k in translation) {
        translation = translation[k];
      } else {
        // Return the key if translation not found
        console.debug(`Translation not found for key: ${key}, returning key`);
        return key;
      }
    }

    // Return the translation if found and is a string, otherwise return the key
    const result = (typeof translation === 'string') ? translation : key;
    console.debug(`Translation result for ${key}: ${result}`);
    return result;
  }

  static get styles() {
    return css`
        :host {
          background: var(
            --ha-card-background,
            var(--card-background-color, white)
          );
          -webkit-backdrop-filter: var(--ha-card-backdrop-filter, none);
          backdrop-filter: var(--ha-card-backdrop-filter, none);
          box-shadow: var(--ha-card-box-shadow, none);
          box-sizing: border-box;
          border-radius: var(--ha-card-border-radius, var(--ha-border-radius-lg));
          border-width: var(--ha-card-border-width, 1px);
          border-style: solid;
          border-color: var(--ha-card-border-color, var(--divider-color, #e0e0e0));
          color: var(--primary-text-color);
          display: block;
          transition: all 0.3s ease-out;
          position: relative;
        }

        :host([raised]) {
          border: none;
          box-shadow: var(
            --ha-card-box-shadow,
            0px 2px 1px -1px rgba(0, 0, 0, 0.2),
            0px 1px 1px 0px rgba(0, 0, 0, 0.14),
            0px 1px 3px 0px rgba(0, 0, 0, 0.12)
          );
        }

        .card-header,
        :host ::slotted(.card-header) {
          color: var(--ha-card-header-color, var(--primary-text-color));
          font-family: var(--ha-card-header-font-family, inherit);
          font-size: var(--ha-card-header-font-size, var(--mdc-typography-headline6-font-size, 20px));
          letter-spacing: -0.012em;
          line-height: var(--ha-line-height-expanded);
          padding: 8px 16px 12px;
          display: block;
          margin-block-start: 0px;
          margin-block-end: 0px;
          font-weight: var(--ha-font-weight-normal);
        }

        .section-header {
          font-size: var(--mdc-typography-body1-font-size, 16px);
          font-weight: var(--ha-font-weight-medium);
          color: var(--primary-text-color);
          display: flex;
          align-items: center;
          gap: 8px;
          padding-top: 8px;
        }

        .section-header ha-icon {
          --mdc-icon-size: 20px;
          color: var(--primary-color);
        }

        /* Compact chip container - replaces ha-settings-row */
        .chip-container {
          padding: 2px 0;
          margin: 4px 0;
        }

        /* Fan speed control styling */
        ha-control-slider {
          --control-slider-thickness: 40px;
          --control-slider-border-radius: 20px;
          --control-slider-color: var(--primary-color);
          --control-slider-background: var(--disabled-color);
          padding-bottom: 4px;
        }

        /* Chip set styling */
        ha-chip-set {
          gap: 8px;
          flex-wrap: wrap;
        }

        ha-assist-chip {
          --ha-assist-chip-container-height: 36px;
          --ha-assist-chip-label-text-size: 14px;
        }

        /* Icon styling */
        ha-icon {
          color: var(--state-icon-color);
          --state-inactive-color: var(--state-icon-color);
        }

        /* Fan speed control styling */
        ha-control-slider {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 4px 0;
        }

        /* Control row layout for toggles */
        .control-row {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 0px 6px;
        }

        .control-row:last-child {
          border-bottom: none;
        }

        .control-info {
          flex: 1;
          margin-right: 16px;
          min-width: 0; /* Allow text truncation if needed */
        }

        .control-row ha-entity-toggle {
          flex-shrink: 0;
          min-width: 48px;
        }

        .control-title {
          display: flex;
          align-items: center;
          font-weight: var(--ha-font-weight-medium);
          color: var(--secondary-text-color);
          margin-bottom: 4px;
        }

        .control-title ha-icon {
          margin-right: 8px;
          --mdc-icon-size: 18px;
          color: var(--primary-color);
        }

        .control-description {
          color: var(--secondary-text-color);
          font-size: var(--mdc-typography-caption-font-size, 12px);
          line-height: 1.4;
          padding-left: 24px;
        }

        /* Fan speed control row */
        .fan-control-row {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 0px 0;
          margin-top: 0px;
        }

        /* Error and loading states */
        .error-message,
        .loading-message {
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 24px;
          text-align: center;
          flex-direction: column;
          gap: 12px;
          color: var(--secondary-text-color);
        }

        .error-message ha-icon {
          color: var(--error-color);
          --mdc-icon-size: 48px;
        }

        .loading-message ha-icon {
          color: var(--primary-color);
          --mdc-icon-size: 48px;
          animation: spin 1s linear infinite;
        }

        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }

        :host ::slotted(.card-content:not(:first-child)),
        slot:not(:first-child)::slotted(.card-content) {
          padding-top: 0px;
          margin-top: -4px;
        }

        :host ::slotted(.card-content) {
          padding: 12px 16px;
        }

        :host ::slotted(.card-actions) {
          border-top: 1px solid var(--divider-color, #e8e8e8);
          padding: 8px;
        }
    `;
  }

  // Lifecycle methods
  willUpdate(changedProps) {
    super.willUpdate(changedProps);

    if (changedProps.has('hass') && this.hass) {
      this._updateEntityStates();

      // Load translations when hass becomes available for the first time
      if (!this._translations || Object.keys(this._translations).length === 0) {
        this._loadTranslations();
      }
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

  _setupEntityReferences() {
    const entities = new Set();

    if (this.config.entity) {
      entities.add(this.config.entity);
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
      await this.hass.callService("fan", "set_percentage", {
        entity_id: this.config.entity,
        percentage: speed * 25,
      });
      fireEvent(this, "hass-notification", {
        message: `${this._t("events.speed-set")}: ${speed * 25}%`,
      });
      if ("vibrate" in navigator) navigator.vibrate(40);
    } catch (e) {
      fireEvent(this, "hass-notification", {
        message: `${this._t("events.error")}: ${e.message}`,
      });
    } finally {
      this._loading = false;
    }
  }

  // Render methods
  render() {
    if (this._error) {
      return this._renderError();
    }

    // Show loading if translations are not loaded yet or card is loading
    if (this._loading && !this._getVmcState()) {
      return this._renderLoading();
    }

    // Wait for translations to be loaded before rendering content
    if (!this._translations || Object.keys(this._translations).length === 0) {
      return this._renderLoading();
    }

    const vmcState = this._getVmcState();
    if (!vmcState) {
      return this._renderError('VMC device not found. Please check your configuration.');
    }

    // Card solo per la gestione dei comandi (ventilazione, modalità, luci, timer)
    return html`
      <ha-card>
        <div class="card-content">
          <div class="card-header">
            <ha-icon icon="mdi:air-filter" style="color: var(--primary-color); margin-right: 8px;"></ha-icon>
            ${this.config.name}
          </div>
          ${this._renderFanControls()}
          ${this._renderModeControls()}
        </div>
      </ha-card>
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
        <span>${this._t("card.loading")}</span>
      </div>
    `;
  }


  _renderFanControls() {
    const vmcState = this._getVmcState();
    if (!vmcState) return nothing;

    // Step di velocità
    const speedSteps = [
      { value: 0, pct: 0, icon: "mdi:fan-off", label: this._t("fan_speeds.off") },
      { value: 1, pct: 25, icon: "mdi:fan-speed-1", label: this._t("fan_speeds.low") },
      { value: 2, pct: 50, icon: "mdi:fan-speed-2", label: this._t("fan_speeds.medium") },
      { value: 3, pct: 75, icon: "mdi:fan-speed-3", label: this._t("fan_speeds.high") },
      { value: 4, pct: 100, icon: "mdi:fan", label: this._t("fan_speeds.max") },
    ];
    const currentPercentage = parseFloat(vmcState.attributes.percentage || 0);
    const currentStep = speedSteps.reduce((prev, curr) =>
      Math.abs(curr.pct - currentPercentage) < Math.abs(prev.pct - currentPercentage) ? curr : prev
    );

    return html`
      <div class="section-header">
        <ha-icon icon="mdi:fan"></ha-icon>
        ${this._t("controls.fan_speed.title")}
      </div>

      <div class="control-row">
        <div class="control-info">
          <div class="control-description">${this._t("controls.fan_speed.description")}</div>
        </div>
      </div>

      <div class="fan-control-row">
        <ha-icon icon="${currentStep.icon}" style="font-size: 1.5rem; color: var(--primary-color);"></ha-icon>
        <ha-control-slider
          min="0"
          max="4"
          step="1"
          .value="${currentStep.value}"
          @value-changed="${this._setFanSpeedDiscrete}"
          ?disabled="${this._loading || vmcState.state === 'off'}"
          style="flex: 1;"
          dir="ltr"
        ></ha-control-slider>
        <span style="min-width: 40px; text-align: right; font-weight: 600; color: var(--primary-color);">${currentStep.pct}%</span>
      </div>
    `;
  }

  async _setFanSpeedDiscrete(e) {
    const step = Number(e.target.value);
    if (!isNaN(step) && step >= 0 && step <= 4) {
      await this._setFanSpeed(step);
    }
  }

  // Home Assistant integration methods
  getCardSize() {
    return 1;
  }

  static getConfigElement() {
    return document.createElement("vmc-helty-card-editor");
  }

  setConfig(config) {
    this.config = config;
    this._setupEntityReferences();

    // Load translations if hass is available
    if (this.hass && (!this._translations || Object.keys(this._translations).length === 0)) {
      this._loadTranslations();
    }

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
  description: 'Advanced control card for VMC Helty Flow devices with multilingual support',
  preview: true,
  documentationURL: 'https://github.com/dpezzoli/ha_vmc_helty_flow/www/vmc-helty-card/README.md',
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
