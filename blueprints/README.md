# Blueprint VMC Helty Flow per Home Assistant

Raccolta di blueprint per automatizzare la VMC Helty Flow in Home Assistant.
Per la guida completa su quale blueprint scegliere e come configurarli, vedi [BLUEPRINT_GUIDE.md](BLUEPRINT_GUIDE.md).

---

## 📅 VMC Schedule Plan – Boost giorno/notte base

[![Importa in Home Assistant](https://my.home-assistant.io/redirect/blueprint_import/badge.svg?url=https://raw.githubusercontent.com/darius1907/ha_vmc_helty_flow/main/blueprints/automation/vmc_schedule_plan/vmc_schedule_plan.yaml)](https://my.home-assistant.io/redirect/blueprint_import/?url=https://raw.githubusercontent.com/darius1907/ha_vmc_helty_flow/main/blueprints/automation/vmc_schedule_plan/vmc_schedule_plan.yaml)

Gestisce cicli di boost giorno/notte con velocità fisse configurabili. Nessun sensore richiesto.

- **Giorno**: ogni ora boost (default 75%) per 30 min, poi ritorno al livello base (default 25%)
- **Notte**: ogni 2 ore boost (default 50%) per 15 min, poi ritorno al livello base
- Percentuali e orari completamente configurabili da UI

---

## ⚡ VMC Schedule Boost – Cicli boost avanzati

[![Importa in Home Assistant](https://my.home-assistant.io/redirect/blueprint_import/badge.svg?url=https://raw.githubusercontent.com/darius1907/ha_vmc_helty_flow/main/blueprints/automation/vmc_schedule_plan/vmc_schedule_boost.yaml)](https://my.home-assistant.io/redirect/blueprint_import/?url=https://raw.githubusercontent.com/darius1907/ha_vmc_helty_flow/main/blueprints/automation/vmc_schedule_plan/vmc_schedule_boost.yaml)

Cicli boost periodici con durate configurabili separatamente per giorno e notte. Ottimizza il ricambio d'aria con ventilazione a impulsi.

**Prerequisiti**: helper `input_boolean.vmc_boost_active`

---

## 🌬️ VMC Air Quality Adaptive – Ventilazione adattiva qualità aria

[![Importa in Home Assistant](https://my.home-assistant.io/redirect/blueprint_import/badge.svg?url=https://raw.githubusercontent.com/darius1907/ha_vmc_helty_flow/main/blueprints/automation/vmc_schedule_plan/vmc_air_quality_adaptive.yaml)](https://my.home-assistant.io/redirect/blueprint_import/?url=https://raw.githubusercontent.com/darius1907/ha_vmc_helty_flow/main/blueprints/automation/vmc_schedule_plan/vmc_air_quality_adaptive.yaml)

Regola automaticamente la velocità VMC in base ai livelli di CO2 (e VOC opzionale). Il massimo del comfort intelligente.

**Prerequisiti**: sensore CO2 (integrato VMC o esterno – Netatmo, ESPHome, ecc.)

---

## 💧 VMC Humidity Control – Controllo umidità automatico

[![Importa in Home Assistant](https://my.home-assistant.io/redirect/blueprint_import/badge.svg?url=https://raw.githubusercontent.com/darius1907/ha_vmc_helty_flow/main/blueprints/automation/vmc_schedule_plan/vmc_humidity_control.yaml)](https://my.home-assistant.io/redirect/blueprint_import/?url=https://raw.githubusercontent.com/darius1907/ha_vmc_helty_flow/main/blueprints/automation/vmc_schedule_plan/vmc_humidity_control.yaml)

Attiva il boost VMC automaticamente quando l'umidità supera la soglia configurata (doccia, cottura). Previene muffe e condensa.

**Prerequisiti**: sensore umidità nel bagno o cucina

---

## 🔔 VMC Filter Reminder – Promemoria manutenzione filtro

[![Importa in Home Assistant](https://my.home-assistant.io/redirect/blueprint_import/badge.svg?url=https://raw.githubusercontent.com/darius1907/ha_vmc_helty_flow/main/blueprints/automation/vmc_schedule_plan/vmc_filter_reminder.yaml)](https://my.home-assistant.io/redirect/blueprint_import/?url=https://raw.githubusercontent.com/darius1907/ha_vmc_helty_flow/main/blueprints/automation/vmc_schedule_plan/vmc_filter_reminder.yaml)

Sistema completo di notifiche per la manutenzione del filtro VMC. Avvisi progressivi al 90% (~15970h), 95% (~16857h) e 100% (17744h) della vita del filtro.

**Prerequisiti**: sensore `sensor.vmc_helty_filter_hours` (fornito dall'integrazione)

---

## 🚀 Installazione rapida

1. Clicca il badge "Importa in Home Assistant" del blueprint desiderato
2. Vai su **Impostazioni → Automazioni & Scene → Blueprint**
3. Crea una nuova automazione basata sul blueprint importato
4. Configura i parametri richiesti

Per la guida dettagliata con decision tree e combinazioni consigliate, consulta [BLUEPRINT_GUIDE.md](BLUEPRINT_GUIDE.md).

## 📌 Requisiti generali

- Integrazione VMC Helty Flow installata e configurata
- Entità `fan` della VMC funzionante (`fan.set_percentage` supportato)
