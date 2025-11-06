# 🚀 Quick Start - Statistiche Riscaldamento con Storico

Guida rapida per configurare lo storico delle ore di riscaldamento in 5 minuti.

---

## 📦 Cosa Ti Serve

- ✅ Home Assistant 2024.1+
- ✅ Valvole termostatiche con entità `climate.*`
- ✅ 10 minuti di tempo

---

## 🎯 Opzione Consigliata: Utility Meter

### **Step 1: Crea Helper** (2 minuti)

Vai su **Impostazioni → Dispositivi e Servizi → Helper** e crea per **ogni stanza**:

1. **Input Number** - Nome: `heating_hours_[stanza]`
   - Min: `0`, Max: `24`, Step: `0.01`, Unità: `h`

2. **Input Number** - Nome: `heating_cumulative_[stanza]`
   - Min: `0`, Max: `100000`, Step: `0.01`, Unità: `h`

3. **Input Text** - Nome: `heating_start_[stanza]`
   - Max: `50`

### **Step 2: Configura Utility Meter** (3 minuti)

Aggiungi a `configuration.yaml`:

```yaml
utility_meter:
  heating_daily_soggiorno:
    source: input_number.heating_cumulative_soggiorno
    cycle: daily

  heating_weekly_soggiorno:
    source: input_number.heating_cumulative_soggiorno
    cycle: weekly

  heating_monthly_soggiorno:
    source: input_number.heating_cumulative_soggiorno
    cycle: monthly
```

Riavvia Home Assistant.

### **Step 3: Importa Blueprint** (2 minuti)

1. **Impostazioni → Automazioni → Blueprint → Importa**
2. URL: `https://github.com/darius1907/ha_vmc_helty_flow/blob/main/blueprints/automation/heating_usage_tracker/heating_usage_tracker.yaml`

### **Step 4: Crea Automazione** (3 minuti)

1. **Automazioni → Crea → Usa Blueprint**
2. Seleziona: **🔥 Statistiche Riscaldamento**
3. Configura:
   - Valvola: `climate.termosifone_soggiorno`
   - Contatore giornaliero: `input_number.heating_hours_soggiorno`
   - Contatore cumulativo: `input_number.heating_cumulative_soggiorno`
   - Start time: `input_text.heating_start_soggiorno`
   - Soglia OFF: `5°C`

---

## 📊 Visualizza Dati

### **Metodo 1: Grafici Nativi**

Aggiungi al dashboard:

```yaml
type: statistics-graph
title: Ore Riscaldamento - Ultimi 30 Giorni
entities:
  - sensor.heating_daily_soggiorno
stat_types:
  - state
  - mean
chart_type: bar
period:
  calendar:
    period: month
```

### **Metodo 2: Card Semplice**

```yaml
type: entities
title: Riscaldamento Oggi
entities:
  - entity: input_number.heating_hours_soggiorno
    name: Ore oggi
  - entity: sensor.heating_weekly_soggiorno
    name: Questa settimana
  - entity: sensor.heating_monthly_soggiorno
    name: Questo mese
```

---

## ✅ Verifica Funzionamento

1. Cambia temperatura valvola da **5°C** a **20°C**
2. Attendi 30 secondi
3. Controlla **Logbook**: deve apparire "Riscaldamento acceso"
4. Verifica `input_text.heating_start_soggiorno` abbia un timestamp
5. Cambia temperatura a **5°C**
6. Verifica che `input_number.heating_hours_soggiorno` si aggiorni

---

## 🔧 Troubleshooting

### Problema: Contatore non si aggiorna
- ✅ Verifica che l'automazione sia **attiva**
- ✅ Controlla **Logbook** per eventi
- ✅ Verifica che `input_text` abbia un valore

### Problema: Grafici vuoti
- ✅ Attendi 24h per primo reset
- ✅ Verifica che `recorder` sia configurato
- ✅ Aumenta `purge_keep_days` in `configuration.yaml`:
  ```yaml
  recorder:
    purge_keep_days: 180
  ```

---

## 📚 Documentazione Completa

Per configurazioni avanzate, leggi [README.md](README.md):
- Template sensor per calcoli
- Dashboard completo
- Export CSV
- Multi-valvola
- Notifiche

---

## 🎉 Risultato

Dopo la configurazione avrai:
- ✅ Storico automatico di **3-6+ mesi**
- ✅ Grafici giornalieri, settimanali, mensili
- ✅ Reset automatici a mezzanotte
- ✅ Dati persistenti nel database HA
- ✅ Zero manutenzione richiesta

---

**Tempo totale:** ~10 minuti
**Manutenzione:** 0 minuti/mese
**Storico:** Illimitato (dipende da `purge_keep_days`)
