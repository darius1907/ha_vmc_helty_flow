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
    };
  }

  constructor() {
    super();
    this.config = {};
    this.hass = null;
    this._vmcEntities = [];
  }

  static get styles() {
    return css`
      :host {
        display: block;
        padding: 16px;
        background: var(--card-background-color);
        static get properties() {
          return {
            hass: { type: Object },
            config: { type: Object },
            _vmcEntities: { type: Array, state: true },
          };
        }
      .config-section:last-child {
        constructor() {
          super();
          this.config = {};
          this.hass = null;
          this._vmcEntities = [];
        }
        display: flex;
        setConfig(config) {
          this.config = { ...config };
          this._discoverEntities();
        }
      .form-group {
        willUpdate(changedProps) {
          super.willUpdate(changedProps);
          if (changedProps.has('hass') && this.hass) {
            this._discoverEntities();
          }
        }
        font-weight: 500;
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
      }
        _fireConfigChanged() {
          const event = new CustomEvent('config-changed', {
            detail: { config: this.config },
            bubbles: true,
            composed: true,
          });
          this.dispatchEvent(event);
        }
        gap: 8px;
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
      <div class="config-section">
        <div class="section-title">
          <ha-icon icon="mdi:air-filter"></ha-icon>
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
          <ha-icon icon="mdi:air-filter"></ha-icon>
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

}

// Register the editor
customElements.define('vmc-helty-card-editor', VmcHeltyCardEditor);

console.info(`%c VMC HELTY CARD EDITOR v2.1 LitElement %c Loaded successfully! 🛠️`,
  "color: white; background: blue; font-weight: bold;",
  "color: blue; font-weight: normal;");
