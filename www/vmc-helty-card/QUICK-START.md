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
```

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
temperature_entity: sensor.cucina_temperatura_accurata
humidity_entity: sensor.cucina_umidita_accurata
room_volume: 32.4  # 4.5m × 3.6m × 2.0m
show_advanced: true
enable_comfort_calculations: true
enable_air_exchange: true
```

### Soggiorno Grande
```yaml
type: custom:vmc-helty-card
entity: fan.vmc_helty_flow_soggiorno
name: "VMC Soggiorno"
room_volume: 89.6  # 8m × 5.6m × 2.0m
show_co2: true
show_voc: true
show_advanced: true
```

### Bagno - Configurazione Minima
```yaml
type: custom:vmc-helty-card
entity: fan.vmc_helty_flow_bagno
name: "Ventilazione Bagno"
room_volume: 15.75  # 2.5m × 3.5m × 1.8m
show_co2: false
show_voc: false
show_advanced: false
```

## 📐 Calcolo Volume Stanza

### Calcolatore Integrato
Nell'editor visuale:
1. **Inserisci dimensioni**: Lunghezza × Larghezza × Altezza (metri)
2. **Click Calcola**: Volume automaticamente impostato
3. **Regola fine**: Modifica il valore se necessario

### Volumi Standard
- **Bagno piccolo**: 10-20 m³
- **Camera**: 30-50 m³
- **Cucina**: 25-45 m³
- **Soggiorno**: 60-120 m³
- **Open space**: 100-300 m³

## 🌡️ Perché Usare Sensori Personalizzati?

1. **Precisione**: Sensori esterni più accurati di quelli interni VMC
2. **Posizionamento**: Sensori posizionati ottimalmente nella stanza
3. **Qualità**: Sensori premium con maggiore accuratezza
4. **Zone Specifiche**: Sensori corrispondenti all'area ventilata

## 📊 Funzioni Avanzate

### Punto di Rugiada
- **Calcolo**: Formula Magnus con temperatura/umidità selezionate
- **Scopo**: Valutazione rischio condensa
- **Unità**: °C

### Indice Comfort
- **Algoritmo**: Punteggio comfort basato su temperatura + umidità
- **Categorie**:
  - Eccellente: 85-100%
  - Buono: 70-84%
  - Discreto: 55-69%
  - Scarso: 0-54%

### Tempo Ricambio Aria
- **Calcolo**: Volume stanza ÷ Flusso ventilatore × 60 (minuti)
- **Flussi d'aria**:
  - Velocità 0: 0 m³/h (Spento)
  - Velocità 1: 10 m³/h
  - Velocità 2: 17 m³/h
  - Velocità 3: 26 m³/h
  - Velocità 4: 37 m³/h
- **Valutazioni**:
  - Eccellente: ≤20 minuti
  - Buono: 21-30 minuti
  - Accettabile: 31-60 minuti
  - Scarso: >60 minuti

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

### Problemi Calcolo Volume
```
Ricambio aria mostra categoria "Scarso"
```
**Soluzioni**:
1. Verifica che il volume stanza sia accurato per lo spazio
2. Controlla se il flusso d'aria VMC corrisponde alle specifiche del tuo modello
3. Considera la disposizione stanza (porte aperte, collegamenti ad altre stanze)

## ✨ Funzionalità v2.0

### 🆕 Novità Principali
- ✅ **Selezione Dispositivo**: Supporto multipli VMC
- ✅ **Sensori Personalizzati**: Usa sensori esterni per precisione
- ✅ **Volume Stanza**: Calcoli ricambio aria accurati
- ✅ **Editor Visuale**: Configurazione semplice e intuitiva
- ✅ **Compatibilità v1.x**: Tutte le configurazioni esistenti funzionano

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
