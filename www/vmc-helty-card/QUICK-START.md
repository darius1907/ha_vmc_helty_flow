# 🚀 VMC Helty Card - Guida Rapida

## Installazione Veloce

### 1. Copia i File
```bash
# Crea la directory
mkdir -p /config/www/vmc-helty-card/### ✨ Funzionalità Principali

### 🆕 Caratteristiche Principali
- ✅ **Selezione Dispositivo**: Supporto multipli VMC
- ✅ **Sensori Personalizzati**: Usa sensori esterni per precisione
- ✅ **Volume Stanza**: Calcoli ricambio aria accurati
- ✅ **Editor Visuale**: Configurazione semplice e intuitiva
- ✅ **LitElement**: Architettura moderna e compatibilea i file della card
cp vmc-helty-card.js /config/www/vmc-helty-card/
cp vmc-helty-card-editor.js /config/www/vmc-helty-card/
```

### 2. Aggiungi alle Risorse di Lovelace
```yaml
resources:
  - url: /local/vmc-helty-card/vmc-helty-card.js
    type: module
  - url: /local/vmc-helty-card/vmc-helty-card-editor.js
    type: module
```

**Importante**: I file di traduzione vengono caricati automaticamente e NON devono essere aggiunti alle risorse.

### 3. Configurazione con Editor Visuale

1. **Modalità Modifica** → **Aggiungi Carta**
2. **Cerca "VMC Helty"** → Seleziona la carta
3. **Configura con l'editor**:
   - 🎯 **Seleziona VMC**: Scegli il dispositivo VMC dal menu
   - 🌡️ **Sensori Custom** (opzionale): Seleziona sensori di temperatura/umidità personalizzati
   - 📏 **Volume Stanza**: Imposta volume in m³ o usa il calcolatore integrato
   - ⚙️ **Opzioni Display**: Mostra/nascondi sensori e funzioni avanzate

## 🎯 Configurazioni di Esempio

### Cucina con Sensori Personalizzati

```yaml
type: custom:vmc-helty-card
entity: fan.vmc_helty_flow_cucina
name: "VMC Cucina"
```

## 🔧 Risoluzione Problemi Comuni

### Dispositivo Non Trovato

```
Errore: Definire un'entità fan VMC
```

**Soluzione**: Seleziona un'entità fan VMC valida dal menu

### Problemi Sensori Personalizzati

```
Avviso: Sensore personalizzato non disponibile
```

**Soluzioni**:

1. Verifica che l'entità sensore esista e sia disponibile
2. Controlla che il sensore abbia la device class o unità corretta
3. Usa l'editor visuale per ri-selezionare il sensore


### 🎨 Design e UX

- ✅ **Mobile-First**: Ottimizzato per tutti i dispositivi
- ✅ **Temi HA**: Integrazione completa con i temi Home Assistant
- ✅ **Accessibilità**: Supporto screen reader e navigazione tastiera
- ✅ **Icone MDI**: Icone Material Design attraverso ha-icon

### 🏆 Conformità Linee Guida

- ✅ **100% Conforme** alle linee guida Home Assistant frontend
- ✅ **Performance** ottimizzate per rendering efficiente
- ✅ **CSP Compliance** senza script o stili inline
- ✅ **Error Handling** robusto con feedback utente

---

**Inizia subito con VMC Helty Card!** 🌀

Per la documentazione completa: [README.md](README.md)
