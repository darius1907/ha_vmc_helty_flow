# 📘 VMC Helty Flow - Guida Completa Blueprint

## 📑 Indice
1. [Blueprint Disponibili](#blueprint-disponibili)
2. [Come Scegliere](#come-scegliere-il-blueprint-giusto)
3. [Installazione](#installazione)
4. [Configurazione](#configurazione-dettagliata)
5. [Esempi Pratici](#esempi-pratici)
6. [Troubleshooting](#troubleshooting)
7. [FAQ](#faq)

---

## Blueprint Disponibili

### 1. 📅 VMC Schedule Plan
**File**: `vmc_schedule_plan.yaml`
**Complessità**: ⭐ Facile
**Sensori richiesti**: Nessuno

Gestisce cicli giorno/notte con velocità fisse configurabili.

**Pro**: Semplicità, affidabilità, no sensori
**Contro**: Non si adatta a condizioni variabili

**Quando usarlo**:
- Prima automazione VMC
- Pattern utilizzo casa regolare
- Non hai sensori aggiuntivi

---

### 2. ⚡ VMC Schedule Boost
**File**: `vmc_schedule_boost.yaml`
**Complessità**: ⭐⭐ Media
**Sensori richiesti**: input_boolean helper

Cicli boost periodici con durate configurabili separatamente per giorno/notte.

**Pro**: Ottimizza ricambio aria, risparmio energetico
**Contro**: Richiede helper, setup più complesso

**Quando usarlo**:
- Vuoi boost periodici automatici
- Preferisci ventilazione a impulsi
- Ottimizzazione energetica

**Setup prerequisiti**:
```yaml
input_boolean:
  vmc_boost_active:
    name: "VMC Boost Attivo"
```

---

### 3. 🌬️ VMC Air Quality Adaptive 🆕
**File**: `vmc_air_quality_adaptive.yaml`
**Complessità**: ⭐⭐⭐ Avanzata
**Sensori richiesti**: CO2 sensor (VOC opzionale)

Regola velocità automaticamente in base a qualità aria reale.

**Pro**: Massimo comfort, intelligente, efficiente
**Contro**: Richiede sensori affidabili, setup complesso

**Logica**:
- CO2 < 800 ppm → Velocità minima (25%)
- CO2 800-1000 ppm → Velocità media (50%)
- CO2 > 1000 ppm → Velocità alta (75%) o Hyperventilation
- VOC alti → Boost indipendente

**Quando usarlo**:
- Hai sensori CO2/VOC
- Occupazione casa variabile
- Vuoi massima qualità aria

**Sensori compatibili**:
- `sensor.vmc_helty_co2` (integrato VMC)
- Sensori CO2 esterni (Netatmo, ESPHome, etc.)
- `sensor.vmc_helty_voc` (opzionale)

---

### 4. 💧 VMC Humidity Control 🆕
**File**: `vmc_humidity_control.yaml`
**Complessità**: ⭐⭐ Media
**Sensori richiesti**: Humidity sensor

Boost automatico quando umidità supera soglia (doccia, cucina).

**Pro**: Previene muffa, automatico, personalizzabile
**Contro**: Richiede sensore umidità affidabile

**Logica**:
1. Umidità > soglia (es. 70%) → Attiva boost 100%
2. Mantieni boost per durata minima (es. 15 min)
3. Se umidità ancora alta → Estendi boost
4. Umidità < soglia ritorno (es. 60%) → Torna a velocità normale
5. Cooldown opzionale prima di nuovo boost

**Quando usarlo**:
- Bagno con doccia
- Cucina  con cottura frequente
- Problemi muffa/condensa

**Sensori compatibili**:
- `sensor.vmc_helty_humidity` (VMC integrato)
- Aqara, Xiaomi, ESPHome humidity sensors
- Sensori multi-sensore (temp+hum)

---

### 5. 🔔 VMC Filter Reminder 🆕
**File**: `vmc_filter_reminder.yaml`
**Complessità**: ⭐ Facile
**Sensori richiesti**: sensor.vmc_helty_filter_hours

Sistema completo notifiche manutenzione filtro.

**Pro**: Non dimentichi mai, notifiche multiple, statistiche
**Contro**: Nessuno

**Notifiche**:
- **90% (~15970h)**: Avviso preventivo
- **95% (~16857h)**: Allerta critica
- **100% (17744h)**: Promemoria giornaliero urgente

**Canali notifica supportati**:
- ✅ Persistent notification (UI Home Assistant)
- ✅ Mobile app notifications (iOS/Android)
- ✅ Email
- ✅ Telegram (configurabile)
- ✅ Action buttons per reset rapido

**Quando usarlo**:
- Sempre! È un must-have
- Non costa nulla in termini di performance
- Prolunga vita VMC

---

## Come Scegliere il Blueprint Giusto

### 🎯 Decision Tree

```
Hai sensori CO2/VOC?
├─ SÌ → Usa "Air Quality Adaptive" (massimo comfort)
│   └─ + "Humidity Control" per bagno/cucina
│   └─ + "Filter Reminder" per manutenzione
│
└─ NO → Hai sensore umidità in bagno?
    ├─ SÌ → Usa "Schedule Plan" base
    │   └─ + "Humidity Control" per boost doccia
    │   └─ + "Filter Reminder"
    │
    └─ NO → Usa "Schedule Plan" o "Schedule Boost"
        └─ + "Filter Reminder" (sempre!)
```

### 💡 Combinazioni Consigliate

#### Setup Minimo (Senza Sensori)
```
✅ VMC Schedule Plan
✅ VMC Filter Reminder
```
**Risultato**: Automazione giorno/notte + notifiche filtro

#### Setup Bagno/Cucina
```
✅ VMC Schedule Plan
✅ VMC Humidity Control (bagno)
✅ VMC Filter Reminder
```
**Risultato**: Base giorno/notte + boost doccia automatico

#### Setup Completo (Con Sensori)
```
✅ VMC Air Quality Adaptive
✅ VMC Humidity Control
✅ VMC Filter Reminder
```
**Risultato**: Intelligenza massima + comfort ottimale

#### Setup Risparmio Energetico
```
✅ VMC Schedule Boost (cicli periodici)
✅ VMC Filter Reminder
```
**Risultato**: Ventilazione a impulsi + manutenzione

---

## Installazione

### Metodo 1: Import Automatico (Consigliato) ✨

1. Click sul badge "Import Blueprint" nella documentazione
2. Home Assistant apre automaticamente la pagina import
3. Click "Preview Blueprint"
4. Click "Import Blueprint"
5. ✅ Fatto!

### Metodo 2: Import da URL

1. Settings → Automations & Scenes
2. Tab "Blueprints"
3. Click "Import Blueprint" (angolo basso a destra)
4. Incolla URL:
   ```
   https://raw.githubusercontent.com/darius1907/ha_vmc_helty_flow/main/blueprints/automation/vmc_schedule_plan/[nome_file].yaml
   ```
5. Click "Preview Blueprint"
6. Click "Import Blueprint"

**URLs disponibili**:
- Schedule Plan: `...vmc_schedule_plan.yaml`
- Schedule Boost: `...vmc_schedule_boost.yaml`
- Air Quality: `...vmc_air_quality_adaptive.yaml`
- Humidity: `...vmc_humidity_control.yaml`
- Filter Reminder: `...vmc_filter_reminder.yaml`

### Metodo 3: File Manuale (Avanzato)

1. Connetti via SSH o File Editor
2. Copia file blueprint in:
   ```
   /config/blueprints/automation/vmc_schedule_plan/[nome_file].yaml
   ```
3. Developer Tools → YAML → Check Configuration
4. Restart Home Assistant

---

## Configurazione Dettagliata

### 1. Creare Automazione da Blueprint

1. Settings → Automations & Scenes
2. Tab "Automations"
3. Click "+ Create Automation"
4. Scroll giù → "Start with a blueprint"
5. Seleziona blueprint VMC desiderato
6. Compila campi obbligatori
7. Personalizza opzionali
8. Click "Save"
9. Dai nome descrittivo (es. "VMC - Boost Automatico Doccia")

### 2. Configurazione Campi Comuni

#### Campo: Entità VMC ⚠️ OBBLIGATORIO
```
Tipo: Entity selector (domain: fan)
Esempio: fan.vmc_helty_soggiorno
```

**Come trovare entità corretta**:
1. Developer Tools → States
2. Cerca "vmc_helty"
3. Copia entity_id che inizia con `fan.`

#### Campo: Sensori
```
CO2: sensor.vmc_helty_co2
Humidity: sensor.vmc_helty_humidity
VOC: sensor.vmc_helty_voc
```

**Se hai sensori esterni**:
```
CO2: sensor.netatmo_co2
Humidity: sensor.aqara_bathroom_humidity
```

#### Campo: Velocità
```
Formato: Percentuale (0-100)
Step: 25% (allineato a speed VMC 0-4)

0% = Spento
25% = Velocità 1
50% = Velocità 2
75% = Velocità 3
100% = Velocità 4
```

### 3. Setup Helper (quando richiesti)

Alcuni blueprint richiedono input_boolean o input_number.

**Via UI** (Raccomandato):
1. Settings → Devices & Services
2. Tab "Helpers"
3. "+ Create Helper"
4. Seleziona "Toggle" (input_boolean) o "Number" (input_number)
5. Compila nome e icona
6. Save

**Via YAML**:
```yaml
# configuration.yaml
input_boolean:
  vmc_boost_active:
    name: "VMC Boost Attivo"
    icon: mdi:fan-chevron-up

  vmc_auto_mode:
    name: "VMC Modalità Automatica"
    icon: mdi:auto-mode

input_number:
  vmc_target_co2:
    name: "Target CO2"
    min: 400
    max: 1500
    step: 50
    unit_of_measurement: "ppm"
```

Dopo modifica YAML: Developer Tools → YAML → Restart

---

## Esempi Pratici

### Esempio 1: Casa singola, 2 persone, work from home

**Obiettivo**: Qualità aria ottimale durante giorno, risparmio notte

**Blueprint**: Air Quality Adaptive + Humidity Control

**Configurazione**:
```yaml
Air Quality Adaptive:
  VMC: fan.vmc_helty_soggiorno
  Sensore CO2: sensor.vmc_helty_co2
  Soglia Bassa: 700 ppm
  Soglia Alta: 1000 ppm
  Velocità Minima: 25%
  Velocità Media: 50%
  Velocità Alta: 100%
  Hyperventilation: Sì
  Delay: 5 minuti

Humidity Control:
  VMC: fan.vmc_helty_bagno
  Sensore: sensor.bathroom_humidity
  Soglia Boost: 75%
  Soglia Ritorno: 60%
  Durata Minima: 20 minuti
  Velocità Boost: 100%
```

**Risultato**:
- CO2 si mantiene < 800 ppm durante lavoro
- Boost automatico doccia mattina/sera
- Risparmio energetico quando aria è buona

---

### Esempio 2: Appartamento, fuori casa 9-18

**Obiettivo**: Risparmio energetico, ventilazione minima quando fuori

**Blueprint**: Schedule Plan + Presence Based (futuro)

**Configurazione**:
```yaml
Schedule Plan:
  VMC: fan.vmc_helty
  Ora Giorno: 06:00
  Ora Notte: 23:00
  Velocità Giorno: 50%
  Velocità Notte: 25%
```

**Miglioramento futuro con presenza**:
- Casa occupata → 50%
- Casa vuota → 25%
- Delay 15 minuti

---

### Esempio 3: Villa multi-piano con cucina open space

**Obiettivo**: Gestione umidità cucina, qualità aria soggiorno

**Blueprint**: Air Quality + Humidity Control x2

**Configurazione**:
```yaml
Air Quality (Soggiorno):
  VMC: fan.vmc_helty_soggiorno
  CO2: sensor.living_room_co2
  Soglie: 800/1000 ppm

Humidity Control (Cucina):
  VMC: fan.vmc_helty_cucina
  Humidity: sensor.kitchen_humidity
  Soglia: 70%
  Durata: 30 minuti (cucina = cotture lunghe)

Humidity Control (Bagno):
  VMC: fan.vmc_helty_bagno
  Humidity: sensor.bathroom_humidity
  Soglia: 75%
  Durata: 15 minuti (doccia = boost breve)
```

---

## Troubleshooting

### ❌ Blueprint non appare in lista

**Causa**: File non nel percorso corretto o sintassi YAML invalida

**Soluzione**:
1. Verifica percorso: `/config/blueprints/automation/vmc_schedule_plan/`
2. Controlla sintassi YAML: [YAML Lint](http://www.yamllint.com/)
3. Developer Tools → YAML → Check Configuration
4. Restart Home Assistant
5. Refresh cache browser (Ctrl+F5)

---

### ❌ Automazione non si attiva

**Causa 1**: Condition blocking

**Soluzione**:
1. Apri automazione
2. Click 3 puntini → "Information"
3. Controlla "Last triggered" (deve aggiornarsi)
4. Se presente condition/blackout, verifica sia nell'ora corretta

**Causa 2**: Entity non trovata

**Soluzione**:
1. Developer Tools → States
2. Cerca entity configurata
3. Verifica nome esatto (case sensitive)
4. Controlla entity abilitata (può essere disabled di default)

**Causa 3**: Trigger non configurato correttamente

**Soluzione**:
1. Abilita "Trace" nell'automazione
2. Attiva manualmente: "Run actions"
3. Controlla log per errori specifici

---

### ❌ Velocità VMC non cambia

**Causa**: Entity VMC non supporta set_percentage

**Soluzione**:
1. Developer Tools → States
2. Cerca `fan.vmc_helty_*`
3. Verifica "supported_features" include "set_percentage"
4. Se no, aggiorna integrazione VMC Helty Flow

---

### ❌ Notifiche non arrivano

**Causa**: Servizio notify non configurato o non esistente

**Soluzione**:
1. Developer Tools → States
2. Cerca "notify." → Verifica servizi disponibili
3. Se usi mobile app: Settings → Companion App → Ensure notifications enabled
4. Testa servizio manualmente:
   ```yaml
   service: notify.mobile_app_iphone
   data:
     message: "Test"
   ```
5. Se non funziona, riconfigura app companion

---

### ❌ Helper non disponibile

**Causa**: input_boolean/input_number non creato

**Soluzione**:
1. Settings → Devices & Services → Helpers
2. "+ Create Helper"
3. Seleziona tipo corretto
4. Nome deve corrispondere esattamente al blueprint

**Alternativa YAML**:
```yaml
# configuration.yaml
input_boolean:
  vmc_boost_active:
    name: "VMC Boost Attivo"
```
Poi: Developer Tools → YAML → Restart

---

### ❌ Boost rimane attivo troppo a lungo

**Causa**: Soglia ritorno troppo bassa o sensore impreciso

**Soluzione Humidity Control**:
1. Aumenta "Soglia Ritorno" (es. da 60% a 65%)
2. Riduci "Durata Massima" (safety timeout)
3. Verifica calibrazione sensore umidità

**Soluzione Air Quality**:
1. Aumenta "Delay" (es. da 3 a 10 minuti)
2. Verifica posizionamento sensore CO2 (lontano da finestre)

---

### ❌ Oscillazioni continue velocità

**Causa**: Delay troppo basso o soglie troppo vicine

**Soluzione**:
1. Aumenta "Delay" (Air Quality: da 3 a 10 minuti)
2. Allarga gap tra soglie (es. 800-1000 → 750-1050)
3. Usa mode: "single" invece di "restart"

---

## FAQ

### Q: Posso usare più blueprint contemporaneamente?
**A**: Sì, ma attenzione a conflitti! Esempio OK:
- Schedule Plan (base giorno/notte)
- Humidity Control (boost doccia)
- Filter Reminder (notifiche)

Esempio ❌ CONFLITTO:
- Schedule Plan + Air Quality Adaptive (combattono per velocità)

**Soluzione conflitti**: Usa condition per separare contesti o scegli uno solo.

---

### Q: Blueprint funziona con altri VMC (non Helty)?
**A**: Alcuni sì, se supportano:
- `fan.set_percentage` service
- Entity domain `fan`
- Percentuale 0-100%

Testa manualmente prima:
```yaml
service: fan.set_percentage
target:
  entity_id: fan.tua_vmc
data:
  percentage: 50
```

---

### Q: Come disabilito temporaneamente automazione?
**A**:
1. Settings → Automations
2. Trova automazione
3. Toggle switch OFF
4. Ripristina quando vuoi

**Alternativa**: Usa input_boolean per enable/disable condizionale:
```yaml
condition:
  - condition: state
    entity_id: input_boolean.vmc_auto_mode
    state: 'on'
```

---

### Q: Posso modificare blueprint dopo import?
**A**: Sì, 2 metodi:

**Metodo 1** (Modifica automazione):
- Apri automazione creata
- Click "Edit" → Modifica parametri
- Save

**Metodo 2** (Modifica blueprint):
- File Editor o SSH
- Naviga a `/config/blueprints/automation/vmc_schedule_plan/[file].yaml`
- Modifica e salva
- Restart Home Assistant
- Ricrea automazioni

---

### Q: Blueprint supporta multi-VMC?
**A**: Sì! Crea automazione separata per ogni VMC:

```
Automazione 1: "VMC Soggiorno - Air Quality"
  Entity: fan.vmc_helty_soggiorno

Automazione 2: "VMC Camera - Air Quality"
  Entity: fan.vmc_helty_camera
```

---

### Q: Come monitoro efficacia blueprint?
**A**: Usa dashboard dedicata:

```yaml
type: vertical-stack
cards:
  - type: logbook
    entities:
      - automation.vmc_automazione
    hours_to_show: 24

  - type: history-graph
    entities:
      - sensor.vmc_helty_co2
      - fan.vmc_helty
    hours_to_show: 24

  - type: entity
    entity: automation.vmc_automazione
    attribute: last_triggered
```

Analizza:
- Frequency trigger (quanto spesso si attiva)
- Correlation tra trigger e qualità aria
- Consumi energetici stimati

---

### Q: Blueprint funziona offline/senza internet?
**A**: ✅ Sì! Tutti i blueprint sono 100% locali:
- No cloud necessario
- No API esterne
- Funziona anche con HA offline

**Eccezione**: Notifiche push mobile richiedono internet per delivery (ma automazione funziona comunque).

---

### Q: Come contribuisco con nuovo blueprint?
**A**:
1. Fork repository GitHub
2. Crea blueprint in `/blueprints/automation/vmc_schedule_plan/`
3. Testa accuratamente
4. Documenta caso d'uso
5. Pull Request
6. Review e merge

Vedi [CONTRIBUTING.md](../CONTRIBUTING.md) per details.

---

## 🔗 Link Utili

- **Repository**: [GitHub](https://github.com/darius1907/ha_vmc_helty_flow)
- **Issues**: [Report Bug](https://github.com/darius1907/ha_vmc_helty_flow/issues)
- **Discussions**: [Community](https://github.com/darius1907/ha_vmc_helty_flow/discussions)
- **Documentazione**: [README principale](../README.md)
- **Piano Miglioramenti**: [Roadmap](../IMPROVEMENT_PLAN.md)

---

## 📝 Changelog Blueprint

### v1.2.0 (2026-03-23)
- ✨ Aggiunto: VMC Air Quality Adaptive
- ✨ Aggiunto: VMC Humidity Control
- ✨ Aggiunto: VMC Filter Reminder
- 📚 Aggiunto: Guida completa blueprint

### v1.0.0 (2024-09-24)
- 🎉 Rilascio iniziale: VMC Schedule Plan
- 🎉 Rilascio iniziale: VMC Schedule Boost

---

**Autore**: VMC Helty Flow Development Team
**Licenza**: MIT
**Ultima revisione**: 2026-03-23
