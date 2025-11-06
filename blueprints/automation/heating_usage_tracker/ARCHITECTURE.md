# 🏗️ Architettura - Heating Usage Tracker

Diagramma dell'architettura del sistema di tracciamento ore riscaldamento.

---

## 📊 Flusso dei Dati

```
┌─────────────────────────────────────────────────────────────────┐
│                    VALVOLA TERMOSTATICA                         │
│                   (climate.termosifone)                         │
│                                                                  │
│  State: temperature = 5°C → 20°C → 5°C                         │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                BLUEPRINT AUTOMATION                              │
│           (heating_usage_tracker.yaml)                          │
│                                                                  │
│  Trigger:                                                       │
│  ├─ State Change: temperature attribute                        │
│  └─ Time: 00:00:00 (midnight)                                  │
│                                                                  │
│  Logic:                                                         │
│  ├─ If temp <= 5°C → OFF                                       │
│  └─ If temp > 5°C → ON                                         │
└────────────┬───────────────┬─────────────────┬──────────────────┘
             │               │                 │
    ┌────────▼────┐  ┌───────▼────────┐  ┌────▼─────────┐
    │ ACCENSIONE  │  │  SPEGNIMENTO    │  │   MIDNIGHT   │
    │             │  │                 │  │   RESET      │
    └─────┬───────┘  └────────┬────────┘  └──────┬───────┘
          │                   │                   │
          ▼                   ▼                   ▼
┌─────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│ input_text      │  │ Calculate Delta  │  │ Log Summary      │
│ heating_start   │  │ (now - start)    │  │ Reset Daily      │
│                 │  │                  │  │ Counter          │
│ Set: now()      │  └─────────┬────────┘  └──────────────────┘
└─────────────────┘            │
                               ▼
                    ┌──────────────────────┐
                    │ Update Counters      │
                    │                      │
                    │ Daily:               │
                    │   += delta           │
                    │                      │
                    │ Cumulative:          │
                    │   += delta           │
                    └──────────┬───────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATA STORAGE                                │
│                                                                  │
│  ┌──────────────────┐  ┌──────────────────┐                    │
│  │ input_number     │  │ input_number     │                    │
│  │ heating_hours    │  │ heating_cumul.   │                    │
│  │                  │  │                  │                    │
│  │ Value: 8.2h      │  │ Value: 245.6h    │                    │
│  │ (today only)     │  │ (total ever)     │                    │
│  └──────────────────┘  └─────────┬────────┘                    │
│                                   │                              │
└───────────────────────────────────┼──────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                    UTILITY METER                                 │
│                  (HA Native Integration)                         │
│                                                                  │
│  Source: input_number.heating_cumulative_soggiorno              │
│                                                                  │
│  Outputs:                                                       │
│  ├─ sensor.heating_daily_soggiorno    (reset 00:00)           │
│  ├─ sensor.heating_weekly_soggiorno   (reset Monday)          │
│  ├─ sensor.heating_monthly_soggiorno  (reset 1st)             │
│  └─ sensor.heating_yearly_soggiorno   (reset Jan 1st)         │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    HA RECORDER                                   │
│                  (Database Storage)                              │
│                                                                  │
│  Tables:                                                        │
│  ├─ states (real-time values)                                  │
│  ├─ statistics (hourly aggregates)                             │
│  └─ statistics_short_term (5-min aggregates)                   │
│                                                                  │
│  Retention: purge_keep_days = 180 (6 months)                   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    VISUALIZATION                                 │
│                  (Lovelace Dashboard)                            │
│                                                                  │
│  Cards:                                                         │
│  ├─ statistics-graph (daily/monthly/yearly)                    │
│  ├─ history-graph (real-time)                                  │
│  ├─ entities (current values)                                  │
│  └─ custom cards (apexcharts, mini-graph)                      │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Ciclo di Vita dei Dati

### **1. Accensione Riscaldamento**
```
┌─────────────┐      ┌────────────────┐      ┌─────────────────┐
│ Temp: 5→20°C│──────▶│ Trigger: State │──────▶│ Save Timestamp │
└─────────────┘      │ Change         │      │ in input_text   │
                     └────────────────┘      └─────────────────┘
```

### **2. Spegnimento Riscaldamento**
```
┌─────────────┐      ┌────────────────┐      ┌─────────────────┐
│ Temp: 20→5°C│──────▶│ Calculate      │──────▶│ Update Counters │
└─────────────┘      │ Delta (h)      │      │ Daily + Cumul.  │
                     └────────────────┘      └─────────────────┘
```

### **3. Reset Giornaliero (Mezzanotte)**
```
┌─────────────┐      ┌────────────────┐      ┌─────────────────┐
│ Time: 00:00 │──────▶│ Log Summary    │──────▶│ Reset Daily     │
└─────────────┘      │ (today's hours)│      │ Counter to 0    │
                     └────────────────┘      └─────────────────┘
```

### **4. Utility Meter (Automatico)**
```
┌─────────────┐      ┌────────────────┐      ┌─────────────────┐
│ Daily Reset │──────▶│ Weekly Reset   │──────▶│ Monthly Reset   │
│ 00:00       │      │ Monday 00:00   │      │ 1st 00:00       │
└─────────────┘      └────────────────┘      └─────────────────┘
```

---

## 🗄️ Schema Database

### **Helper Entities**

| Entity | Type | Purpose | Persistence |
|--------|------|---------|-------------|
| `input_number.heating_hours_soggiorno` | Helper | Ore giornaliere | State only (reset daily) |
| `input_number.heating_cumulative_soggiorno` | Helper | Contatore cumulativo | State + History |
| `input_text.heating_start_soggiorno` | Helper | Timestamp accensione | State only |

### **Utility Meter Sensors**

| Entity | Cycle | Reset | Storage |
|--------|-------|-------|---------|
| `sensor.heating_daily_soggiorno` | daily | 00:00 | Statistics table |
| `sensor.heating_weekly_soggiorno` | weekly | Monday 00:00 | Statistics table |
| `sensor.heating_monthly_soggiorno` | monthly | 1st 00:00 | Statistics table |
| `sensor.heating_yearly_soggiorno` | yearly | Jan 1st 00:00 | Statistics table |

### **Recorder Tables**

```sql
-- States table (real-time values)
CREATE TABLE states (
    entity_id VARCHAR(255),
    state TEXT,
    last_changed TIMESTAMP,
    last_updated TIMESTAMP,
    -- Real-time current state
);

-- Statistics table (long-term data)
CREATE TABLE statistics (
    entity_id VARCHAR(255),
    start TIMESTAMP,
    mean FLOAT,
    min FLOAT,
    max FLOAT,
    sum FLOAT,
    -- Hourly/Daily aggregates for history
);
```

---

## 📈 Retention Policy

### **Default Configuration**

```yaml
recorder:
  purge_keep_days: 10  # ❌ Too short for heating stats

  # Only 10 days of data - insufficient for seasonal analysis
```

### **Recommended Configuration**

```yaml
recorder:
  purge_keep_days: 180  # ✅ 6 months history

  # Include heating entities explicitly
  include:
    entities:
      - input_number.heating_hours_soggiorno
      - input_number.heating_cumulative_soggiorno
      - sensor.heating_daily_soggiorno
      - sensor.heating_weekly_soggiorno
      - sensor.heating_monthly_soggiorno
```

### **Advanced Configuration**

```yaml
recorder:
  purge_keep_days: 30  # Keep detailed data for 1 month

  # But keep statistics forever
  commit_interval: 1

  # Exclude unnecessary attributes
  exclude:
    entity_globs:
      - sensor.heating_*
    attributes:
      - attribution
      - device_class

# Long-term statistics (separate from states)
# Statistics are kept indefinitely by default
```

---

## 🔄 Data Flow Timeline

```
Day 1:
├─ 08:00 → Accensione (temp 5→20°C)
│          └─ input_text.heating_start = "2025-11-06 08:00:00"
│
├─ 18:00 → Spegnimento (temp 20→5°C)
│          ├─ Delta = 10h
│          ├─ input_number.heating_hours = 10h
│          └─ input_number.heating_cumulative = 10h
│
└─ 00:00 → Reset Giornaliero
           ├─ Log: "Totale ieri: 10h"
           ├─ input_number.heating_hours = 0
           └─ sensor.heating_daily = 10h (stored in statistics)

Day 2:
├─ 07:00 → Accensione
├─ 19:00 → Spegnimento (12h)
│          └─ input_number.heating_cumulative = 22h (10+12)
└─ 00:00 → Reset
           └─ sensor.heating_daily = 12h

Day 7 (Monday):
└─ 00:00 → Weekly Reset
           └─ sensor.heating_weekly = 70h

Day 30:
└─ 00:00 → Monthly Reset
           └─ sensor.heating_monthly = 245h
```

---

## 🎯 Performance Considerations

### **Database Impact**

| Entity | Update Frequency | Storage Impact |
|--------|-----------------|----------------|
| `input_number.heating_hours` | On valve state change (~2-10x/day) | Low (state only) |
| `input_number.heating_cumulative` | On valve state change (~2-10x/day) | Medium (state + history) |
| `sensor.heating_daily` | Daily (1x/day) | Low (statistics) |
| `sensor.heating_monthly` | Monthly (1x/month) | Very Low |

### **Optimization Tips**

1. **Exclude Attributes**: Don't store unnecessary attributes
   ```yaml
   recorder:
     exclude:
       entity_globs:
         - sensor.heating_*
       attributes:
         - icon
         - friendly_name
   ```

2. **Commit Interval**: Increase for less frequent writes
   ```yaml
   recorder:
     commit_interval: 5  # Default is 1 second
   ```

3. **Use Statistics**: For long-term data, statistics are more efficient than states
   - States: ~100 bytes per record
   - Statistics: ~50 bytes per hour

---

## 🔐 Data Security

### **Backup Strategy**

```yaml
# Automatic backup script (weekly)
shell_command:
  backup_heating_stats: >
    python3 /config/scripts/export_heating_history.py &&
    cp /config/backups/heating_stats/*.csv /backup/external/
```

### **Restore Procedure**

1. Restore Home Assistant backup
2. Import CSV files
3. Recreate helper entities
4. Re-import blueprint
5. Verify data in statistics

---

**Aggiornato:** 2025-11-06
**Versione:** 2.0.0
