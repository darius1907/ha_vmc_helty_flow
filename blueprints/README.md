# VMC Boost Giorno/Notte – Blueprint per Home Assistant

[![Importa in Home Assistant](https://my.home-assistant.io/redirect/blueprint_import/badge.svg?url=https://raw.githubusercontent.com/darius1907/ha_vmc_helty_flow/main/blueprints/automation/vmc_schedule_plan/vmc_schedule_plan.yaml)](https://my.home-assistant.io/redirect/blueprint_import/?url=https://raw.githubusercontent.com/darius1907/ha_vmc_helty_flow/main/blueprints/automation/vmc_schedule_plan/vmc_schedule_plan.yaml)

## ✨ Funzionalità
- **Giorno**: ogni ora boost (default 75%) per 30 min, poi ritorno al livello base (default 25%)
- **Notte**: ogni 2 ore boost (default 50%) per 15 min, poi ritorno al livello base
- Supporta anche la modalità **100% (Max)** configurabile da UI

## 🚀 Installazione
1. Copia il file nella tua installazione Home Assistant:

config/blueprints/automation/vmc_schedule_plan/vmc_schedule_plan.yaml

oppure importa direttamente con il badge sopra ⬆️

2. Dopo l’import vai su  
**Impostazioni → Automazioni & Scene → Blueprint**  
e crea una nuova automazione basata su `VMC Boost Giorno/Notte`.

## ⚙️ Configurazione
- **VMC Fan**: entità `fan` della VMC
- **Percentuali configurabili**: Low (25%), Medium (50%), High (75%), Max (100%)
- **Orario giorno/notte**: personalizzabili
- **Durata boost giorno/notte**: regolabili da UI

## 📌 Requisiti
- Il tuo fan deve supportare `fan.set_percentage`
