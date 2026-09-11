# 🗺️ VMC Helty Flow - Roadmap Operativa

> **Piano di sviluppo** con task tracciabili, milestone e criteri di completamento
> **Versione**: 1.0
> **Data inizio**: 2026-03-23
> **Ultima revisione**: 2026-09-11 (v1.2.1 rilasciato 2026-09-11 — patch di bugfix per affidabilità comunicazione TCP)

---

## 📊 Dashboard Progressi

### Stato Generale Progetto
```
Versione Corrente: v1.2.1 ✅
Prossimo Release: v1.3.0 📋
Quality Scale: Silver ⭐⭐
Test Coverage: 84% ✅ (gate: 65%)
Tech Debt: 2 item ⚠️ (SENS-009: monitoraggio energia reale; debug logging in produzione)
```

### Milestone Overview
| Milestone | Stato | Data Target | Completamento |
|-----------|-------|-------------|---------------|
| v1.1.1 | ✅ Completed | 2026-03-26 | ▓▓▓▓▓▓▓▓▓▓ 100% |
| v1.2.0 | ✅ Completed | 2026-03-30 | ▓▓▓▓▓▓▓▓▓▓ 100% |
| v1.2.1 | ✅ Completed (patch, non pianificata) | 2026-09-11 | ▓▓▓▓▓▓▓▓▓▓ 100% |
| v1.3.0 | 📋 Planned | 2026-08-15 | ░░░░░░░░░░ 0% |
| v1.4.0 | 📋 Planned | 2026-11-15 | ░░░░░░░░░░ 0% |
| v1.5.0 | 📋 Planned | 2027-02-15 | ░░░░░░░░░░ 0% |

---

## 🎯 Milestone 1: v1.1.1 (Target: 2026-03-26)

**Obiettivo**: Rilascio beta con nuovi blueprint e sensori base per feedback community

### Sprint 1.1: Blueprint e Testing (1-2 settimane)
**Owner**: Development Team
**Start**: 2026-03-23
**End**: 2026-04-06

#### Task Checklist

##### 1. Blueprint Testing e Refinement
- [x] **BLU-001**: Test completo `vmc_air_quality_adaptive.yaml`
  - [x] Test con sensore CO2 integrato VMC
  - [x] Test con sensore CO2 esterno (Netatmo/ESPHome)
  - [x] Test logic hyperventilation mode
  - [x] Test delay anti-oscillazione
  - [x] Validate YAML syntax
  - [x] **Criteri successo**: 10 test run senza errori, 5 cicli CO2 alto→basso
  - **Effort**: 3h ✅ **COMPLETATO 2026-03-26**
  - **Priority**: 🔴 Alta

- [x] **BLU-002**: Test completo `vmc_humidity_control.yaml`
  - [x] Test boost doccia (70% → 100% speed)
  - [x] Test durata minima garantita
  - [x] Test estensione boost se umidità alta
  - [x] Test cooldown tra boost
  - [x] Test blackout notturno
  - [x] Test notifiche mobile/persistent
  - [x] **Criteri successo**: 5 cicli doccia simulati correttamente
  - **Effort**: 3h ✅ **COMPLETATO 2026-03-26**
  - **Priority**: 🔴 Alta

- [x] **BLU-003**: Test completo `vmc_filter_reminder.yaml`
  - [x] Test notifica avviso 90% (~15970h su 17744h)
  - [x] Test notifica critica 95% (~16857h su 17744h)
  - [x] Test promemoria giornaliero 100%
  - [x] Test persistent notification
  - [x] Test mobile notification con action buttons
  - [x] Test email notification
  - [x] **Criteri successo**: Tutte le notifiche arrivano nei canali configurati
  - **Effort**: 2h ✅ **COMPLETATO 2026-03-26**
  - **Priority**: 🟡 Media

- [x] **BLU-004**: Fix bug e improvement da testing
  - [x] Fix eventuali errori sintassi YAML
  - [x] Ottimizza logica condition
  - [x] Migliora messaggi notifica
  - [x] Aggiungi validation input
  - **Effort**: 4h ✅ **COMPLETATO 2026-03-26**
  - **Priority**: 🔴 Alta
  - **Dipendenze**: BLU-001, BLU-002, BLU-003

##### 2. Documentation Blueprint
- [x] **DOC-001**: Aggiorna `blueprints/README.md`
  - [x] Aggiungi badge import per nuovi blueprint
  - [x] Documenta prerequisiti
  - [x] Aggiungi esempi configurazione
  - **Effort**: 2h ✅ **COMPLETATO 2026-03-26**
  - **Priority**: 🟡 Media

- [x] **DOC-002**: Review `blueprints/BLUEPRINT_GUIDE.md`
  - [x] Verifica esempi pratici accurati
  - [x] Aggiungi screenshot (opzionale)
  - [x] Proof-reading italiano
  - **Effort**: 2h ✅ **COMPLETATO 2026-03-26**
  - **Priority**: 🟡 Media

- [x] **DOC-003**: Traduci guida in inglese
  - [x] Crea `blueprints/BLUEPRINT_GUIDE_EN.md`
  - [x] Traduzioni accurate esempi
  - **Effort**: 4h ✅ **COMPLETATO 2026-03-26**
  - **Priority**: 🟢 Bassa

##### 3. Code Quality
- [x] **QA-001**: Run linters su blueprint files
  - [x] yamllint su tutti i .yaml
  - [x] Fix warning/errors
  - **Effort**: 1h ✅ **COMPLETATO 2026-03-26**
  - **Priority**: 🔴 Alta

- [x] **QA-002**: Peer review blueprint code
  - [x] Review logic automazioni
  - [x] Review best practices HA
  - [x] Security check (no credentials hardcoded)
  - **Effort**: 2h
  - **Priority**: 🟡 Media

**Sprint 1.1 Total Effort**: ~23 ore
**Deliverable**: 3 blueprint testati e documentati

---

### Sprint 1.2: Sensori Nuovi (1 settimana)
**Owner**: Development Team
**Start**: 2026-04-07
**End**: 2026-04-13

#### Task Checklist

##### 4. Sensori Statistici
- [x] **SENS-001**: Implementa `VmcHeltyFilterLifePercentageSensor`
  - [x] Crea classe in `sensor.py`
  - [x] Calcolo: `(MAX_HOURS - current_hours) / MAX_HOURS * 100`
  - [x] Unit: percentage, state_class: measurement
  - [x] Icon: mdi:air-filter
  - [x] Unique ID: `{name_slug}_filter_life_percentage`
  - [x] **Criteri successo**: Sensore mostra 100% con filtro nuovo, 0% a 17744h
  - **Effort**: 2h ✅ **COMPLETATO 2026-03-23**
  - **Priority**: 🔴 Alta
  - **Test**: 12/12 passed, Coverage sensor.py: 43%

- [x] **SENS-002**: Implementa `VmcHeltyDailyEnergyEstimateSensor` ⚠️ **DA MIGLIORARE**
  - [x] Crea classe in `sensor.py`
  - [x] Mappa velocità → potenza (W): {0:0, 1:10, 2:20, 3:35, 4:50}
  - [x] Calcola Wh basato su pattern utilizzo giornaliero tipico
  - [x] Device class: energy, unit: Wh
  - [x] State class: total
  - [x] **Criteri successo**: Stima realistica energia giornaliera
  - **Effort**: 3h ✅ **COMPLETATO 2026-03-23**
  - **Priority**: 🟡 Media
  - **Test**: 18/18 passed, Include calcolo costi e proiezioni
  - **⚠️ NOTA**: Pattern fisso poco realistico, necessita monitoraggio velocità reale
  - **→ Vedi SENS-009 per miglioramento**

- [x] **SENS-003**: Implementa `VmcHeltyPowerSensor` (istantaneo)
  - [x] Crea classe in `sensor.py`
  - [x] Potenza istantanea basata su velocità corrente
  - [x] Device class: power, unit: W
  - [x] State class: measurement
  - [x] **Criteri successo**: Valore aggiorna in real-time con cambio velocità
  - **Effort**: 1h ✅ **COMPLETATO 2026-03-23**
  - **Priority**: 🟡 Media
  - **Test**: 18/18 passed, Include efficiency metrics

- [ ] **SENS-004**: Implementa `VmcHeltyRunningTimeSensor` *(spostato a Milestone 3 / Sprint 3.1)*

- [ ] **SENS-009**: Migliora `VmcHeltyDailyEnergyEstimateSensor` (v1.3.0)
  - [ ] Rimuovi pattern fisso poco realistico
  - [ ] Implementa monitoraggio velocità reale con timestamp
  - [ ] Accumula Wh basato su tempo effettivo a ogni velocità
  - [ ] Persistent storage per stato tra restart
  - [ ] Reset automatico a mezzanotte
  - [ ] Calcolo: somma(potenza_velocità * tempo_a_velocità)
  - [ ] **Criteri successo**: Energia calcolata su utilizzo reale misurato
  - **Effort**: 4h
  - **Priority**: 🔴 Alta (Miglioramento)
  - **Dipendenze**: SENS-002 (sostituisce logica pattern)

##### 5. Binary Sensors Alerting
- [x] **SENS-005**: Implementa `VmcHeltyFilterWarningBinarySensor` *(completato, in Milestone 2 / Sprint 2.1)*

- [x] **SENS-006**: Implementa `VmcHeltyAirQualityAlertBinarySensor`
  - [x] ON quando CO2 > 1000 ppm per 5+ minuti
  - [x] Device class: problem
  - [x] Icon: mdi:molecule-co2
  - [x] **Criteri successo**: Alert tempestivo quando aria scadente
  - **Effort**: 1h ✅ **COMPLETATO 2026-03-26**
  - **Priority**: 🟡 Media

- [x] **SENS-007**: Implementa `VmcHeltyCondensationRiskBinarySensor`
  - [x] ON quando dew_point_delta < 2°C
  - [x] Device class: problem
  - [x] Icon: mdi:water-alert
  - [x] **Criteri successo**: Alert quando rischio condensazione
  - **Effort**: 1h ✅ **COMPLETATO 2026-03-26**
  - **Priority**: 🟡 Media

- [x] **SENS-008**: Implementa `VmcHeltyOfflineBinarySensor`
  - [x] ON quando coordinator.last_update_success = False
  - [x] Device class: connectivity
  - [x] Icon: mdi:wifi-alert
  - [x] **Criteri successo**: Alert immediato se VMC offline
  - **Effort**: 1h ✅ **COMPLETATO 2026-03-26**
  - **Priority**: 🟢 Bassa

##### 6. Testing Sensori
- [x] **TEST-001**: Unit test nuovi sensori
  - [x] Test filter life percentage calculation
  - [x] Test energy calculation accuracy
  - [x] Test binary sensor triggers
  - [x] Coverage >95% su nuovo codice
  - **Effort**: 4h ✅ **COMPLETATO 2026-03-26**
  - **Priority**: 🔴 Alta
  - **Dipendenze**: SENS-001 → SENS-008

- [x] **TEST-002**: Integration test sensori
  - [x] Test sensori appaiono in entity registry
  - [x] Test device info corretto
  - [x] Test state persistence
  - **Effort**: 2h ✅ **COMPLETATO 2026-03-26**
  - **Priority**: 🔴 Alta

**Sprint 1.2 Total Effort**: ~15 ore
**Deliverable**: Sensori rimanenti per beta + test di integrazione

---

### Sprint 1.3: Quality & Release Beta (3 giorni)
**Owner**: Development Team
**Start**: 2026-04-14
**End**: 2026-04-15

#### Task Checklist

##### 7. Code Quality & Testing
- [x] **QA-003**: Run full test suite
  - [x] `pytest tests/ -v --cov`
  - [x] Verify coverage gate configurata (`>=65%`) soddisfatta
  - [x] Fix failing tests
  - **Effort**: 2h ✅ **COMPLETATO 2026-03-26**
  - **Priority**: 🔴 Alta

- [x] **QA-004**: Run linters
  - [x] `pylint custom_components/vmc_helty_flow/`
  - [x] `mypy custom_components/vmc_helty_flow/`
  - [x] Fix issues rating >9.5/10
  - **Effort**: 2h ✅ **COMPLETATO 2026-03-26**
  - **Priority**: 🔴 Alta

- [x] **QA-005**: Run pre-commit hooks
  - [x] `pre-commit run --all-files`
  - [x] Fix formatting/lint issues
  - **Effort**: 1h ✅ **COMPLETATO 2026-03-26**
  - **Priority**: 🔴 Alta

##### 8. Documentation
- [x] **DOC-004**: Aggiorna `CHANGELOG.md`
  - [x] Sezione `[1.1.1]` con tutte le novità
  - [x] Link a blueprint e sensori
  - [x] Breaking changes (se presenti)
  - **Effort**: 1h ✅ **COMPLETATO 2026-03-26**
  - **Priority**: 🔴 Alta

- [x] **DOC-005**: Aggiorna `README.md` principale
  - [x] Sezione blueprint con link
  - [x] Lista sensori aggiornata
  - [x] Badge versione v1.1.1
  - **Effort**: 1h ✅ **COMPLETATO 2026-03-26**
  - **Priority**: 🟡 Media

- [x] **DOC-006**: Aggiorna `manifest.json`
  - [x] Version: "1.1.1"
  - [x] Quality scale verificato (Silver)
  - **Effort**: 10min ✅ **COMPLETATO 2026-03-26**
  - **Priority**: 🔴 Alta

##### 9. Git & Release
- [x] **REL-001**: Commit e push modifiche
  - [x] Branch: `improvements-v1.2.0`
  - [x] Commit message conventional format
  - [x] Push to origin + github
  - **Effort**: 30min ✅ **COMPLETATO 2026-03-26**
  - **Priority**: 🔴 Alta

- [x] **REL-002**: Create Pull Request
  - [x] PR to main con descrizione dettagliata
  - [x] Checklist completamento
  - [x] Request review
  - **Effort**: 30min ✅ **COMPLETATO 2026-03-26**
  - **Priority**: 🔴 Alta

- [x] **REL-003**: Tag release beta
  - [x] `git tag v1.1.1`
  - [x] Annotated tag con release notes
  - [x] Push tag a remotes
  - **Effort**: 15min ✅ **COMPLETATO 2026-03-26**
  - **Priority**: 🔴 Alta

- [x] **REL-004**: GitHub Release draft
  - [x] Crea release v1.1.1
  - [x] "Pre-release" flag abilitato
  - [x] Release notes da CHANGELOG
  - [x] Richiesta beta testers
  - **Effort**: 1h ✅ **COMPLETATO 2026-03-26**
  - **Priority**: 🔴 Alta

**Sprint 1.3 Total Effort**: ~9 ore
**Deliverable**: v1.1.1 released su GitHub

---

## 🎯 Milestone 2: v1.2.0 (Target: 2026-05-15)

**Obiettivo**: Sensori evoluti configurabili con sorgenti dati esterne (EASC — External Advanced Sensor Configuration)

### 📋 Feature Principale: External Advanced Sensor Configuration (EASC)

#### Overview
Sistema che permette ai sensori evoluti di utilizzare fonti dati esterne (sensori HA, ESPHome, Zigbee) al posto dei sensori VMC interni, con fallback automatico a dati VMC.

#### Analisi Sensori Evoluti Attualmente Implementati

**Sensori che usano Temperatura + Umidità (da VMGI response):**
```
┌─────────────────────────────────────────────────────────────┐
│ SENSORE                          │ INPUT DA VMC    │ FORMULA │
├─────────────────────────────────┼─────────────────┼─────────┤
│ VmcHeltyAbsoluteHumiditySensor  │ T_int, Humidity │ Magnus  │
│ VmcHeltyDewPointSensor           │ T_int, Humidity │ Magnus  │
│ VmcHeltyComfortIndexSensor       │ T_int, Humidity │ ASHRAE  │
│ VmcHeltyDewPointDeltaSensor      │ T_int, T_ext,   │ Magnus  │
│                                   │ Humidity        │         │
└─────────────────────────────────────────────────────────────┘

Source Data: VMGI response, positions [1], [2], [3]
- Position 1: Temperatura interna (°C * 10)
- Position 2: Temperatura esterna (°C * 10)
- Position 3: Umidità relativa (% * 10)
```

**Sensori che usano Fan Speed + Volume ambiente (da VMGO response):**
```
┌─────────────────────────────────────────────────────────────┐
│ SENSORE                          │ INPUT          │ FORMULA │
├─────────────────────────────────┼────────────────┼─────────┤
│ VmcHeltyAirExchangeTimeSensor    │ Fan Speed,     │ V/Q*60  │
│ VmcHeltyDailyAirChangesSensor    │ Room Volume    │ (Q/V)*24│
└─────────────────────────────────────────────────────────────┘

Source Data: VMGO response position [1], Room Volume from config
- Position 1: Fan speed (0-7) → AIRFLOW_MAPPING → m³/h
- Room Volume: Configurabile per stanza (default 60 m³)
```

**Sensori base (non evoluti) che usano CO2 + VOC (da VMGI response):**
```
┌─────────────────────────────────────────────────────────────┐
│ SENSORE (base)                   │ INPUT          │ SOURCE  │
├─────────────────────────────────┼────────────────┼─────────┤
│ VmcHeltySensor(type="co2")       │ CO2 ppm        │ VMGI[4] │
│ VmcHeltySensor(type="voc")       │ VOC level      │ VMGI[11]│
└─────────────────────────────────────────────────────────────┘

NOTA: CO2 e VOC sono attualmente usati solo in sensori base.
Future opportunity: VOC-based adaptive ventilation control
```

#### Requisiti Feature EASC

**R1: Configurabilità Source Dati**
- Per ogni sensore evoluto, permettere override della fonte dati
- Supportare: VMC (default), entity_id generico, const value, formula custom
- Fallback automatico se source esterno non disponibile

**R2: Mapping Sensori Esterni**
- Temperature sensor (interno): `climate.*` o `sensor.*temperature*`
- Temperature sensor (esterno): `weather.*` o custom `sensor.*outdoor*`
- Humidity sensor: `sensor.*humidity*`
- VOC sensor: `sensor.*voc*` o custom
- CO2 sensor: `sensor.*co2*` o custom
- Fan speed: `fan.*` entity

**R3: Validazione e Conversioni**
- Auto-detect unità di misura (°C vs °F)
- Conversione da diversi formati (10⁻¹ per VMC → numeri normali)
- Type checking (string → float/int)
- Range validation (es. 0-100% per humidity)

**R4: Persistenza Configurazione**
- Salva mapping nel `config_entry.options`
- Allow update via config flow dialog
- Migrate legacy configs automaticamente

**R5: Diagnostics & Debugging**
- Log quale source è usato per ogni calcolo
- Timestamp ultimo dato valido da fonte esterna
- Fallback reason se fonte esterna fallisce

#### Architecture EASC

```yaml
# config_entry.options schema
easc_config:
  advanced_sensors:
    absolute_humidity:
      enabled: true
      temperature_source: "sensor.living_room_temp"  # default: use VMC
      humidity_source: "sensor.living_room_humidity"  # default: use VMC
      formula: "magnus"  # default
    dew_point:
      enabled: true
      temperature_source: "sensor.living_room_temp"
      humidity_source: "sensor.living_room_humidity"
    comfort_index:
      enabled: true
      temperature_source: "sensor.living_room_temp"
      humidity_source: "sensor.living_room_humidity"
    dew_point_delta:
      enabled: true
      temperature_internal: "sensor.living_room_temp"
      temperature_external: "weather.provincia"  # weather entity
      humidity_source: "sensor.living_room_humidity"
```

---

### Sprint 2.1: EASC Infrastructure & Sensor Refactoring (2 settimane)
**Owner**: Development Team
**Start**: 2026-04-03
**End**: 2026-04-16

#### Task Checklist

##### Infrastructure
- [x] **EASC-001**: Config schema validation
  - [x] Aggiungi config schema per EASC options (`easc_schema.py`)
  - [x] Validate entity_id references (`validate_source`)
  - [x] Validation formulas custom (`validate_formula`)
  - **Effort**: 3h ✅ **COMPLETATO 2026-03-27**
  - **Priority**: 🔴 Alta

- [x] **EASC-002**: Data source provider
  - [x] Crea `EASCDataProvider` class (`easc_provider.py`)
  - [x] Method `get_temperature(source)` → float
  - [x] Method `get_humidity(source)` → float
  - [x] Method `get_entity_state(entity_id)` with fallback
  - [x] Unit conversion utilities (`celsius_from_unit`, `humidity_to_percent`)
  - **Effort**: 4h ✅ **COMPLETATO 2026-03-27**
  - **Priority**: 🔴 Alta

- [x] **EASC-003**: Options flow UI (step EASC in VmcHeltyOptionsFlowHandler)
  - [x] Nuovo step `advanced_sensors` nell'options flow esistente
  - [x] Toggle enabled/disabled per ogni sensore avanzato
  - [x] Campi sorgente per temperature_source, humidity_source, ecc.
  - [x] Form validation e error handling (`validate_source` per-campo)
  - [x] Helpers `_flatten_easc_config` / `_build_easc_config_from_input`
  - [x] Labels `strings.json` aggiornate (IT)
  - **Effort**: 5h ✅ **COMPLETATO 2026-03-27**
  - **Priority**: 🔴 Alta

##### Sensor Refactoring
- [x] **EASC-004**: Refactor VmcHeltyAbsoluteHumiditySensor
  - [x] Inject EASCDataProvider (lazy, via `self.hass`)
  - [x] Get temp/humidity da provider con sorgenti configurabili
  - [x] Update unit tests (`config_entry.options = {}`)
  - **Effort**: 2h ✅ **COMPLETATO 2026-03-27**
  - **Priority**: 🔴 Alta

- [x] **EASC-005**: Refactor VmcHeltyDewPointSensor
  - [x] Inject EASCDataProvider
  - [x] Support external temp/humidity sources
  - [x] Update unit tests
  - **Effort**: 2h ✅ **COMPLETATO 2026-03-27**
  - **Priority**: 🔴 Alta

- [x] **EASC-006**: Refactor VmcHeltyComfortIndexSensor
  - [x] Inject EASCDataProvider
  - [x] Support external temp/humidity sources
  - [x] Update unit tests
  - **Effort**: 2h ✅ **COMPLETATO 2026-03-27**
  - **Priority**: 🔴 Alta

- [x] **EASC-007**: Refactor VmcHeltyDewPointDeltaSensor
  - [x] Support external temp_int, temp_ext, humidity sources
  - [x] Weather entity support via `get_temperature_external()`
  - [x] Update unit tests
  - **Effort**: 2h ✅ **COMPLETATO 2026-03-27**
  - **Priority**: 🔴 Alta

##### Testing & Documentation
- [x] **TEST-004**: Unit tests EASC provider
  - [x] Test temperature conversions (°C vs °F) — `TestCelsiusFromUnit` (7 test)
  - [x] Test humidity conversions (0-1 vs 0-100) — `TestHumidityToPercent` (6 test)
  - [x] Test fallback to VMC data — `TestGetTemperatureEntity`, `TestGetHumidityEntity`
  - [x] Test invalid entity_id handling — `TestGetEntityState`, `TestMixedScenarios`
  - [x] Test `magnus_coefficients` (Magnus-Tetens vs August-Roche-Magnus) — `TestMagnusCoefficients` (5 test)
  - **Effort**: 3h ✅ **COMPLETATO 2026-03-27**
  - **Priority**: 🔴 Alta

- [x] **TEST-005**: Integration tests sensors refactored
  - [x] Test ogni sensore con 3 source scenarios (VMC, external, mixed) — `test_easc_integration_sensors.py`
  - [x] Test fallback automatico (entity unavailable/unknown → VMC)
  - [x] Test error conditions (None data, zero humidity, invalid VMGI)
  - [x] Test formula attribute in `extra_state_attributes` per tutti e 4 i sensori
  - **Effort**: 4h ✅ **COMPLETATO 2026-03-27**
  - **Priority**: 🔴 Alta

- [x] **DOC-012**: Documentation EASC
  - [x] Crea `docs/EXTERNAL_ADVANCED_SENSORS.md`
  - [x] Guida configurazione step-by-step (form EASC, campi source, formula)
  - [x] Esempi: integrazione Netatmo, ESPHome, weather entity
  - [x] Sezione fallback automatico con esempio log WARNING
  - [x] Troubleshooting: valori inattesi, fallback inatteso, debug logging, errori validazione
  - **Effort**: 3h ✅ **COMPLETATO 2026-03-27**
  - **Priority**: 🟡 Media

##### Binary Sensors
- [x] **SENS-005**: Implementa `VmcHeltyFilterWarningBinarySensor`
  - [x] Crea classe in `sensor.py`
  - [x] ON quando filter_hours > 90% massimo (~15970h su 17744h)
  - [x] Device class: problem
  - [x] Icon: mdi:air-filter-alert
  - [x] **Criteri successo**: Trigger ON a ~15970h, OFF dopo reset
  - **Effort**: 1h ✅ **COMPLETATO 2026-03-26**
  - **Priority**: 🔴 Alta

**Sprint 2.1 Total Effort**: ~31h

---

### Sprint 2.2: EASC Advanced & Release (1 settimana)
**Owner**: Development Team
**Start**: 2026-04-17
**End**: 2026-05-01

#### Task Checklist

- [x] **EASC-008**: Diagnostics logging
  - [x] DEBUG log per ogni lettura (source + valore) in `EASCDataProvider`
  - [x] WARNING + DEBUG fallback quando fonte esterna non disponibile
  - [x] Sezione `easc` in `diagnostics.py`: configurazione + disponibilità entità + `last_updated`
  - **Effort**: 2h ✅ **COMPLETATO 2026-03-27**
  - **Priority**: 🟡 Media

- [x] **EASC-009**: Custom formula support
  - [x] Supporto formula custom per sensori evoluti (AbsoluteHumidity, DewPoint, ComfortIndex, DewPointDelta)
  - [x] `magnus_coefficients(formula)` in `easc_provider.py` + integrazione in tutti i `native_value`
  - [x] Formula field in `_flatten_easc_config` / `_build_easc_config_from_input` e schema options flow
  - [x] `validate_formula` nel form + errore `invalid_easc_formula` in `strings.json`
  - [x] Test formula custom scenarios in `test_easc_options_flow.py`
  - **Effort**: 3h ✅ **COMPLETATO 2026-03-27**
  - **Priority**: 🟡 Media

- [x] **TEST-006**: Full integration testing EASC
  - [x] Test tutti i sensori con EASC abilitato (pipeline options→sensori) — `test_easc_full_flow.py`
  - [x] Test config flow completo — round-trip flatten/build con tutti i 17 campi (incl. formula)
  - [x] Test regression sensors esistenti — `VmcHeltySensor` non risente di EASC options
  - [x] Test `is_sensor_enabled` per tutti i 4 sensori
  - [x] Test multi-sensore simultaneo + indipendenza delle sorgenti
  - **Effort**: 4h ✅ **COMPLETATO 2026-03-27**
  - **Priority**: 🔴 Alta

- [x] **DOC-013**: Aggiorna README principale
  - [x] Sezione EASC con link a `docs/EXTERNAL_ADVANCED_SENSORS.md`
  - [x] Lista sensori aggiornata con tag `(EASC-enabled)` + link documentazione
  - [x] Sezione "External Advanced Sensor Configuration (EASC)" con quick setup + esempio Netatmo
  - [x] Sezione "Upcoming Features" aggiornata con EASC e Filter Warning come già shippati
  - **Effort**: 2h ✅ **COMPLETATO 2026-03-27**
  - **Priority**: 🟡 Media

- [x] **DOC-011**: Aggiorna `CHANGELOG.md` v1.2.0
  - [x] Sezione `[Unreleased] — v1.2.0` con tutte le novità EASC
  - [x] EASCDataProvider, magnus_coefficients, options flow, diagnostics, sensori, test, docs
  - [x] Nessun breaking change (EASC è opt-in, default = `vmc`)
  - [x] Link a `docs/EXTERNAL_ADVANCED_SENSORS.md`
  - **Effort**: 1h ✅ **COMPLETATO 2026-03-27**
  - **Priority**: 🔴 Alta

- [x] **REL-005**: Merge feature branch
  - [x] Merge `milestone-1.2` → `main`
  - [x] Resolve conflicts (se presenti)
  - [x] Verify CI/CD passa
  - **Effort**: 1h ✅ **COMPLETATO 2026-03-30**
  - **Priority**: 🔴 Alta

- [x] **REL-006**: Tag release v1.2.0
  - [x] `git tag -a v1.2.0 -m "Release v1.2.0"`
  - [x] Push tag a tutti remotes
  - **Effort**: 15min ✅ **COMPLETATO 2026-03-30**
  - **Priority**: 🔴 Alta

- [x] **REL-007**: GitHub Release publication
  - [x] Create release from tag
  - [x] Copy release notes da CHANGELOG
  - [x] Mark as "Latest release"
  - [x] Publish
  - **Effort**: 30min ✅ **COMPLETATO 2026-03-30**
  - **Priority**: 🔴 Alta

- [x] **REL-008**: HACS update
  - [x] Verify HACS fetches new version
  - [x] Update integration description
  - **Effort**: 30min ✅ **COMPLETATO 2026-03-30**
  - **Priority**: 🔴 Alta

**Sprint 2.2 Total Effort**: ~14h
**Deliverable**: v1.2.0 con EASC pubblicamente disponibile

---


## 🎯 Milestone 3: v1.3.0 (Target: 2026-08-15)

**Obiettivo**: Nuovi sensori di monitoraggio e blueprint aggiuntivi di automazione

### Sprint 3.1: Nuovi Sensori (2 giorni)
**Owner**: Development Team
**Start**: 2026-05-19
**End**: 2026-05-20

#### Task Checklist

- [ ] **REL-022**: Create feature branch
  - [ ] Merge `feature/v1.3.0` → `main`
  - [ ] Verify CI/CD passa
  - **Effort**: 30min
  - **Priority**: 🔴 Alta

- [ ] **SENS-004**: Implementa `VmcHeltyRunningTimeSensor`
  - [ ] Tempo totale funzionamento (hours)
  - [ ] Device class: duration
  - [ ] Persistent tra restart
  - [ ] **Criteri successo**: Accumula correttamente ore funzionamento
  - **Effort**: 2h
  - **Priority**: 🟢 Bassa

**Sprint 3.1 Total Effort**: ~3h

---

### Sprint 3.2: Blueprint Aggiuntivi (1 settimana)
**Owner**: Development Team
**Start**: 2026-05-22
**End**: 2026-05-28

#### Task Checklist

- [ ] **BLU-005**: Crea `vmc_temperature_compensation.yaml`
  - [ ] Logic: riduce ventilazione se temp esterna estrema
  - [ ] Input: outdoor/indoor temp sensors
  - [ ] Threshold: min inverno (-5°C), max estate (35°C)
  - [ ] Test con dati reali
  - **Effort**: 4h
  - **Priority**: 🟡 Media

- [ ] **BLU-007**: Crea `vmc_energy_saving.yaml`
  - [ ] Logic: riduce in fasce orarie risparmio
  - [ ] Input: time ranges start/end
  - [ ] Velocità differenziate per fascia
  - [ ] Test transizioni orarie
  - **Effort**: 3h
  - **Priority**: 🟢 Bassa

- [ ] **BLU-008**: Testing tutti i blueprint aggiuntivi
  - [ ] Test scenarios per ogni blueprint
  - [ ] Verifica no conflitti tra blueprint
  - [ ] Validate YAML syntax
  - **Effort**: 4h
  - **Priority**: 🔴 Alta
  - **Dipendenze**: BLU-005, BLU-006, BLU-007

- [ ] **BLU-009**: Documentation nuovi blueprint
  - [ ] Aggiungi a BLUEPRINT_GUIDE.md
  - [ ] Esempi configurazione
  - [ ] Update README blueprint
  - **Effort**: 3h
  - **Priority**: 🟡 Media

**Sprint 3.2 Total Effort**: ~17h
**Deliverable**: 3 blueprint aggiuntivi (totale 6)

---

### Sprint 3.3: Release v1.3.0 (3 giorni)
**Owner**: Development Team
**Start**: 2026-05-29
**End**: 2026-05-31

#### Task Checklist

- [ ] **DOC-011**: Aggiorna `CHANGELOG.md` v1.3.0
  - [ ] Sezione `[1.3.0]` con nuovi sensori e blueprint
  - [ ] Breaking changes (se presenti)
  - **Effort**: 1h
  - **Priority**: 🔴 Alta

- [ ] **REL-009**: Merge feature branch
  - [ ] Merge `feature/v1.3.0` → `main`
  - [ ] Verify CI/CD passa
  - **Effort**: 30min
  - **Priority**: 🔴 Alta

- [ ] **REL-010**: Tag release v1.3.0
  - [ ] `git tag -a v1.3.0 -m "Release v1.3.0"`
  - [ ] Push tag a tutti remotes
  - **Effort**: 15min
  - **Priority**: 🔴 Alta

- [ ] **REL-011**: GitHub Release publication
  - [ ] Create release from tag
  - [ ] Copy release notes da CHANGELOG
  - [ ] Mark as "Latest release"
  - [ ] Publish
  - **Effort**: 30min
  - **Priority**: 🔴 Alta

- [ ] **REL-012**: HACS update
  - [ ] Verify HACS fetches new version
  - [ ] Update integration description
  - **Effort**: 30min
  - **Priority**: 🔴 Alta

**Sprint 3.3 Total Effort**: ~3h
**Deliverable**: v1.3.0 pubblicamente disponibile

---

## 🎯 Milestone 4: v1.4.0 (Target: 2026-11-15)

**Obiettivo**: Dashboard package completo e polish finale per release stabile

### Sprint 4.1: Package & Dashboard (1 settimana)
**Owner**: Development Team
**Start**: 2026-08-17
**End**: 2026-08-23

#### Task Checklist

##### Package Completo
- [ ] **PKG-001**: Crea `packages/vmc_helty_dashboard.yaml`
  - [ ] Sezione input_boolean helpers
  - [ ] Sezione input_number helpers
  - [ ] Sezione template sensors
  - [ ] Sezione automations package
  - [ ] Comments dettagliati
  - **Effort**: 4h
  - **Priority**: 🔴 Alta

- [ ] **PKG-002**: Template Sensors
  - [ ] `sensor.vmc_status_descrittivo` (testuale)
  - [ ] `sensor.vmc_air_quality_overall` (Eccellente/Buona/...)
  - [ ] `sensor.vmc_filter_remaining_days` (stima giorni)
  - [ ] Icon dinamici basati su stato
  - **Effort**: 3h
  - **Priority**: 🟡 Media

- [ ] **PKG-003**: Automazioni Package
  - [ ] Auto-control CO2 (base)
  - [ ] Auto-control umidità (base)
  - [ ] Notifica filtro automatica
  - [ ] Mode switching giorno/notte
  - **Effort**: 4h
  - **Priority**: 🟡 Media

##### Dashboard Views
- [ ] **DASH-001**: Crea `dashboards/vmc_helty.yaml`
  - [ ] View 1: Controllo (card + quick controls)
  - [ ] View 2: Monitoraggio (grafici e gauge)
  - [ ] View 3: Manutenzione (filtro + statistiche)
  - [ ] View 4: Automazioni (liste automazioni attive)
  - **Effort**: 5h
  - **Priority**: 🔴 Alta

- [ ] **DASH-002**: Screenshot dashboard
  - [ ] Screenshot ogni view
  - [ ] Salva in `docs/images/`
  - [ ] Aggiungi a documentazione
  - **Effort**: 1h
  - **Priority**: 🟢 Bassa

##### Documentation Package
- [ ] **DOC-007**: Guida installazione package
  - [ ] `docs/PACKAGE_SETUP.md`
  - [ ] Step-by-step install
  - [ ] Configurazione helpers
  - [ ] Personalizzazione dashboard
  - **Effort**: 3h
  - **Priority**: 🟡 Media

**Sprint 4.1 Total Effort**: ~20h
**Deliverable**: Package completo importabile + dashboard pronte

---

### Sprint 4.2: Final Polish & Release (4 giorni)
**Owner**: Development Team
**Start**: 2026-08-24
**End**: 2026-08-27

#### Task Checklist

- [ ] **QA-006**: Full integration testing
  - [ ] Test package import
  - [ ] Test tutti blueprint insieme
  - [ ] Test dashboard rendering
  - [ ] Test multi-VMC setup
  - **Effort**: 4h
  - **Priority**: 🔴 Alta

- [ ] **QA-007**: Performance testing
  - [ ] Monitor CPU/memory usage
  - [ ] Verify no memory leaks
  - [ ] Test con 1000+ history samples
  - **Effort**: 2h
  - **Priority**: 🟡 Media

- [ ] **QA-008**: Accessibility check dashboard
  - [ ] Keyboard navigation
  - [ ] Screen reader compatibility
  - [ ] Color contrast
  - **Effort**: 2h
  - **Priority**: 🟢 Bassa

- [ ] **DOC-009**: Review completa documentazione
  - [ ] Proof-reading README principale
  - [ ] Check tutti i link funzionanti
  - [ ] Aggiorna screenshots obsoleti
  - **Effort**: 3h
  - **Priority**: 🟡 Media

- [ ] **DOC-010**: Release notes v1.4.0
  - [ ] File `RELEASE_NOTES_v1.4.0.md`
  - [ ] Highlights principali
  - [ ] Breaking changes
  - [ ] Migration guide da v1.3.0
  - [ ] Credits contributors
  - **Effort**: 2h
  - **Priority**: 🔴 Alta

- [ ] **DOC-011**: Aggiorna `CHANGELOG.md` v1.4.0
  - [ ] Sezione `[1.4.0]` completa
  - [ ] Data release corretta
  - [ ] Link a commits/PRs
  - **Effort**: 30min
  - **Priority**: 🔴 Alta

- [ ] **REL-013**: Merge feature branch
  - [ ] Merge `feature/v1.4.0` → `main`
  - [ ] Resolve conflicts (se presenti)
  - [ ] Verify CI/CD passa
  - **Effort**: 1h
  - **Priority**: 🔴 Alta

- [ ] **REL-015**: Tag release v1.4.0
  - [ ] `git tag -a v1.4.0 -m "Release v1.4.0"`
  - [ ] Push tag a tutti remotes
  - **Effort**: 15min
  - **Priority**: 🔴 Alta

- [ ] **REL-016**: GitHub Release publication
  - [ ] Create release from tag
  - [ ] Copy release notes da CHANGELOG
  - [ ] Mark as "Latest release"
  - [ ] Publish
  - **Effort**: 30min
  - **Priority**: 🔴 Alta

- [ ] **REL-017**: HACS update
  - [ ] Verify HACS fetches new version
  - [ ] Update integration description
  - [ ] Update screenshots
  - **Effort**: 1h
  - **Priority**: 🔴 Alta

**Sprint 4.2 Total Effort**: ~17h
**Deliverable**: v1.4.0 pubblicamente disponibile

---


## 🎯 Milestone 5: v1.5.0 (Target: 2027-02-15)

**Obiettivo**: Quality Scale Gold + Energy Dashboard + Scene e Script predefiniti

### Sprint 5.1: Quality Scale Gold Upgrade (2 settimane)
**Owner**: Development Team
**Start**: 2026-11-16
**End**: 2026-11-29

#### Task Checklist

##### Icon Translations
- [ ] **GOLD-001**: Implementa icon translations in `strings.json`
  - [ ] State-based icons per sensors
  - [ ] Range-based icons (filter, battery-like)
  - [ ] Update entity descriptions
  - **Effort**: 4h
  - **Priority**: 🔴 Alta

##### Exception Translations
- [ ] **GOLD-002**: Translate all exceptions
  - [ ] Convert ServiceValidationError a translated
  - [ ] Convert HomeAssistantError a translated
  - [ ] Aggiungi translation keys in strings.json
  - [ ] Test error messages in UI
  - **Effort**: 3h
  - **Priority**: 🔴 Alta

##### Entity Translations Complete
- [ ] **GOLD-003**: Complete entity translations
  - [ ] All entity names
  - [ ] All state attributes
  - [ ] All device classes
  - [ ] Verify Italian + English
  - **Effort**: 4h
  - **Priority**: 🔴 Alta

##### Documentation Review
- [ ] **GOLD-004**: Review per Gold standard
  - [ ] Check all docstrings present
  - [ ] Type hints complete
  - [ ] Code examples accurate
  - **Effort**: 3h
  - **Priority**: 🟡 Media

**Sprint 5.1 Total Effort**: ~14h

---

### Sprint 5.2: Energy Dashboard Integration (1 settimana)
**Owner**: Development Team
**Start**: 2026-11-30
**End**: 2026-12-06

#### Task Checklist

##### Energy Platform
- [ ] **ENERGY-001**: Registra sensori con Energy platform
  - [ ] Config energy manager
  - [ ] Register power sensor
  - [ ] Register energy sensor
  - [ ] Test in Energy dashboard
  - **Effort**: 4h
  - **Priority**: 🔴 Alta

- [ ] **ENERGY-002**: Tariffe energia opzionali
  - [ ] Config input_number per costo kWh
  - [ ] Calcolo costo giornaliero/mensile
  - [ ] Sensor monetary unit
  - **Effort**: 3h
  - **Priority**: 🟡 Media

- [ ] **ENERGY-003**: Statistics long-term
  - [ ] Verify recorder configuration
  - [ ] Optimize storage energy data
  - [ ] Test retention policies
  - **Effort**: 2h
  - **Priority**: 🟡 Media

##### Testing Energy
- [ ] **TEST-003**: Test energy tracking accuracy
  - [ ] Compare with real consumption (se possibile)
  - [ ] Verify accumulation correct
  - [ ] Test reset/calibration
  - **Effort**: 3h
  - **Priority**: 🔴 Alta

**Sprint 5.2 Total Effort**: ~12h

---

### Sprint 5.3: Scene e Script (3 giorni)
**Owner**: Development Team
**Start**: 2026-12-07
**End**: 2026-12-09

#### Task Checklist

##### Scene Predefinite
- [ ] **SCENE-001**: Crea `examples/scenes.yaml`
  - [ ] Scene "Modalità Notte"
  - [ ] Scene "Boost Rapido"
  - [ ] Scene "Risparmio Energetico"
  - [ ] Scene "Manuale Max Comfort"
  - **Effort**: 2h
  - **Priority**: 🟡 Media

##### Script Predefiniti
- [ ] **SCRIPT-001**: Crea `examples/scripts.yaml`
  - [ ] Script "VMC Boost Temporizzato"
  - [ ] Script "VMC Filter Check"
  - [ ] Script "VMC Diagnostics Run"
  - [ ] Script "VMC Night Mode Auto"
  - **Effort**: 3h
  - **Priority**: 🟡 Media

- [ ] **SCRIPT-002**: Documentation scene/script
  - [ ] Guida uso in docs
  - [ ] Esempi personalizzazione
  - **Effort**: 2h
  - **Priority**: 🟢 Bassa

**Sprint 5.3 Total Effort**: ~7h

---

### Sprint 5.4: Release v1.5.0 (3 giorni)
**Owner**: Development Team
**Start**: 2026-12-10
**End**: 2026-12-12

#### Task Checklist

- [ ] **DOC-011**: Aggiorna `CHANGELOG.md` v1.5.0
  - [ ] Sezione `[1.5.0]` completa
  - [ ] Data release corretta
  - **Effort**: 1h
  - **Priority**: 🔴 Alta

- [ ] **REL-018**: Merge feature branch
  - [ ] Merge `feature/v1.5.0` → `main`
  - [ ] Verify CI/CD passa
  - **Effort**: 1h
  - **Priority**: 🔴 Alta

- [ ] **REL-019**: Tag release v1.5.0
  - [ ] `git tag -a v1.5.0 -m "Release v1.5.0"`
  - [ ] Push tag a tutti remotes
  - **Effort**: 15min
  - **Priority**: 🔴 Alta

- [ ] **REL-020**: GitHub Release publication
  - [ ] Create release from tag
  - [ ] Copy release notes da CHANGELOG
  - [ ] Submit Gold quality scale verification
  - [ ] Mark as "Latest release"
  - [ ] Publish
  - **Effort**: 1h
  - **Priority**: 🔴 Alta

- [ ] **REL-021**: HACS update
  - [ ] Verify HACS fetches new version
  - [ ] Update integration description
  - [ ] Update screenshots
  - **Effort**: 1h
  - **Priority**: 🔴 Alta

**Sprint 5.4 Total Effort**: ~4h
**Deliverable**: v1.5.0 Gold Quality pubblicamente disponibile

---


## 📋 Backlog (Priorità Bassa - Future)

### Feature Requests Community
- [ ] Multi-zona VMC management
- [ ] HomeKit native integration
- [ ] Alexa/Google Home custom intents
- [ ] Mobile app companion
- [ ] Machine Learning predictions
- [ ] Weather integration advanced
- [ ] Calendar-based scheduling

### Technical Debt
- [ ] Rimuovi tutti `_LOGGER.setLevel(logging.DEBUG)`
- [ ] Risolvi TODO in `config_flow.py:567`
- [ ] Refactor constants consolidation
- [ ] Mypy strict mode

---

## 📊 Metriche e KPI

### Development Metrics
| Metrica | Target v1.3.0 | Attuale (v1.2.0) | Status |
|---------|---------------|------------------|--------|
| Test Coverage | >90% | 84% | ✅ (gate: 65%) |
| Pylint Score | >9.5 | 9.83 | ✅ |
| Blueprint Count | 6 | 2 | 🔄 33% |
| Sensor Count | 20 | 20+ | ✅ |
| Documentation Pages | 10 | 6 | 🔄 60% |

### Community Metrics (Goals)
| Metrica | Target v1.2.0 | Baseline |
|---------|---------------|----------|
| GitHub Stars | 100 | 42 |
| HACS Installs | 500 | 156 |
| Issues Closed % | >80% | 73% |
| Forum Posts | 20 | 8 |
| Contributors | 5 | 1 |

---

## 🚦 Risk Management

### Risks Identificati

| Risk | Probabilità | Impatto | Mitigation |
|------|-------------|---------|------------|
| Beta testers insufficienti | Media | Alto | Early announcement, incentives |
| Breaking changes in HA Core | Bassa | Alto | Monitor HA dev, test pre-release |
| Blueprint conflicts | Media | Medio | Clear documentation, warnings |
| Performance issues multi-VMC | Bassa | Medio | Performance testing, optimization |
| Translation quality | Media | Basso | Community review, proofreading |

---

## 👥 Team & Responsibilities

### Roles

- **Project Lead**: Coordinamento milestone, decisioni architetturali
- **Core Developer**: Implementazione features, code review
- **QA Lead**: Testing strategy, quality assurance
- **Documentation Lead**: Docs, guides, examples
- **Community Manager**: Support, feedback collection, communication

### Time Allocation Estimate

- **Development**: 70% (coding, testing, debugging)
- **Documentation**: 20% (writing, reviewing, translating)
- **Community**: 10% (support, feedback, communication)

---

## 📅 Timeline Overview

```
2026-03  ║████░░░░░░░░░░░░░░░░░░░░░░║ Sprint 1.1-1.3 → v1.1.1 ✅
2026-04  ║░░░░████████████░░░░░░░░░░║ Sprint 2.1 (EASC infra + refactoring)
2026-05  ║░░░░░░░░░░░░░░░░████████░░║ Sprint 2.2 (EASC advanced + release v1.2.0)
2026-05  ║░░░░░░░░░░░░░░░░░░░░░░████║ Sprint 3.1-3.2 (Sensori + Blueprint)
2026-05  ║░░░░░░░░░░░░░░░░░░░░░░░░██║ Sprint 3.3 → v1.3.0
2026-08  ║░░████████████░░░░░░░░░░░░║ Sprint 4.1-4.2 (Package + Dashboard)
2026-08  ║░░░░░░░░░░░░░░██░░░░░░░░░░║ Sprint 4.2 → v1.4.0
2026-11  ║░░░░░░░░░░░░░░░░████████░░║ Sprint 5.1-5.3 (Gold + Energy + Scene)
2026-12  ║░░░░░░░░░░░░░░░░░░░░░░████║ Sprint 5.4 → v1.5.0

Legend: ████ = Active Development
        ░░░░ = Planning/Buffer
```

---

## ✅ Acceptance Criteria

### v1.1.1
- ✅ 3 nuovi blueprint testati e funzionanti
- ✅ 8 nuovi sensori implementati
- ✅ Test coverage >95%
- ✅ Documentation aggiornata
- ✅ No breaking changes per utenti esistenti
- ✅ GitHub release pubblicata con "pre-release" flag

### v1.2.0
- ✅ Tutti i sensori evoluti supportano sorgenti dati esterne (EASC)
- ✅ Config flow UI per configurazione EASC
- ✅ Fallback automatico a dati VMC funzionante
- ✅ Test coverage >95% su codice EASC
- ✅ Documentazione EASC completa
- ✅ SENS-005 `VmcHeltyFilterWarningBinarySensor` implementato
- ✅ Zero bug critici aperti

### v1.3.0
- ✅ Tutti criteri v1.2.0
- ✅ SENS-004 `VmcHeltyRunningTimeSensor` implementato e testato
- ✅ 6 blueprint totali disponibili (3 esistenti + 3 nuovi)
- ✅ Documentation blueprint aggiornata

### v1.4.0
- ✅ Tutti criteri v1.3.0
- ✅ Package YAML importabile completo
- ✅ 4 dashboard views funzionanti
- ✅ QA completo (integration, performance, accessibility)
- ✅ Release notes e comunicazione community

### v1.5.0
- ✅ Quality Scale Gold certificato
- ✅ Energy Dashboard integration funzionante
- ✅ Scene e script predefiniti
- ✅ Tutte translations complete (IT + EN)
- ✅ Performance benchmark passed
- ✅ Community feedback positivo (>80%)

---

## 🔄 Review Process

### Weekly Review (ogni Venerdì)
- Review task completati questa settimana
- Update progress percentages
- Identify blockers
- Adjust priorities se necessario
- Plan next week tasks

### Sprint Retrospective (fine ogni sprint)
- What went well?
- What could be improved?
- Action items per prossimo sprint
- Update timeline se necessario

### Milestone Review (fine milestone)
- Verifica acceptance criteria
- Community feedback assessment
- Lessons learned documentation
- Celebrate achievements! 🎉

---

## 📝 Notes & Updates

### 2026-03-23 - Initial Roadmap
- ✅ Created comprehensive roadmap
- ✅ Defined milestones v1.1.1, v1.2.0, v1.3.0, v1.4.0
- ✅ Breakdown in sprints with effort estimates
- ✅ Created 3 blueprint proof-of-concepts
- ✅ Documented acceptance criteria

### 2026-03-27 - Restructure Milestone Plan
- ✅ Milestone 2 = v1.2.0 (EASC feature)
- ✅ Milestone 3 = v1.3.0 (Sensori + Blueprint)
- ✅ Milestone 4 = v1.4.0 (Package + Dashboard)
- ✅ Milestone 5 = v1.5.0 (Gold Quality + Energy + Scene/Script)
- ✅ Sprint numbering allineato con milestone
- ✅ DOC-011 e REL release steps presenti in ogni milestone

### 2026-03-30 - v1.2.0 Released
- ✅ EASC (External Advanced Sensor Configuration) completato e rilasciato
- ✅ Tutti i task Sprint 2.1 e Sprint 2.2 completati
- ✅ REL-005→REL-008 eseguiti (merge, tag, GitHub release, HACS)
- ✅ 757 test, 84% coverage, Pylint 9.83/10
- ⏸️ Sviluppo in pausa dopo v1.2.0

### Next Update: ripresa sviluppo per v1.3.0

---

## 🎯 Quick Reference

### Priority Legend
- 🔴 Alta: Blocca release, critico
- 🟡 Media: Importante, non blocca release
- 🟢 Bassa: Nice-to-have, opzionale

### Status Legend
- ✅ Completato
- 🔄 In Progress
- 📋 Planned
- ⏸️ On Hold
- ❌ Cancelled

### Effort Estimate Guidelines
- XS: <1h
- S: 1-2h
- M: 2-4h
- L: 4-8h
- XL: >8h (split in sub-tasks)

---

**Responsabile Roadmap**: VMC Helty Flow Development Team
**Prossima Review**: ripresa sviluppo v1.3.0
**Documento vivente**: Aggiornare regolarmente con progressi effettivi
