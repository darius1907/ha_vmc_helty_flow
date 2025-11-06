# 🔥 Heating Usage Tracker - Statistiche Riscaldamento con Storico

Blueprint avanzato per Home Assistant che traccia le ore di riscaldamento giornaliere delle valvole termostatiche e mantiene uno **storico consultabile di 3-6 mesi** (o più).

---

## 📋 Indice

1. [Caratteristiche](#caratteristiche)
2. [Soluzioni Disponibili](#soluzioni-disponibili)
3. [Setup Rapido](#setup-rapido)
4. [Configurazione Avanzata](#configurazione-avanzata)
5. [Dashboard e Grafici](#dashboard-e-grafici)
6. [Troubleshooting](#troubleshooting)

---

## ✨ Caratteristiche

- ✅ **Tracciamento automatico** delle ore di riscaldamento
- ✅ **Storico a lungo termine** (3-6+ mesi)
- ✅ **Grafici nativi** di Home Assistant
- ✅ **Statistiche giornaliere, settimanali, mensili, annuali**
- ✅ **Calcolo costi energetici**
- ✅ **Notifiche opzionali** (accensione/spegnimento)
- ✅ **Multi-valvola** (configura per ogni termosifone)
- ✅ **Zero dipendenze custom**

---

## 🎯 Soluzioni Disponibili

### **Opzione 1: Utility Meter (CONSIGLIATA) ⭐**

**File:** `configuration_example.yaml`

**Vantaggi:**
- ✅ Storico automatico illimitato
- ✅ Reset automatici (daily/weekly/monthly/yearly)
- ✅ Nessun blueprint custom necessario
- ✅ Integrazione nativa con Energy Dashboard

**Configurazione:**
1. Copia il contenuto di `configuration_example.yaml`
2. Incollalo in `configuration.yaml` o in `packages/heating_stats.yaml`
3. Riavvia Home Assistant
4. Configura il blueprint originale (`heating_usage_tracker.yaml`)

---

### **Opzione 2: Blueprint con LTS (Long Term Statistics)**

**File:** `heating_usage_tracker_with_history.yaml`

**Vantaggi:**
- ✅ Storico persistente nel database HA
- ✅ Contatore cumulativo integrato
- ✅ Notifiche push opzionali
- ✅ Nessuna configurazione YAML aggiuntiva

**Configurazione:**
1. Importa il blueprint `heating_usage_tracker_with_history.yaml`
2. Crea 3 helper per ogni valvola:
   - `input_number` per ore giornaliere
   - `input_number` per contatore cumulativo
   - `input_text` per timestamp accensione
3. Configura l'automazione dal blueprint

---

## 🚀 Setup Rapido

### **Prerequisiti**

1. **Home Assistant** versione 2024.1+ (richiesta per utility_meter)
2. **Valvole termostatiche** con entità `climate.*`
3. **Helper** da creare nell'interfaccia

### **Step 1: Crea Helper**

Vai su **Impostazioni → Dispositivi e Servizi → Helper** e crea:

#### Per ogni valvola:

1. **Input Number - Ore Giornaliere**
   - Nome: `Ore Riscaldamento [Stanza]`
   - Min: `0`
   - Max: `24`
   - Step: `0.01`
   - Unità: `h`
   - Icona: `mdi:radiator`

2. **Input Number - Contatore Cumulativo** (solo se usi Opzione 1)
   - Nome: `Ore Riscaldamento [Stanza] - Cumulativo`
   - Min: `0`
   - Max: `100000`
   - Step: `0.01`
   - Unità: `h`
   - Icona: `mdi:counter`

3. **Input Text - Timestamp Accensione**
   - Nome: `Riscaldamento [Stanza] - Ultimo Avvio`
   - Max Length: `50`
   - Icona: `mdi:clock-start`

### **Step 2: Configura Utility Meter** (Opzione 1)

Aggiungi a `configuration.yaml`:

```yaml
utility_meter:
  heating_daily_soggiorno:
    source: input_number.heating_cumulative_soggiorno
    cycle: daily

  heating_monthly_soggiorno:
    source: input_number.heating_cumulative_soggiorno
    cycle: monthly
```

Riavvia Home Assistant.

### **Step 3: Importa Blueprint**

1. Vai su **Impostazioni → Automazioni e Scene → Blueprint**
2. Click **Importa Blueprint**
3. URL: `https://github.com/darius1907/ha_vmc_helty_flow/blob/main/blueprints/automation/heating_usage_tracker/heating_usage_tracker.yaml`

### **Step 4: Crea Automazione**

1. Vai su **Automazioni → Crea Automazione → Usa Blueprint**
2. Seleziona: **🔥 Statistiche Riscaldamento**
3. Configura:
   - **Valvola Termostatica**: `climate.termosifone_soggiorno`
   - **Contatore Ore**: `input_number.heating_hours_soggiorno`
   - **Start Time**: `input_text.heating_start_soggiorno`
   - **Soglia OFF**: `5°C` (default)
4. Salva con nome: `Heating Tracker - Soggiorno`

### **Step 5: Verifica**

1. Cambia manualmente la temperatura sulla valvola da `5°C` a `20°C`
2. Attendi qualche secondo
3. Controlla il logbook per confermare l'accensione
4. Verifica che `input_text.heating_start_soggiorno` abbia un timestamp

---

## 📊 Configurazione Avanzata

### **Template Sensor per Calcoli**

Aggiungi a `configuration.yaml`:

```yaml
sensor:
  - platform: template
    sensors:
      # Costo energetico (€0.30/kWh)
      heating_cost_daily_soggiorno:
        friendly_name: "Costo Riscaldamento Oggi"
        unit_of_measurement: "€"
        value_template: >
          {{ (states('sensor.heating_daily_soggiorno') | float(0) * 0.30) | round(2) }}

      # Media ore giornaliere
      heating_avg_daily_soggiorno:
        friendly_name: "Media Giornaliera"
        unit_of_measurement: "h"
        value_template: >
          {% set monthly = states('sensor.heating_monthly_soggiorno') | float(0) %}
          {% set days = now().day %}
          {{ (monthly / days) | round(1) if days > 0 else 0 }}
```

### **Notifiche Telegram/Discord**

Modifica il blueprint per inviare notifiche:

```yaml
- service: notify.telegram
  data:
    message: >
      🔥 Riscaldamento {{ device_name }} acceso alle {{ now().strftime('%H:%M') }}
```

### **Integrazione con Energy Dashboard**

Configura utility_meter con `tariffs` per tariffe bi-orarie:

```yaml
utility_meter:
  heating_daily_soggiorno:
    source: input_number.heating_cumulative_soggiorno
    cycle: daily
    tariffs:
      - peak
      - off_peak
```

---

## 📈 Dashboard e Grafici

### **Importa Dashboard Esempio**

Copia il contenuto di `dashboard_example.yaml` in una nuova vista Lovelace.

### **Grafici Disponibili**

1. **Riepilogo Oggi**: Ore attuali + percentuale utilizzo
2. **Storico 7 Giorni**: Grafico a barre
3. **Storico 3 Mesi**: Grafico a linee con media
4. **Confronto Multi-Valvola**: Tutte le stanze
5. **Costi Mensili**: Grafico spesa energetica
6. **Tabella Dettagliata**: Logbook eventi

### **Custom Cards Consigliate** (opzionali)

- [ApexCharts Card](https://github.com/RomRider/apexcharts-card): Grafici avanzati
- [Mini Graph Card](https://github.com/kalkih/mini-graph-card): Grafici compatti
- [Auto Entities](https://github.com/thomasloven/lovelace-auto-entities): Liste dinamiche

---

## 🔧 Troubleshooting

### **Problema: Contatore non si aggiorna**

**Soluzione:**
1. Verifica che la temperatura impostata sulla valvola cambi correttamente
2. Controlla il logbook per eventi di accensione/spegnimento
3. Verifica che `input_text.heating_start_soggiorno` contenga un timestamp valido
4. Attiva debug logging:
   ```yaml
   logger:
     default: info
     logs:
       homeassistant.components.automation: debug
   ```

### **Problema: Utility Meter non crea sensor**

**Soluzione:**
1. Verifica sintassi YAML con [YAML Lint](http://www.yamllint.com/)
2. Controlla che il `source` esista: `input_number.heating_cumulative_*`
3. Riavvia Home Assistant dopo modifiche a `configuration.yaml`
4. Controlla log errori: **Developer Tools → Logs**

### **Problema: Storico non si visualizza**

**Soluzione:**
1. Attendi 24-48h per il primo reset del utility_meter
2. Verifica che il database recorder sia configurato correttamente:
   ```yaml
   recorder:
     purge_keep_days: 180  # Mantiene storico 6 mesi
   ```
3. Controlla che le entità siano incluse nel recorder (non escluse)

### **Problema: Reset non avviene a mezzanotte**

**Soluzione:**
1. Verifica timezone di Home Assistant: **Impostazioni → Sistema → Generale**
2. Controlla che il trigger `at: "00:00:00"` sia corretto
3. Usa `cron` per orari personalizzati:
   ```yaml
   trigger:
     - platform: time
       at: "00:00:00"
   ```

### **Problema: Valori errati dopo riavvio HA**

**Soluzione:**
1. Gli `input_number` mantengono lo stato dopo riavvio ✅
2. Se il riscaldamento era acceso durante il riavvio, potrebbe perdere il timestamp
3. Aggiungi automazione di recovery:
   ```yaml
   - alias: "Heating Tracker Recovery"
     trigger:
       - platform: homeassistant
         event: start
     action:
       - service: input_text.set_value
         data:
           entity_id: input_text.heating_start_soggiorno
           value: ""
   ```

---

## 📊 Esempi di Statistiche

### **Dati Esempio dopo 3 Mesi**

| Stanza | Oggi | Settimana | Mese | 3 Mesi | Costo (€0.30/kWh) |
|--------|------|-----------|------|--------|-------------------|
| Soggiorno | 8.2h | 56h | 245h | 720h | €216 |
| Camera | 6.5h | 45h | 198h | 580h | €174 |
| Bagno | 2.1h | 15h | 68h | 190h | €57 |

### **Query SQL per Analisi Avanzate**

```sql
SELECT
  DATE(created) as date,
  SUM(state) as total_hours
FROM states
WHERE entity_id = 'sensor.heating_daily_soggiorno'
  AND created >= DATE('now', '-90 days')
GROUP BY DATE(created)
ORDER BY date DESC;
```

---

## 🔗 Risorse Utili

- [Home Assistant Utility Meter](https://www.home-assistant.io/integrations/utility_meter/)
- [Home Assistant Statistics](https://www.home-assistant.io/integrations/statistics/)
- [Recorder Integration](https://www.home-assistant.io/integrations/recorder/)
- [Energy Dashboard](https://www.home-assistant.io/docs/energy/)

---

## 📝 Changelog

### v2.0.0 (2025-11-06)
- ✨ Aggiunto supporto storico lungo termine (3-6+ mesi)
- ✨ Integrazione Utility Meter
- ✨ Blueprint con LTS (Long Term Statistics)
- ✨ Dashboard esempio completo
- ✨ Template sensor per calcoli avanzati
- 📚 Documentazione completa

### v1.0.0
- 🎉 Release iniziale
- ✅ Tracciamento ore giornaliere
- ✅ Reset mezzanotte
- ✅ Log eventi

---

## 🤝 Contributi

Per segnalare bug o suggerire miglioramenti, apri una issue su GitHub.

---

## 📄 Licenza

MIT License - Vedi [LICENSE](../../../LICENSE)
