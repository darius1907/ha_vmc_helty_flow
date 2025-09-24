# Home Assistant Custom Card Development Guidelines

Basato sulle linee guida ufficiali di Home Assistant per lo sviluppo del frontend e delle card personalizzate.

## 🏗️ **Architettura e Principi Fondamentali**

### **1. Mobile-First Design**
```javascript
// ✅ Corretto - Design responsivo mobile-first
class VmcHeltyCard extends LitElement {
  static get styles() {
    return css`
      :host {
        display: block;
        padding: 16px;
        box-sizing: border-box;
      }

      /* Mobile first (default) */
      .card-content {
        display: flex;
        flex-direction: column;
        gap: 12px;
      }

      /* Tablet e desktop */
      @media (min-width: 768px) {
        .card-content {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 16px;
        }
      }
    `;
  }
}
```

### **2. Progressive Web App (PWA) Compatibility**
```javascript
// ✅ Supporto per Progressive Web App
class VmcHeltyCard extends LitElement {
  connectedCallback() {
    super.connectedCallback();

    // Registra service worker se disponibile
    if ('serviceWorker' in navigator) {
      this._registerServiceWorker();
    }
  }

  _registerServiceWorker() {
    // Gestione service worker per funzionalità offline
  }
}
```

## 🎨 **Design System e UI Guidelines**

### **1. Tema e Styling Consistency**
```javascript
// ✅ Usa le variabili CSS di Home Assistant
static get styles() {
  return css`
    :host {
      /* Colori del tema HA */
      --primary-color: var(--primary-color);
      --accent-color: var(--accent-color);
      --text-primary-color: var(--text-primary-color);
      --card-background-color: var(--card-background-color);
      --divider-color: var(--divider-color);

      /* Stati di attivazione */
      --state-active-color: var(--state-active-color);
      --state-inactive-color: var(--state-inactive-color);

      /* Errori e warning */
      --error-color: var(--error-color);
      --warning-color: var(--warning-color);
      --success-color: var(--success-color);
    }

    .card {
      background: var(--card-background-color);
      border-radius: var(--ha-card-border-radius, 12px);
      box-shadow: var(--ha-card-box-shadow);
      color: var(--text-primary-color);
    }
  `;
}
```

### **2. Icone e Iconografia**
```javascript
// ✅ Usa Material Design Icons (mdi)
render() {
  return html`
    <ha-card>
      <div class="card-content">
        <ha-icon
          icon="mdi:fan"
          class="fan-icon ${this._fanState === 'on' ? 'active' : ''}"
        ></ha-icon>

        <!-- Stati con icone appropriate -->
        <div class="status-indicators">
          <ha-icon icon="mdi:thermometer"></ha-icon>
          <ha-icon icon="mdi:water-percent"></ha-icon>
          <ha-icon icon="mdi:molecule-co2"></ha-icon>
        </div>
      </div>
    </ha-card>
  `;
}
```

### **3. Tipografia e Spacing**
```css
/* ✅ Sistema di spaziature coerente */
:host {
  /* Spaziature standard HA */
  --spacing-xs: 4px;
  --spacing-s: 8px;
  --spacing-m: 16px;
  --spacing-l: 24px;
  --spacing-xl: 32px;
}

.card-content {
  padding: var(--spacing-m);
  gap: var(--spacing-s);
}

.section-title {
  font-family: var(--paper-font-headline_-_font-family);
  font-size: var(--paper-font-headline_-_font-size);
  font-weight: var(--paper-font-headline_-_font-weight);
  margin-bottom: var(--spacing-s);
}
```

## ⚡ **Performance Guidelines**

### **1. Lazy Loading e Code Splitting**
```javascript
// ✅ Lazy loading per componenti pesanti
class VmcHeltyCard extends LitElement {
  async _loadAdvancedFeatures() {
    if (!this._advancedFeaturesLoaded) {
      const { AdvancedVmcControls } = await import('./advanced-controls.js');
      this._advancedFeaturesLoaded = true;
    }
  }

  connectedCallback() {
    super.connectedCallback();

    // Carica solo se necessario
    if (this.config.show_advanced_controls) {
      this._loadAdvancedFeatures();
    }
  }
}
```

### **2. Efficient Rendering**
```javascript
// ✅ Minimizza re-rendering con shouldUpdate
shouldUpdate(changedProps) {
  // Aggiorna solo se cambiano proprietà rilevanti
  if (changedProps.has('hass')) {
    const oldHass = changedProps.get('hass');
    if (oldHass) {
      // Controlla solo le entità che ci interessano
      return this._entityIds.some(entityId =>
        oldHass.states[entityId] !== this.hass.states[entityId]
      );
    }
  }
  return changedProps.has('config');
}
```

### **3. Memory Management**
```javascript
// ✅ Pulizia delle risorse
disconnectedCallback() {
  super.disconnectedCallback();

  // Rimuovi event listeners
  if (this._resizeObserver) {
    this._resizeObserver.disconnect();
  }

  // Cancella timer
  if (this._updateTimer) {
    clearInterval(this._updateTimer);
  }
}
```

## 🔌 **Integration Guidelines**

### **1. Entity State Management**
```javascript
// ✅ Gestione stati entità robusta
_getEntityState(entityId) {
  if (!this.hass || !entityId) {
    return null;
  }

  const state = this.hass.states[entityId];
  if (!state) {
    console.warn(`Entity ${entityId} not found`);
    return null;
  }

  return state;
}

_isEntityAvailable(entityId) {
  const state = this._getEntityState(entityId);
  return state && state.state !== 'unavailable' && state.state !== 'unknown';
}
```

### **2. Service Calls**
```javascript
// ✅ Service calls con error handling
async _callService(domain, service, serviceData = {}) {
  try {
    await this.hass.callService(domain, service, serviceData);
  } catch (error) {
    console.error(`Failed to call ${domain}.${service}:`, error);

    // Mostra notifica di errore all'utente
    this._showError(`Failed to ${service.replace('_', ' ')}`);
  }
}

_showError(message) {
  const event = new CustomEvent('hass-notification', {
    detail: { message, type: 'error' },
    bubbles: true,
    composed: true
  });
  this.dispatchEvent(event);
}
```

### **3. Configuration Validation**
```javascript
// ✅ Validazione configurazione completa
setConfig(config) {
  if (!config) {
    throw new Error('Invalid configuration');
  }

  // Validazione entità richieste
  if (!config.entity) {
    throw new Error('You need to define an entity');
  }

  // Validazione tipo entità
  if (!config.entity.startsWith('fan.')) {
    throw new Error('Entity must be a fan');
  }

  // Configurazione con defaults
  this.config = {
    show_temperature: true,
    show_humidity: true,
    show_co2: true,
    theme: 'default',
    ...config
  };
}
```

## 🎛️ **User Experience Guidelines**

### **1. Accessibility (a11y)**
```javascript
// ✅ Supporto completo per accessibilità
render() {
  return html`
    <ha-card
      role="region"
      aria-label="VMC Helty Flow Control"
    >
      <div class="card-content">
        <!-- Controlli con ARIA labels -->
        <button
          class="fan-button"
          @click=${this._toggleFan}
          aria-label="Toggle fan ${this._fanState === 'on' ? 'off' : 'on'}"
          aria-pressed=${this._fanState === 'on'}
        >
          <ha-icon icon="mdi:fan"></ha-icon>
        </button>

        <!-- Slider con ARIA -->
        <ha-slider
          min="0"
          max="100"
          .value=${this._fanSpeed}
          @value-changed=${this._fanSpeedChanged}
          aria-label="Fan speed: ${this._fanSpeed}%"
          role="slider"
        ></ha-slider>
      </div>
    </ha-card>
  `;
}
```

### **2. Touch-Friendly Controls**
```css
/* ✅ Controlli ottimizzati per touch */
.control-button {
  min-height: 44px; /* Apple's minimum touch target */
  min-width: 44px;
  padding: var(--spacing-s);
  border-radius: var(--ha-card-border-radius);

  /* Feedback visivo per touch */
  transition: transform 0.1s ease;
}

.control-button:active {
  transform: scale(0.95);
}

/* Spazio tra controlli per evitare tocchi accidentali */
.controls-grid {
  gap: var(--spacing-s);
}
```

### **3. Loading States e Feedback**
```javascript
// ✅ Stati di caricamento e feedback utente
render() {
  return html`
    <ha-card class="${this._isLoading ? 'loading' : ''}">
      <div class="card-content">
        ${this._isLoading ? html`
          <div class="loading-overlay">
            <ha-circular-progress active></ha-circular-progress>
            <span>Loading VMC data...</span>
          </div>
        ` : this._renderContent()}
      </div>
    </ha-card>
  `;
}
```

## 🔧 **Configuration Editor Guidelines**

### **1. Visual Configuration Schema**
```javascript
// ✅ Schema di configurazione completo
static getConfigElement() {
  return document.createElement('vmc-helty-card-editor');
}

static getStubConfig() {
  return {
    type: 'custom:vmc-helty-card',
    entity: 'fan.vmc_helty_flow',
    show_temperature: true,
    show_humidity: true,
    show_co2: true,
    theme: 'default'
  };
}
```

### **2. Editor Implementation**
```javascript
// ✅ Editor con validazione live
class VmcHeltyCardEditor extends LitElement {
  setConfig(config) {
    this._config = config;
  }

  _entityChanged(ev) {
    const newConfig = {
      ...this._config,
      entity: ev.detail.value
    };

    // Validazione real-time
    this._validateConfig(newConfig);

    // Dispatch evento di cambiamento
    const changeEvent = new CustomEvent('config-changed', {
      detail: { config: newConfig },
      bubbles: true,
      composed: true
    });
    this.dispatchEvent(changeEvent);
  }

  _validateConfig(config) {
    // Validazione e feedback visivo
    const entitySelect = this.shadowRoot.querySelector('#entity-select');
    if (config.entity && !config.entity.startsWith('fan.')) {
      entitySelect.classList.add('error');
      entitySelect.setAttribute('error-message', 'Must be a fan entity');
    } else {
      entitySelect.classList.remove('error');
      entitySelect.removeAttribute('error-message');
    }
  }
}
```

## 🚀 **Distribution e Packaging**

### **1. Manifest e Metadata**
```json
// ✅ package.json per HACS compatibility
{
  "name": "vmc-helty-card",
  "version": "1.0.0",
  "description": "Advanced Lovelace card for VMC Helty Flow control",
  "main": "vmc-helty-card.js",
  "keywords": ["home-assistant", "lovelace", "card", "vmc", "ventilation"],
  "author": "Your Name",
  "license": "MIT",
  "homepage": "https://github.com/yourusername/vmc-helty-card",
  "repository": {
    "type": "git",
    "url": "https://github.com/yourusername/vmc-helty-card.git"
  }
}
```

### **2. HACS Compatibility**
```json
// ✅ hacs.json per HACS store
{
  "name": "VMC Helty Control Card",
  "content_in_root": false,
  "filename": "vmc-helty-card.js",
  "country": "IT",
  "render_readme": true,
  "domains": ["fan", "sensor", "button", "switch"]
}
```

### **3. Version Management**
```javascript
// ✅ Console info per debugging
console.info(
  `%c VMC-HELTY-CARD %c v1.0.0 `,
  'color: orange; font-weight: bold; background: black',
  'color: white; font-weight: bold; background: dimgray'
);

// Version check per compatibilità
const MIN_HA_VERSION = '2024.1.0';
if (window.hassVersion && compareVersions(window.hassVersion, MIN_HA_VERSION) < 0) {
  console.warn(`VMC Helty Card requires Home Assistant ${MIN_HA_VERSION} or newer`);
}
```

## 🛡️ **Security e Best Practices**

### **1. Input Sanitization**
```javascript
// ✅ Sanitizzazione input utente
_sanitizeInput(input) {
  if (typeof input !== 'string') {
    return '';
  }

  // Rimuovi HTML/script tags
  return input
    .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
    .replace(/<[^>]+>/g, '')
    .trim();
}
```

### **2. Error Boundaries**
```javascript
// ✅ Gestione errori robusta
updated(changedProps) {
  super.updated(changedProps);

  try {
    this._updateEntityStates();
  } catch (error) {
    console.error('Error updating entity states:', error);
    this._showFallbackUI();
  }
}

_showFallbackUI() {
  // Interfaccia di fallback in caso di errori
  this.shadowRoot.innerHTML = `
    <ha-card>
      <div class="error-state">
        <ha-icon icon="mdi:alert"></ha-icon>
        <p>Unable to load VMC controls</p>
      </div>
    </ha-card>
  `;
}
```

### **3. CSP Compliance**
```javascript
// ✅ Content Security Policy compliance
// Evita inline styles e scripts
static get styles() {
  return css`
    /* Tutti gli stili in CSS, non inline */
  `;
}

// No eval() o Function() constructor
// No innerHTML con contenuto non sicuro
```

## 📚 **Documentation Requirements**

### **1. README Structure**
```markdown
# VMC Helty Control Card

## Installation
### Manual Installation
### HACS Installation

## Configuration
### Basic Configuration
### Advanced Options
### Entity Requirements

## Examples
### Minimal Setup
### Full Feature Setup
### Custom Themes

## Troubleshooting
### Common Issues
### Debug Mode
### Support Channels

## Contributing
### Development Setup
### Testing
### Pull Request Guidelines

## License
```

### **2. Code Documentation**
```javascript
/**
 * Advanced Lovelace card for VMC Helty Flow control
 *
 * @class VmcHeltyCard
 * @extends {LitElement}
 *
 * @example
 * ```yaml
 * type: custom:vmc-helty-card
 * entity: fan.vmc_helty_flow
 * show_temperature: true
 * ```
 */
class VmcHeltyCard extends LitElement {
  /**
   * Configure the card with user settings
   * @param {Object} config - Card configuration
   * @param {string} config.entity - Fan entity ID
   * @param {boolean} [config.show_temperature=true] - Show temperature sensors
   */
  setConfig(config) {
    // Implementation
  }
}
```

Queste linee guida garantiscono che la card sia:
- **Performante** e ottimizzata per dispositivi mobili
- **Accessibile** a tutti gli utenti
- **Coerente** con il design system di Home Assistant
- **Sicura** e robusta
- **Facilmente configurabile** e mantenibile

La nostra implementazione attuale segue già la maggior parte di queste linee guida! 🎯
