# 📁 Heating Usage Tracker - Indice File

Panoramica completa di tutti i file disponibili per il sistema di tracciamento ore riscaldamento.

---

## 📚 Documentazione

### **README.md** 📖
**Descrizione:** Documentazione completa con tutte le informazioni necessarie
**Contiene:**
- Caratteristiche del sistema
- Soluzioni disponibili (Utility Meter vs LTS)
- Setup completo passo-passo
- Configurazione avanzata (template sensor, notifiche, energy dashboard)
- Dashboard e grafici
- Troubleshooting dettagliato
- Esempi di statistiche reali
- Query SQL per analisi avanzate

**Quando leggerlo:** Prima di iniziare la configurazione, per capire tutte le opzioni disponibili

---

### **QUICK_START.md** ⚡
**Descrizione:** Guida rapida per setup in 10 minuti
**Contiene:**
- Setup veloce dell'Opzione 1 (Utility Meter)
- 4 step essenziali con tempi stimati
- Esempi di grafici semplici
- Verifica funzionamento
- Troubleshooting rapido

**Quando leggerlo:** Se vuoi partire subito senza leggere tutta la documentazione

---

### **ARCHITECTURE.md** 🏗️
**Descrizione:** Architettura tecnica del sistema
**Contiene:**
- Diagrammi di flusso ASCII
- Schema database
- Ciclo di vita dei dati
- Retention policy
- Performance considerations
- Data security e backup

**Quando leggerlo:** Per capire come funziona internamente il sistema o per troubleshooting avanzato

---

## 🔧 File di Configurazione

### **configuration_example.yaml** ⚙️
**Descrizione:** Esempio completo di configurazione Utility Meter
**Contiene:**
- Definizione helper (input_number, input_text)
- Configurazione utility_meter (daily/weekly/monthly/yearly)
- Template sensor per calcoli avanzati (costi, media, percentuali)
- Automazione backup mensile
- Istruzioni per replicare su più valvole

**Come usarlo:**
1. Copia il contenuto
2. Incolla in `configuration.yaml` o `packages/heating_stats.yaml`
3. Adatta i nomi delle stanze
4. Riavvia Home Assistant

---

### **dashboard_example.yaml** 📊
**Descrizione:** Dashboard completo per visualizzare le statistiche
**Contiene:**
- Card riepilogo oggi
- Grafici storici (7 giorni, 3 mesi)
- Confronto periodi (giorno/settimana/mese)
- Grafico a torta distribuzione annuale
- Tabella storico dettagliato
- Grafico costi mensili
- Confronto multi-valvola
- Card alternative (markdown, mini-graph, history-graph)

**Come usarlo:**
1. Copia il contenuto
2. Vai su Lovelace → Modifica Dashboard → Aggiungi Vista
3. Passa a editor YAML
4. Incolla il codice
5. Salva

---

## 🤖 Blueprint

### **heating_usage_tracker.yaml** (Originale) 📋
**Descrizione:** Blueprint base per tracciamento ore giornaliere
**Caratteristiche:**
- ✅ Traccia ore giornaliere
- ✅ Reset a mezzanotte
- ✅ Log eventi nel logbook
- ❌ Non mantiene storico lungo termine

**Quando usarlo:**
- Con Utility Meter (Opzione 1)
- Per configurazione semplice
- Se non serve contatore cumulativo

**Helper richiesti:**
1. `input_number` per ore giornaliere
2. `input_text` per timestamp accensione

---

### **heating_usage_tracker_with_history.yaml** (Avanzato) 🚀
**Descrizione:** Blueprint con contatore cumulativo integrato
**Caratteristiche:**
- ✅ Traccia ore giornaliere
- ✅ Contatore cumulativo per LTS
- ✅ Notifiche push opzionali
- ✅ Friendly device name nei log
- ✅ Reset a mezzanotte
- ✅ Log eventi dettagliati

**Quando usarlo:**
- Con Long Term Statistics (Opzione 2)
- Per notifiche push
- Se vuoi contatore cumulativo integrato

**Helper richiesti:**
1. `input_number` per ore giornaliere
2. `input_number` per contatore cumulativo
3. `input_text` per timestamp accensione

---

## 🐍 Script Avanzati

### **export_heating_history.py** 💾
**Descrizione:** Script Python per esportare storico in CSV
**Caratteristiche:**
- Export dati da Home Assistant API
- Formato CSV con pandas
- Statistiche riassuntive (media, min, max, totale)
- Backup automatico mensile
- Supporto multi-valvola

**Dipendenze:**
```bash
pip install requests pandas
```

**Come usarlo:**
1. Modifica `HA_URL` e `HA_TOKEN` nello script
2. Aggiungi le tue entità in `ENTITIES`
3. Esegui: `python3 export_heating_history.py`
4. Trova CSV in `/config/backups/heating_stats/`

**Automazione Home Assistant:**
```yaml
shell_command:
  export_heating_stats: "python3 /config/scripts/export_heating_history.py"

automation:
  - alias: "Backup Mensile Statistiche"
    trigger:
      - platform: time
        at: "02:00:00"
    condition:
      - condition: template
        value_template: "{{ now().day == 1 }}"
    action:
      - service: shell_command.export_heating_stats
```

---

## 📋 Indice File INDEX.md (questo file)
**Descrizione:** Navigazione tra tutti i file disponibili
**Contiene:**
- Descrizione di ogni file
- Quando e come usarli
- Link rapidi

---

## 🗂️ Struttura Directory

```
blueprints/automation/heating_usage_tracker/
├── README.md                               # 📖 Documentazione completa
├── QUICK_START.md                          # ⚡ Guida rapida 10 minuti
├── ARCHITECTURE.md                         # 🏗️ Architettura tecnica
├── INDEX.md                                # 📁 Questo file
├── configuration_example.yaml              # ⚙️ Configurazione Utility Meter
├── dashboard_example.yaml                  # 📊 Dashboard Lovelace
├── heating_usage_tracker.yaml              # 📋 Blueprint originale
├── heating_usage_tracker_with_history.yaml # 🚀 Blueprint avanzato con LTS
└── export_heating_history.py               # 💾 Script export CSV
```

---

## 🚀 Percorsi Consigliati

### **Per Principianti**
1. Leggi `QUICK_START.md`
2. Copia `configuration_example.yaml`
3. Importa `heating_usage_tracker.yaml` (originale)
4. Usa `dashboard_example.yaml` per visualizzare

### **Per Utenti Avanzati**
1. Leggi `README.md` (sezione completa)
2. Importa `heating_usage_tracker_with_history.yaml`
3. Personalizza dashboard con custom cards
4. Setup script `export_heating_history.py` per backup

### **Per Troubleshooting**
1. Consulta `README.md` → sezione Troubleshooting
2. Leggi `ARCHITECTURE.md` → Data Flow Timeline
3. Verifica log Home Assistant
4. Controlla configurazione recorder

### **Per Capire il Sistema**
1. `ARCHITECTURE.md` → diagrammi e flussi
2. `README.md` → sezione Advanced Configuration
3. `configuration_example.yaml` → commenti inline

---

## 📊 Tabella Comparativa Soluzioni

| Caratteristica | Utility Meter (Originale) | LTS (Avanzato) |
|----------------|---------------------------|----------------|
| File Blueprint | `heating_usage_tracker.yaml` | `heating_usage_tracker_with_history.yaml` |
| Configurazione YAML | `configuration_example.yaml` (richiesta) | Nessuna configurazione extra |
| Helper Richiesti | 3 per stanza | 3 per stanza |
| Storico Automatico | ✅ Illimitato | ✅ Illimitato |
| Reset Automatici | ✅ Daily/Weekly/Monthly/Yearly | ✅ Daily (manual per altri) |
| Notifiche Push | ❌ Richiede modifica | ✅ Integrato |
| Energy Dashboard | ✅ Supportato | ⚠️ Richiede configurazione |
| Facilità Setup | ⭐⭐⭐ Media | ⭐⭐⭐⭐ Facile |
| Flessibilità | ⭐⭐⭐⭐⭐ Massima | ⭐⭐⭐ Buona |

---

## 🔗 Link Rapidi

### Documentazione
- [README Completo](README.md)
- [Quick Start](QUICK_START.md)
- [Architettura](ARCHITECTURE.md)

### Configurazione
- [Esempio Configuration.yaml](configuration_example.yaml)
- [Esempio Dashboard](dashboard_example.yaml)

### Blueprint
- [Blueprint Base](heating_usage_tracker.yaml)
- [Blueprint Avanzato](heating_usage_tracker_with_history.yaml)

### Script
- [Export CSV Python](export_heating_history.py)

---

## 💡 Tips

### Per Multi-Valvola
1. Copia blocco configurazione per ogni stanza
2. Cambia nome: `soggiorno` → `camera`, `bagno`, etc.
3. Crea automazione separata per ogni valvola
4. Usa dashboard multi-valvola in `dashboard_example.yaml`

### Per Grafici Avanzati
- Installa [ApexCharts Card](https://github.com/RomRider/apexcharts-card)
- Installa [Mini Graph Card](https://github.com/kalkih/mini-graph-card)
- Usa template in `dashboard_example.yaml` come base

### Per Backup
1. Usa script `export_heating_history.py`
2. Configura automazione mensile
3. Salva CSV su NAS o cloud

---

## 📞 Supporto

Per problemi o domande:
1. Consulta `README.md` → Troubleshooting
2. Verifica log: Developer Tools → Logs
3. Apri issue su GitHub con:
   - File `configuration.yaml` (redacted)
   - Log errori
   - Versione Home Assistant

---

**Ultima modifica:** 2025-11-06
**Versione:** 2.0.0
