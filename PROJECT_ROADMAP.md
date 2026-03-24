# 🗺️ VMC Helty Flow - Roadmap Operativa

> **Piano di sviluppo** con task tracciabili, milestone e criteri di completamento
> **Versione**: 1.0
> **Data inizio**: 2026-03-23
> **Ultima revisione**: 2026-03-23

---

## 📊 Dashboard Progressi

### Stato Generale Progetto
```
Versione Corrente: v1.1.0 ✅
Prossimo Release: v1.2.0 🔄
Quality Scale: Silver ⭐⭐
Test Coverage: >95% ✅
Tech Debt: 1 item ⚠️ (SENS-009: monitoraggio energia reale)
```

### Milestone Overview
| Milestone | Stato | Data Target | Completamento |
|-----------|-------|-------------|---------------|
| v1.2.0-beta | 🔄 In Progress | 2026-04-15 | ▓▓▓▓░░░░░░ 45% |
| v1.2.0 | 📋 Planned | 2026-05-15 | ░░░░░░░░░░ 0% |
| v1.3.0 Gold | 📋 Planned | 2026-08-15 | ░░░░░░░░░░ 0% |
| v1.4.0 Platinum | 📋 Planned | 2026-11-15 | ░░░░░░░░░░ 0% |

---

## 🎯 Milestone 1: v1.2.0-beta (Target: 2026-04-15)

**Obiettivo**: Rilascio beta con nuovi blueprint e sensori base per feedback community

### Sprint 1.1: Blueprint e Testing (1-2 settimane)
**Owner**: Development Team
**Start**: 2026-03-23
**End**: 2026-04-06

#### Task Checklist

##### 1. Blueprint Testing e Refinement
- [ ] **BLU-001**: Test completo `vmc_air_quality_adaptive.yaml`
  - [ ] Test con sensore CO2 integrato VMC
  - [ ] Test con sensore CO2 esterno (Netatmo/ESPHome)
  - [ ] Test logic hyperventilation mode
  - [ ] Test delay anti-oscillazione
  - [ ] Validate YAML syntax
  - [ ] **Criteri successo**: 10 test run senza errori, 5 cicli CO2 alto→basso
  - **Effort**: 3h
  - **Priority**: 🔴 Alta

- [ ] **BLU-002**: Test completo `vmc_humidity_control.yaml`
  - [ ] Test boost doccia (70% → 100% speed)
  - [ ] Test durata minima garantita
  - [ ] Test estensione boost se umidità alta
  - [ ] Test cooldown tra boost
  - [ ] Test blackout notturno
  - [ ] Test notifiche mobile/persistent
  - [ ] **Criteri successo**: 5 cicli doccia simulati correttamente
  - **Effort**: 3h
  - **Priority**: 🔴 Alta

- [ ] **BLU-003**: Test completo `vmc_filter_reminder.yaml`
  - [ ] Test notifica avviso 90% (~15970h su 17744h)
  - [ ] Test notifica critica 95% (~16857h su 17744h)
  - [ ] Test promemoria giornaliero 100%
  - [ ] Test persistent notification
  - [ ] Test mobile notification con action buttons
  - [ ] Test email notification
  - [ ] **Criteri successo**: Tutte le notifiche arrivano nei canali configurati
  - **Effort**: 2h
  - **Priority**: 🟡 Media

- [ ] **BLU-004**: Fix bug e improvement da testing
  - [ ] Fix eventuali errori sintassi YAML
  - [ ] Ottimizza logica condition
  - [ ] Migliora messaggi notifica
  - [ ] Aggiungi validation input
  - **Effort**: 4h
  - **Priority**: 🔴 Alta
  - **Dipendenze**: BLU-001, BLU-002, BLU-003

##### 2. Documentation Blueprint
- [ ] **DOC-001**: Aggiorna `blueprints/README.md`
  - [ ] Aggiungi badge import per nuovi blueprint
  - [ ] Documenta prerequisiti
  - [ ] Aggiungi esempi configurazione
  - **Effort**: 2h
  - **Priority**: 🟡 Media

- [ ] **DOC-002**: Review `blueprints/BLUEPRINT_GUIDE.md`
  - [ ] Verifica esempi pratici accurati
  - [ ] Aggiungi screenshot (opzionale)
  - [ ] Proof-reading italiano
  - **Effort**: 2h
  - **Priority**: 🟡 Media

- [ ] **DOC-003**: Traduci guida in inglese
  - [ ] Crea `blueprints/BLUEPRINT_GUIDE_EN.md`
  - [ ] Traduzioni accurate esempi
  - **Effort**: 4h
  - **Priority**: 🟢 Bassa

##### 3. Code Quality
- [ ] **QA-001**: Run linters su blueprint files
  - [ ] yamllint su tutti i .yaml
  - [ ] Fix warning/errors
  - **Effort**: 1h
  - **Priority**: 🔴 Alta

- [ ] **QA-002**: Peer review blueprint code
  - [ ] Review logic automazioni
  - [ ] Review best practices HA
  - [ ] Security check (no credentials hardcoded)
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

- [ ] **SENS-004**: Implementa `VmcHeltyRunningTimeSensor`
  - [ ] Tempo totale funzionamento (hours)
  - [ ] Device class: duration
  - [ ] Persistent tra restart
  - [ ] **Criteri successo**: Accumula correttamente ore funzionamento
  - **Effort**: 2h
  - **Priority**: 🟢 Bassa

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
- [ ] **SENS-005**: Implementa `VmcHeltyFilterWarningBinarySensor`
  - [ ] Crea classe in `sensor.py`
  - [ ] ON quando filter_hours > 90% massimo (~15970h su 17744h)
  - [ ] Device class: problem
  - [ ] Icon: mdi:air-filter-alert
  - [ ] **Criteri successo**: Trigger ON a ~15970h, OFF dopo reset
  - **Effort**: 1h
  - **Priority**: 🔴 Alta

- [ ] **SENS-006**: Implementa `VmcHeltyAirQualityAlertBinarySensor`
  - [ ] ON quando CO2 > 1000 ppm per 5+ minuti
  - [ ] Device class: problem
  - [ ] Icon: mdi:molecule-co2
  - [ ] **Criteri successo**: Alert tempestivo quando aria scadente
  - **Effort**: 1h
  - **Priority**: 🟡 Media

- [ ] **SENS-007**: Implementa `VmcHeltyCondensationRiskBinarySensor`
  - [ ] ON quando dew_point_delta < 2°C
  - [ ] Device class: problem
  - [ ] Icon: mdi:water-alert
  - [ ] **Criteri successo**: Alert quando rischio condensazione
  - **Effort**: 1h
  - **Priority**: 🟡 Media

- [ ] **SENS-008**: Implementa `VmcHeltyOfflineBinarySensor`
  - [ ] ON quando coordinator.last_update_success = False
  - [ ] Device class: connectivity
  - [ ] Icon: mdi:wifi-alert
  - [ ] **Criteri successo**: Alert immediato se VMC offline
  - **Effort**: 1h
  - **Priority**: 🟢 Bassa

##### 6. Testing Sensori
- [ ] **TEST-001**: Unit test nuovi sensori
  - [ ] Test filter life percentage calculation
  - [ ] Test energy calculation accuracy
  - [ ] Test binary sensor triggers
  - [ ] Coverage >95% su nuovo codice
  - **Effort**: 4h
  - **Priority**: 🔴 Alta
  - **Dipendenze**: SENS-001 → SENS-008

- [ ] **TEST-002**: Integration test sensori
  - [ ] Test sensori appaiono in entity registry
  - [ ] Test device info corretto
  - [ ] Test state persistence
  - **Effort**: 2h
  - **Priority**: 🔴 Alta

**Sprint 1.2 Total Effort**: ~18 ore
**Deliverable**: 8 nuovi sensori (4 statistici, 4 binary alert)

---

### Sprint 1.3: Quality & Release Beta (3 giorni)
**Owner**: Development Team
**Start**: 2026-04-14
**End**: 2026-04-15

#### Task Checklist

##### 7. Code Quality & Testing
- [ ] **QA-003**: Run full test suite
  - [ ] `pytest tests/ -v --cov`
  - [ ] Verify coverage >95%
  - [ ] Fix failing tests
  - **Effort**: 2h
  - **Priority**: 🔴 Alta

- [ ] **QA-004**: Run linters
  - [ ] `pylint custom_components/vmc_helty_flow/`
  - [ ] `mypy custom_components/vmc_helty_flow/`
  - [ ] Fix issues rating >9.5/10
  - **Effort**: 2h
  - **Priority**: 🔴 Alta

- [ ] **QA-005**: Run pre-commit hooks
  - [ ] `pre-commit run --all-files`
  - [ ] Fix formatting/lint issues
  - **Effort**: 1h
  - **Priority**: 🔴 Alta

##### 8. Documentation
- [ ] **DOC-004**: Aggiorna `CHANGELOG.md`
  - [ ] Sezione `[1.2.0-beta]` con tutte le novità
  - [ ] Link a blueprint e sensori
  - [ ] Breaking changes (se presenti)
  - **Effort**: 1h
  - **Priority**: 🔴 Alta

- [ ] **DOC-005**: Aggiorna `README.md` principale
  - [ ] Sezione blueprint con link
  - [ ] Lista sensori aggiornata
  - [ ] Badge versione v1.2.0-beta
  - **Effort**: 1h
  - **Priority**: 🟡 Media

- [ ] **DOC-006**: Aggiorna `manifest.json`
  - [ ] Version: "1.2.0-beta"
  - [ ] Quality scale verificato (Silver)
  - **Effort**: 10min
  - **Priority**: 🔴 Alta

##### 9. Git & Release
- [ ] **REL-001**: Commit e push modifiche
  - [ ] Branch: `feature/v1.2.0-beta`
  - [ ] Commit message conventional format
  - [ ] Push to origin + github
  - **Effort**: 30min
  - **Priority**: 🔴 Alta

- [ ] **REL-002**: Create Pull Request
  - [ ] PR to main con descrizione dettagliata
  - [ ] Checklist completamento
  - [ ] Request review
  - **Effort**: 30min
  - **Priority**: 🔴 Alta

- [ ] **REL-003**: Tag release beta
  - [ ] `git tag v1.2.0-beta`
  - [ ] Annotated tag con release notes
  - [ ] Push tag a remotes
  - **Effort**: 15min
  - **Priority**: 🔴 Alta

- [ ] **REL-004**: GitHub Release draft
  - [ ] Crea release v1.2.0-beta
  - [ ] "Pre-release" flag abilitato
  - [ ] Release notes da CHANGELOG
  - [ ] Richiesta beta testers
  - **Effort**: 1h
  - **Priority**: 🔴 Alta

**Sprint 1.3 Total Effort**: ~9 ore
**Deliverable**: v1.2.0-beta released su GitHub

---

## 🎯 Milestone 2: v1.2.0 Stable (Target: 2026-05-15)

**Obiettivo**: Release stabile dopo feedback beta, dashboard package, restanti blueprint

### Sprint 2.1: Beta Feedback & Fixes (1 settimana)
**Start**: 2026-04-16
**End**: 2026-04-22

#### Task Checklist

- [ ] **FEED-001**: Raccolta feedback community
  - [ ] Post su GitHub Discussions
  - [ ] Post su Home Assistant Community Forum
  - [ ] Monitor GitHub Issues
  - [ ] Traccia bug reports
  - **Effort**: 5h (distribuito su settimana)
  - **Priority**: 🔴 Alta

- [ ] **FEED-002**: Fix bug da beta testing
  - [ ] Prioritize bugs critici
  - [ ] Fix e test localmente
  - [ ] Deploy fix incrementali
  - **Effort**: 8h
  - **Priority**: 🔴 Alta

- [ ] **FEED-003**: Improvement da feedback
  - [ ] Raccogli suggerimenti utenti
  - [ ] Valuta fattibilità
  - [ ] Implementa miglioramenti quick
  - **Effort**: 6h
  - **Priority**: 🟡 Media

**Sprint 2.1 Total Effort**: ~19 ore

---

### Sprint 2.2: Blueprint Aggiuntivi (1 settimana)
**Start**: 2026-04-23
**End**: 2026-04-29

#### Task Checklist

##### 10. Nuovi Blueprint
- [ ] **BLU-005**: Crea `vmc_temperature_compensation.yaml`
  - [ ] Logic: riduce ventilazione se temp esterna estrema
  - [ ] Input: outdoor/indoor temp sensors
  - [ ] Threshold: min inverno (-5°C), max estate (35°C)
  - [ ] Test con dati reali
  - **Effort**: 4h
  - **Priority**: 🟡 Media

- [ ] **BLU-006**: Crea `vmc_presence_based.yaml`
  - [ ] Logic: velocità bassa se casa vuota
  - [ ] Input: presence sensor (binary_sensor.occupancy)
  - [ ] Delay configurabile (es. 15min)
  - [ ] Test presence on/off transitions
  - **Effort**: 3h
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

**Sprint 2.2 Total Effort**: ~17 ore
**Deliverable**: 3 blueprint aggiuntivi (totale 6)

---

### Sprint 2.3: Dashboard Package (1 settimana)
**Start**: 2026-04-30
**End**: 2026-05-06

#### Task Checklist

##### 11. Package Completo
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

##### 12. Dashboard Views
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

##### 13. Documentation Package
- [ ] **DOC-007**: Guida installazione package
  - [ ] `docs/PACKAGE_SETUP.md`
  - [ ] Step-by-step install
  - [ ] Configurazione helpers
  - [ ] Personalizzazione dashboard
  - **Effort**: 3h
  - **Priority**: 🟡 Media

- [ ] **DOC-008**: Video tutorial (opzionale)
  - [ ] Recording setup package
  - [ ] Upload su YouTube
  - [ ] Embed in docs
  - **Effort**: 4h
  - **Priority**: 🟢 Bassa (opzionale)

**Sprint 2.3 Total Effort**: ~20 ore (24h con video)
**Deliverable**: Package completo importabile + dashboard pronte

---

### Sprint 2.4: Final Polish & Release (4 giorni)
**Start**: 2026-05-07
**End**: 2026-05-15

#### Task Checklist

##### 14. Quality Assurance Finale
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

##### 15. Documentation Finale
- [ ] **DOC-009**: Review completa documentazione
  - [ ] Proof-reading README principale
  - [ ] Check tutti i link funzionanti
  - [ ] Aggiorna screenshots obsoleti
  - **Effort**: 3h
  - **Priority**: 🟡 Media

- [ ] **DOC-010**: Release notes v1.2.0
  - [ ] File `RELEASE_NOTES_v1.2.0.md`
  - [ ] Highlights principali
  - [ ] Breaking changes
  - [ ] Migration guide da v1.1.0
  - [ ] Credits contributors
  - **Effort**: 2h
  - **Priority**: 🔴 Alta

- [ ] **DOC-011**: Aggiorna CHANGELOG.md finale
  - [ ] Cambia `[1.2.0-beta]` → `[1.2.0]`
  - [ ] Data release corretta
  - [ ] Link a commits/PRs
  - **Effort**: 30min
  - **Priority**: 🔴 Alta

##### 16. Release v1.2.0
- [ ] **REL-005**: Merge feature branch
  - [ ] Merge `feature/v1.2.0` → `main`
  - [ ] Resolve conflicts (se presenti)
  - [ ] Verify CI/CD passa
  - **Effort**: 1h
  - **Priority**: 🔴 Alta

- [ ] **REL-006**: Tag release v1.2.0
  - [ ] `git tag -a v1.2.0 -m "Release v1.2.0"`
  - [ ] Push tag a tutti remotes
  - [ ] Verify tag presente su GitHub
  - **Effort**: 15min
  - **Priority**: 🔴 Alta

- [ ] **REL-007**: GitHub Release publication
  - [ ] Create release from tag
  - [ ] Copy release notes
  - [ ] Attach assets (se necessario)
  - [ ] Mark as "Latest release"
  - [ ] Publish
  - **Effort**: 30min
  - **Priority**: 🔴 Alta

- [ ] **REL-008**: HACS update
  - [ ] Verify HACS fetches new version
  - [ ] Update integration description
  - [ ] Update screenshots
  - **Effort**: 1h
  - **Priority**: 🔴 Alta

##### 17. Marketing & Communication
- [ ] **COMM-001**: Annuncio Home Assistant Community
  - [ ] Post su forum con highlights
  - [ ] Screenshot e demo
  - [ ] Link download
  - **Effort**: 1h
  - **Priority**: 🟡 Media

- [ ] **COMM-002**: Social media
  - [ ] Post su Reddit r/homeassistant
  - [ ] Twitter/X announcement
  - [ ] LinkedIn (opzionale)
  - **Effort**: 1h
  - **Priority**: 🟢 Bassa

- [ ] **COMM-003**: Contributors recognition
  - [ ] Update README contributors section
  - [ ] Thank you message nel release
  - [ ] GitHub Discussions announcement
  - **Effort**: 30min
  - **Priority**: 🟡 Media

**Sprint 2.4 Total Effort**: ~18 ore
**Deliverable**: v1.2.0 pubblicamente disponibile

---

## 🎯 Milestone 3: v1.3.0 Gold Quality (Target: 2026-08-15)

**Obiettivo**: Upgrade Quality Scale da Silver a Gold + Energy Dashboard

### Sprint 3.1: Quality Scale Gold Upgrade (2 settimane)
**Start**: 2026-06-01
**End**: 2026-06-14

#### Task Checklist

##### 18. Icon Translations
- [ ] **GOLD-001**: Implementa icon translations in `strings.json`
  - [ ] State-based icons per sensors
  - [ ] Range-based icons (filter, battery-like)
  - [ ] Update entity descriptions
  - **Effort**: 4h
  - **Priority**: 🔴 Alta

##### 19. Exception Translations
- [ ] **GOLD-002**: Translate all exceptions
  - [ ] Convert ServiceValidationError a translated
  - [ ] Convert HomeAssistantError a translated
  - [ ] Aggiungi translation keys in strings.json
  - [ ] Test error messages in UI
  - **Effort**: 3h
  - **Priority**: 🔴 Alta

##### 20. Entity Translations Complete
- [ ] **GOLD-003**: Complete entity translations
  - [ ] All entity names
  - [ ] All state attributes
  - [ ] All device classes
  - [ ] Verify Italian + English
  - **Effort**: 4h
  - **Priority**: 🔴 Alta

##### 21. Documentation Review
- [ ] **GOLD-004**: Review per Gold standard
  - [ ] Check all docstrings present
  - [ ] Type hints complete
  - [ ] Code examples accurate
  - **Effort**: 3h
  - **Priority**: 🟡 Media

**Sprint 3.1 Total Effort**: ~14 ore

---

### Sprint 3.2: Energy Dashboard Integration (1 settimana)
**Start**: 2026-06-15
**End**: 2026-06-21

#### Task Checklist

##### 22. Energy Platform
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

##### 23. Testing Energy
- [ ] **TEST-003**: Test energy tracking accuracy
  - [ ] Compare with real consumption (se possibile)
  - [ ] Verify accumulation correct
  - [ ] Test reset/calibration
  - **Effort**: 3h
  - **Priority**: 🔴 Alta

**Sprint 3.2 Total Effort**: ~12 ore

---

### Sprint 3.3: Scene e Script (3 giorni)
**Start**: 2026-06-22
**End**: 2026-06-24

#### Task Checklist

##### 24. Scene Predefinite
- [ ] **SCENE-001**: Crea `examples/scenes.yaml`
  - [ ] Scene "Modalità Notte"
  - [ ] Scene "Boost Rapido"
  - [ ] Scene "Risparmio Energetico"
  - [ ] Scene "Manuale Max Comfort"
  - **Effort**: 2h
  - **Priority**: 🟡 Media

##### 25. Script Predefiniti
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

**Sprint 3.3 Total Effort**: ~7 ore

---

### Sprint 3.4: Release v1.3.0 (3 giorni)
**Start**: 2026-06-25
**End**: 2026-06-27

#### Task Checklist

- [ ] **REL-009**: Testing completo v1.3.0
- [ ] **REL-010**: Update documentation
- [ ] **REL-011**: Merge e tag v1.3.0
- [ ] **REL-012**: GitHub Release
- [ ] **REL-013**: Submit Gold quality scale verification

**Sprint 3.4 Total Effort**: ~15 ore

---

## 🎯 Milestone 4: v1.4.0 Platinum Advanced (Target: 2026-11-15)

**Obiettivo**: Architettura avanzata per sensori configurabili + sorgenti dati esterne

### 📋 Feature Principale: External Advanced Sensor Configuration (EASC)

#### Overview
System permettere ai sensori evoluti di utilizzare fonti dati esterne (sensori HA, ESPHome, Zigbee) al posto dei sensori VMC interni, con fallback automatico a dati VMC.

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
esac_config:
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

#### Implementation Plan - Sprint 4.1 (2 settimane)

##### 4.1.1 Infrastructure
- [ ] **EASC-001**: Config schema validation
  - [ ] Aggiungi config schema per EASC options
  - [ ] Validate entity_id references
  - [ ] Validation formulas custom
  - **Effort**: 3h
  - **Priority**: 🔴 Alta

- [ ] **EASC-002**: Data source provider
  - [ ] Crea `EASCDataProvider` class
  - [ ] Method `get_temperature(source)` → float
  - [ ] Method `get_humidity(source)` → float
  - [ ] Method `get_entity_state(entity_id)` with fallback
  - [ ] Unit conversion utilities
  - **Effort**: 4h
  - **Priority**: 🔴 Alta

- [ ] **EASC-003**: Config flow UI
  - [ ] Step "advanced_sensor_config"
  - [ ] Dropdown per ogni sensore (enabled/disabled)
  - [ ] Entity picker per temperature_source, humidity_source, etc.
  - [ ] Form validation e error handling
  - **Effort**: 5h
  - **Priority**: 🔴 Alta

##### 4.1.2 Sensor Refactoring
- [ ] **EASC-004**: Refactor VmcHeltyAbsoluteHumiditySensor
  - [ ] Inject EASCDataProvider
  - [ ] Get temp/humidity da provider instead hardcoded VMC
  - [ ] Update unit tests
  - **Effort**: 2h
  - **Priority**: 🔴 Alta

- [ ] **EASC-005**: Refactor VmcHeltyDewPointSensor
  - [ ] Inject EASCDataProvider
  - [ ] Support external temp/humidity sources
  - [ ] Update unit tests
  - **Effort**: 2h
  - **Priority**: 🔴 Alta

- [ ] **EASC-006**: Refactor VmcHeltyComfortIndexSensor
  - [ ] Inject EASCDataProvider
  - [ ] Support external temp/humidity sources
  - [ ] Update unit tests
  - **Effort**: 2h
  - **Priority**: 🔴 Alta

- [ ] **EASC-007**: Refactor VmcHeltyDewPointDeltaSensor
  - [ ] Support external temp_int, temp_ext, humidity sources
  - [ ] Weather entity support per temperatura esterna
  - [ ] Update unit tests
  - **Effort**: 2h
  - **Priority**: 🔴 Alta

##### 4.1.3 Testing & Documentation
- [ ] **TEST-004**: Unit tests EASC provider
  - [ ] Test temperature conversions (°C vs °F)
  - [ ] Test humidity conversions (0-1 vs 0-100)
  - [ ] Test fallback to VMC data
  - [ ] Test invalid entity_id handling
  - **Effort**: 3h
  - **Priority**: 🔴 Alta

- [ ] **TEST-005**: Integration tests sensors refactored
  - [ ] Test ogni sensore con 3 source scenarios (VMC, external, mixed)
  - [ ] Test fallback automatico
  - [ ] Test error conditions
  - **Effort**: 4h
  - **Priority**: 🔴 Alta

- [ ] **DOC-012**: Documentation EASC
  - [ ] Crea `docs/EXTERNAL_ADVANCED_SENSORS.md`
  - [ ] Guida configurazione step-by-step
  - [ ] Esempi: integrazione Netatmo, ESPHome, weather
  - [ ] Troubleshooting
  - **Effort**: 3h
  - **Priority**: 🟡 Media

**Sprint 4.1 Total Effort**: ~31 ore

#### Implementation Plan - Sprint 4.2 (1 settimana)

- [ ] **EASC-008**: Diagnostics logging
- [ ] **EASC-009**: Custom formula support
- [ ] **TEST-006**: Full integration testing
- [ ] **REL-014**: Release v1.4.0-beta
- [ ] **DOC-013**: Update main README

**Sprint 4.2 Total Effort**: ~15 ore

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
- [ ] **External Advanced Sensor Configuration (v1.4.0)** - USE VEDI MILESTONE 4

### Technical Debt
- [ ] Rimuovi tutti `_LOGGER.setLevel(logging.DEBUG)`
- [ ] Risolvi TODO in `config_flow.py:567`
- [ ] Refactor constants consolidation
- [ ] Mypy strict mode

---

## 📊 Metriche e KPI

### Development Metrics
| Metrica | Target v1.2.0 | Attuale | Status |
|---------|---------------|---------|--------|
| Test Coverage | >95% | 95.2% | ✅ |
| Pylint Score | >9.5 | 9.83 | ✅ |
| Blueprint Count | 6 | 2 | 🔄 33% |
| Sensor Count | 20 | 12 | 🔄 60% |
| Documentation Pages | 10 | 5 | 🔄 50% |

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
2026-03  ║████░░░░░░░░░░░░░░░░░░░░░░║ Sprint 1.1-1.3
2026-04  ║░░░░████████████░░░░░░░░░░║ Sprint 2.1-2.2
2026-05  ║░░░░░░░░░░░░░░░░████████░░║ Sprint 2.3-2.4
2026-06  ║░░░░░░░░░░░░░░░░░░░░░░████║ Sprint 3.1-3.2
2026-07  ║██░░░░░░░░░░░░░░░░░░░░░░░░║ Sprint 3.3-3.4
2026-08  ║░░██░░░░░░░░░░░░░░░░░░░░░░║ v1.3.0 Release
2026-09  ║░░░░████░░░░░░░░░░░░░░░░░░║ Sprint 4.1 (EASC dev)
2026-10  ║░░░░░░░░████████████░░░░░░║ Sprint 4.2 (EASC testing)
2026-11  ║░░░░░░░░░░░░░░░░░░░░████░░║ v1.4.0 Release (Platinum ready)

Legend: ████ = Active Development
        ░░░░ = Planning/Buffer
```

---

## ✅ Acceptance Criteria

### v1.2.0-beta
- ✅ 3 nuovi blueprint testati e funzionanti
- ✅ 8 nuovi sensori implementati
- ✅ Test coverage >95%
- ✅ Documentation aggiornata
- ✅ No breaking changes per utenti esistenti
- ✅ GitHub release pubblicata con "pre-release" flag

### v1.2.0
- ✅ Tutti criteri v1.2.0-beta
- ✅ 6 blueprint totali disponibili
- ✅ Package dashboard completo
- ✅ Feedback beta integrati
- ✅ Zero bug critici aperti
- ✅ Documentation completa italiano + inglese
- ✅ Marketing communication eseguiti

### v1.3.0
- ✅ Quality Scale Gold certificato
- ✅ Energy Dashboard integration funzionante
- ✅ Scene e script predefiniti
- ✅ Tutte translations complete
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
- ✅ Defined milestones v1.2.0-beta, v1.2.0, v1.3.0
- ✅ Breakdown in sprints with effort estimates
- ✅ Created 3 blueprint proof-of-concepts
- ✅ Documented acceptance criteria

### Next Update: 2026-04-05 (end Sprint 1.1)

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
**Prossima Review**: 2026-04-05
**Documento vivente**: Aggiornare regolarmente con progressi effettivi
