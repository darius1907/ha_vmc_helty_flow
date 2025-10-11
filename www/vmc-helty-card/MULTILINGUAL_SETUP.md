# VMC Helty Card - Supporto Multilingue

## ✨ Novità: Supporto Multilingue Completo!

La VMC Helty Card ora supporta completamente più lingue con rilevamento automatico dalla configurazione di Home Assistant.

### 🌍 Lingue Supportate

- **🇬🇧 English** (en) - Completo
- **🇮🇹 Italiano** (it) - Lingua predefinita
- **🇫🇷 Français** (fr) - Completo
- **🇩🇪 Deutsch** (de) - Completo
- **🇪🇸 Español** (es) - Completo

### 🚀 Come Funziona

1. **Rilevamento Automatico**: La card rileva automaticamente la lingua di Home Assistant
2. **Sistema di Fallback**: Se una traduzione manca, usa l'inglese come fallback
3. **Caricamento Dinamico**: Le traduzioni vengono caricate al volo senza riavviare
4. **Supporto Offline**: Traduzioni predefinite integrate nel codice

### 📁 Struttura Files

```
www/vmc-helty-card/
├── vmc-helty-card.js           # Card aggiornata con supporto multilingue
├── translations/
│   ├── en.json                 # Inglese
│   ├── it.json                 # Italiano (predefinito)
│   ├── fr.json                 # Francese
│   ├── de.json                 # Tedesco
│   └── es.json                 # Spagnolo
└── MULTILINGUAL_SETUP.md       # Questa guida
```

### 🔧 Installazione

1. **Copia i files di traduzione**: Assicurati che la cartella `translations/` sia presente in `/local/vmc-helty-card/`

2. **Verifica i percorsi**: I files devono essere accessibili a:
   ```
   /local/vmc-helty-card/translations/en.json
   /local/vmc-helty-card/translations/it.json
   /local/vmc-helty-card/translations/fr.json
   /local/vmc-helty-card/translations/de.json
   /local/vmc-helty-card/translations/es.json
   ```

3. **Riavvia Home Assistant** o forza il refresh della cache (Ctrl+F5)

### 🎯 Elementi Tradotti

- **Modalità Speciali**: Iperventilazione, Modalità Notte, Free Cooling
- **Velocità Ventilatore**: Spento, Bassa, Media, Alta, Massima
- **Controlli**: LED Pannello, Sensori, Velocità Ventilazione
- **Descrizioni**: Tutte le descrizioni dei controlli e funzioni
- **Stati**: Acceso, Spento, Automatico, Manuale

### 🛠️ Aggiungere Nuove Lingue

Per aggiungere una nuova lingua:

1. Crea un nuovo file `translations/{codice_lingua}.json`
2. Copia la struttura da `en.json`
3. Traduci tutti i valori di testo
4. La card rileverà automaticamente la nuova lingua

Esempio per il portoghese (`pt.json`):
```json
{
  "modes": {
    "hyperventilation": "Hiperventilação",
    "night_mode": "Modo Noturno",
    "free_cooling": "Resfriamento Livre"
  },
  "fan_speeds": {
    "off": "Desligado",
    "low": "Baixa",
    "medium": "Média",
    "high": "Alta",
    "max": "Máxima"
  }
}
```

### 🔍 Risoluzione Problemi

**Traduzione non si carica:**
- Verifica la console del browser per errori di fetch
- Controlla che i files siano accessibili via `/local/`
- Svuota la cache del browser (Ctrl+F5)

**Testo parzialmente tradotto:**
- Il testo non tradotto apparirà in inglese (fallback)
- Verifica che tutte le chiavi siano presenti nel file di traduzione

**Lingua sbagliata:**
- Controlla la configurazione della lingua in Home Assistant
- La card usa `hass.language` per rilevare la lingua

### ⚡ Prestazioni

- **Caricamento Lazy**: Le traduzioni si caricano solo quando necessario
- **Cache Browser**: I files di traduzione vengono cachati dal browser
- **Fallback Rapido**: Se il caricamento fallisce, usa traduzioni integrate
- **Dimensioni Ottimizzate**: Ogni file di traduzione è < 2KB

### 🎨 Personalizzazione Avanzata

Puoi personalizzare le traduzioni per il tuo caso specifico modificando i files JSON:

```json
{
  "modes": {
    "hyperventilation": "Boost Mode",  // Personalizzato
    "night_mode": "Silent Mode",       // Personalizzato
    "free_cooling": "Eco Mode"         // Personalizzato
  }
}
```

### 📈 Changelog

**v2.1.1**
- ✅ Supporto multilingue completo
- ✅ 5 lingue supportate
- ✅ Rilevamento automatico lingua
- ✅ Sistema di fallback robusto
- ✅ Traduzioni per tutti gli elementi UI

---

💡 **Suggerimento**: Contribuisci con nuove traduzioni! Crea un file per la tua lingua e condividilo con la community.
