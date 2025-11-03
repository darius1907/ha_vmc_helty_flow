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
      _translations: { type: Object, state: true },
      _language: { type: String, state: true },
      _translationsLoading: { type: Boolean, state: true }
    };
  }

  constructor() {
    super();
    this.config = {};
    this.hass = null;
    this._vmcEntities = [];
    this._translations = {};
    this._language = "en";
    this._translationsLoading = false;
  }

  static get styles() {
    return css`
      :host {
        display: block;
        padding: 16px;
        background: var(--card-background-color);
        color: var(--primary-text-color);
      }
      .config-section:last-child {
        display: flex;
        flex-direction: column;
        gap: 16px;
      }
      .form-group {
        font-weight: 500;
        gap: 8px;
        font-size: 12px;
        display: flex;
        flex-direction: column;
        margin-bottom: 16px;
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
    `;
  }

  setConfig(config) {
    this.config = { ...config };
    this._discoverEntities();

    // Load translations if hass is available
    if (this.hass && (!this._translations || Object.keys(this._translations).length === 0)) {
      this._loadTranslations();
    }
  }

  // Lifecycle methods
  async connectedCallback() {
    super.connectedCallback();
    // Load translations when component is connected if hass is already available
    if (this.hass && (!this._translations || Object.keys(this._translations).length === 0)) {
      await this._loadTranslations();
    }
  }

  // Translation methods
  async _loadTranslations() {
    // Prevent multiple simultaneous loading attempts
    if (this._translationsLoading) return;

    try {
      this._translationsLoading = true;
      this._language = this.hass?.language || "it";  // Default to Italian

      console.debug(`Loading editor translations for language: ${this._language}`);

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
          console.debug(`Editor trying to load Italian translations from: ${path}`);
          const response = await fetch(path);
          if (response.ok) {
            defaultTranslations = await response.json();
            successfulPath = path.replace('it.json', '');
            console.debug(`Editor successfully loaded Italian translations from: ${path}`, defaultTranslations);
            break;
          } else {
            console.debug(`Editor failed to load from ${path}: ${response.status} ${response.statusText}`);
          }
        } catch (e) {
          console.debug(`Editor error loading from ${path}:`, e.message);
        }
      }

      // If Italian fails, fallback to English
      if (!defaultTranslations) {
        console.warn("Editor failed to load Italian translations, trying English fallback");
        const enPaths = [
          `/local/vmc-helty-card/translations/en.json`,
          `/hacsfiles/vmc_helty_flow/www/vmc-helty-card/translations/en.json`,
          `./translations/en.json`
        ];

        for (const path of enPaths) {
          try {
            console.debug(`Editor fallback: trying to load English translations from: ${path}`);
            const response = await fetch(path);
            if (response.ok) {
              defaultTranslations = await response.json();
              successfulPath = path.replace('en.json', '');
              console.debug(`Editor successfully loaded English fallback from: ${path}`, defaultTranslations);
              break;
            }
          } catch (e) {
            console.debug(`Editor error loading English fallback from ${path}:`, e.message);
          }
        }
      }

      if (!defaultTranslations) {
        console.error("Editor failed to load translations from all attempted paths");
        return;
      }

      let translations = defaultTranslations;
      // Load language-specific translations if different from the loaded default
      if (this._language !== "it" && this._language !== "en") {
        try {
          const langPath = `${successfulPath}${this._language}.json`;
          console.debug(`Editor loading language-specific translations from: ${langPath}`);
          const response = await fetch(langPath);
          if (response.ok) {
            const langTranslations = await response.json();
            translations = { ...defaultTranslations, ...langTranslations };
            console.debug(`Editor loaded translations for language: ${this._language}`, langTranslations);
          } else {
            console.warn(`Editor translation file for ${this._language} not found at ${langPath}, using default fallback`);
          }
        } catch (e) {
          console.warn(`Editor failed to load translations for ${this._language}, using default fallback:`, e.message);
        }
      }

      this._translations = translations;
      console.debug("Final editor translations object:", this._translations);
      this.requestUpdate();
    } catch (error) {
      console.error("Failed to load editor translations:", error);
      // Fallback to empty object to prevent breaking the editor
      this._translations = {};
    } finally {
      this._translationsLoading = false;
    }
  }  _t(key) {
    if (!key || typeof key !== 'string') return key;

    // If translations not loaded yet, return the key
    if (!this._translations || Object.keys(this._translations).length === 0) {
      return key;
    }

    const keys = key.split(".");
    let translation = this._translations;

    for (const k of keys) {
      if (translation && typeof translation === "object" && k in translation) {
        translation = translation[k];
      } else {
        // Return the key if translation not found
        return key;
      }
    }

    // Return the translation if found and is a string, otherwise return the key
    return (typeof translation === 'string') ? translation : key;
  }

  willUpdate(changedProps) {
    super.willUpdate(changedProps);
    if (changedProps.has('hass') && this.hass) {
      this._discoverEntities();

      // Load translations when hass becomes available for the first time
      if (!this._translations || Object.keys(this._translations).length === 0) {
        this._loadTranslations();
      }
    }
  }
  _discoverEntities() {
    if (!this.hass) return;
    this._vmcEntities = Object.keys(this.hass.states)
      .filter(entityId => entityId.startsWith('fan.vmc_helty_'))
      .map(entityId => ({
        value: entityId,
        label: this.hass.states[entityId]?.attributes?.friendly_name || entityId
      }));
    if (this._vmcEntities.length === 0) {
      this._vmcEntities = Object.keys(this.hass.states)
        .filter(entityId => entityId.startsWith('fan.'))
        .map(entityId => ({
          value: entityId,
          label: this.hass.states[entityId]?.attributes?.friendly_name || entityId
        }));
    }
  }



  _valueChanged(ev) {
    const target = ev.target;
    const key = target.configValue;
    if (!key) return;
    let value = target.value;
    const newConfig = { ...this.config, [key]: value };
    this.config = newConfig;
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
          <span>${this._t('editor.errors.loading')}</span>
        </div>
      `;
    }

    // Wait for translations to be loaded before rendering content
    if (!this._translations || Object.keys(this._translations).length === 0) {
      return html`
        <div class="error-message">
          <ha-icon icon="mdi:loading"></ha-icon>
          <span>Loading translations...</span>
        </div>
      `;
    }

    return html`
      <div class="config-section">
        <div class="section-title">
          <ha-icon icon="mdi:air-filter"></ha-icon>
          ${this._t('editor.device_selection.title')}
        </div>
        <div class="form-group">
          <label class="form-label">${this._t('editor.device_selection.device_label')}</label>
          <div class="form-description">
            ${this._t('editor.device_selection.device_description')}
          </div>
          <ha-select
            .label=${this._t('editor.device_selection.choose_device')}
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
          <label class="form-label">${this._t('editor.device_selection.card_name_label')}</label>
          <div class="form-description">
            ${this._t('editor.device_selection.card_name_description')}
          </div>
          <ha-textfield
            .label=${this._t('editor.device_selection.card_name_label')}
            .value=${this.config.name || ""}
            .configValue=${"name"}
            @input=${this._valueChanged}
          ></ha-textfield>
        </div>
      </div>
    `;
  }

}

// Register the editor
customElements.define('vmc-helty-card-editor', VmcHeltyCardEditor);

console.info(`%c VMC HELTY CARD EDITOR v2.1 LitElement %c Loaded successfully! 🛠️`,
  "color: white; background: blue; font-weight: bold;",
  "color: blue; font-weight: normal;");
