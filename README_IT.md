# 🌬️ VMC Helty Flow - Integrazione Home Assistant

[![hacs][hacsbadge]][hacs]
[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]][license]

[![Project Maintenance][maintenance-shield]][user_profile]
[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]

[![Discord][discord-shield]][discord]
[![Community Forum][forum-shield]][forum]

Integrazione completa per sistemi di Ventilazione Meccanica Controllata (VMC) Helty Flow con Home Assistant.

## 🚀 Installazione Rapida

### Via HACS (Consigliato)

1. **Installa l'Integrazione**:
   - Apri HACS in Home Assistant
   - Vai in **Integrazioni**
   - Clicca sul pulsante **Esplora e scarica repository** in basso a destra
   - Cerca "**VMC Helty Flow**"
   - Clicca su "**Scarica**"
   - Riavvia Home Assistant

   > **Nota**: Se non trovi l'integrazione nella ricerca, potrebbero essere necessarie alcune ore dopo la pubblicazione. In alternativa, puoi aggiungerla come repository personalizzato usando il badge qui sotto:

   [![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=darius1907&repository=ha_vmc_helty_flow&category=integration)

2. **Configura l'Integrazione**:

2. **Configura l'Integrazione**:
   - Vai in **Impostazioni** → **Dispositivi e Servizi**
   - Clicca "**Aggiungi Integrazione**"
   - Cerca "**VMC Helty Flow**"
   - Segui la procedura guidata di configurazione

### Installazione Manuale

1. Copia la cartella `custom_components/vmc_helty_flow` nella tua directory `custom_components/`
2. Riavvia Home Assistant
3. Aggiungi l'integrazione dall'interfaccia

## ✨ Caratteristiche Principali

### 🔍 **Scoperta Dispositivi Avanzata**

- **Scansione Incrementale**: Trova e configura i dispositivi uno alla volta con controllo completo dell'utente
- **Validazione Intelligente**: Controllo automatico di formato subnet, porte e timeout
- **Gestione Errori**: Messaggi informativi e possibilità di recupero dagli errori

### 🎛️ **Controllo Completo VMC**

- **Controllo Ventola**: Velocità variabile e modalità operative
- **Monitoraggio Ambientale**: Temperatura interna/esterna, umidità, CO2, VOC
- **Gestione Filtri**: Monitoraggio ore utilizzo e reset filtro
- **Illuminazione**: Controllo luci integrate con timer
- **Configurazione di Rete**: Gestione WiFi e parametri di rete

## 🏠 Entità Disponibili

### 🌪️ **Controllo Ventilazione**

- **Fan**: Controllo velocità ventola e modalità operative
- **Mode Switch**: Modalità operative (hyperventilation, night, free_cooling)
- **Sensors Switch**: Attivazione/disattivazione sensori ambientali

### 📊 **Sensori Ambientali**

- **Temperatura Interna/Esterna**: Monitoraggio temperature in tempo reale
- **Umidità**: Livelli di umidità ambientale
- **CO2**: Concentrazione anidride carbonica (ppm)
- **VOC**: Composti organici volatili
- **Qualità Aria**: Indicatori complessivi qualità ambientale

### 🔧 **Gestione Sistema**

- **Filter Hours**: Ore di funzionamento filtro
- **Reset Filter Button**: Reset contatore filtro
- **Last Response**: Timestamp ultima comunicazione
- **Panel LED Switch**: Controllo LED pannello frontale

### 💡 **Illuminazione**

- **Light**: Controllo luci integrate
- **Light Timer**: Timer automatico spegnimento luci

### 🌐 **Configurazione di Rete**

- **IP Address**: Indirizzo IP dispositivo
- **Subnet Mask/Gateway**: Parametri di rete
- **SSID/Password**: Configurazione WiFi
- **Network Settings**: Gestione completa parametri di rete

### 📈 **Sensori Avanzati**

- **Dew Point**: Calcolo punto di rugiada per prevenzione condensa
- **Comfort Index**: Indice di comfort basato su temperatura e umidità
- **Dew Point Delta**: Differenza tra temperatura esterna e punto rugiada
- **Air Exchange Time**: Tempo di ricambio aria basato su velocità ventola
- **Daily Air Changes**: Numero ricambi d'aria giornalieri

## 🎨 **Dashboard Personalizzata**

### 📱 **VMC Helty Control Card**

Card Lovelace personalizzata per controllo completo del sistema VMC:

- **🎛️ Controllo Ventola**: Interfaccia intuitiva con pulsanti velocità (0-4)
- **📊 Monitor Ambientale**: Visualizzazione sensori con indicatori colorati
- **🔄 Aggiornamenti Real-time**: Stato ventola e sensori in tempo reale
- **� Design Responsive**: Ottimizzato per mobile, tablet e desktop
- **🎨 Temi Multipli**: Default, Compact, Minimal
- **⚙️ Configurazione Visuale**: Editor grafico integrato in Lovelace

#### Installazione Card

```bash
# Copia i file della card in www/
/config/www/vmc-helty-card/
├── vmc-helty-card.js              # Card principale
└── vmc-helty-card-editor.js       # Editor configurazione
```

Aggiungi alle risorse Lovelace:

```yaml
resources:
  - url: /local/vmc-helty-card/vmc-helty-card.js
    type: module
  - url: /local/vmc-helty-card/vmc-helty-card-editor.js
    type: module
```

**Nota**: I file di traduzione vengono caricati automaticamente e NON devono essere aggiunti alle risorse.

Configurazione card:

```yaml
type: custom:vmc-helty-card
entity: fan.vmc_helty
name: "VMC Living Room"
show_temperature: true
show_humidity: true
show_co2: true
show_voc: true
```

## �🚀 Configurazione Guidata

### 📡 **Scansione Incrementale**

1. **Avvio Configurazione**
   - Apri Home Assistant → Impostazioni → Dispositivi e Servizi
   - Clicca "Aggiungi Integrazione" → Cerca "VMC Helty Flow"

2. **Configurazione Scansione**
   - **Subnet**: Inserisci la rete da scansionare (es. `192.168.1.0/24`)
   - **Porta**: Porta TCP del dispositivo VMC (default: `5001`)
   - **Timeout**: Timeout connessione in secondi (1-60)
   - **Modalità**: Seleziona "Scansione incrementale"

3. **Processo Incrementale**
   - La scansione inizia e si ferma automaticamente ad ogni dispositivo trovato
   - Per ogni dispositivo VMC scoperto, puoi scegliere:
     - **➕ Aggiungi e continua**: Aggiunge il dispositivo e prosegue la scansione
     - **⏭️ Salta e continua**: Ignora questo dispositivo e prosegue
     - **✅ Aggiungi e termina**: Aggiunge il dispositivo e termina
     - **🛑 Termina scansione**: Ferma tutto senza aggiungere

4. **Feedback Immediato**

- Visualizzazione in tempo reale dei dispositivi trovati
- Informazioni dettagliate (nome, IP, modello) per ogni dispositivo
- Contatore progressivo e indicatore posizione nella scansione

### 🔧 **Validazioni e Sicurezza**

- **Formato Subnet**: Validazione automatica formato CIDR
- **Limite IP**: Massimo 254 indirizzi per scansione (per performance)
- **Controllo Porte**: Validazione range porte (1-65535)
- **Timeout Intelligente**: Bilanciamento tra velocità e affidabilità
- **Gestione Duplicati**: Prevenzione configurazioni duplicate automatica

## 📋 **Esempi di Configurazione**

### Configurazione Base

```text
Subnet: 192.168.1.0/24
Porta: 5001
Timeout: 10 secondi
```

### Configurazione Rete Personalizzata

```text
Subnet: 10.0.0.0/24
Porta: 8080
Timeout: 5 secondi
Modalità: Scansione completa
```

### Configurazione Rete Estesa

```text
Subnet: 192.168.0.0/23
Porta: 5001
Timeout: 15 secondi
```

## 🔄 **Automazioni e Integrazioni**

Tutte le entità sono completamente integrate con Home Assistant:

### Automazione Qualità Aria

```yaml
automation:
  - alias: "VMC Boost su CO2 Alto"
    trigger:
      platform: numeric_state
      entity_id: sensor.vmc_helty_soggiorno_co2
      above: 800
    action:
      service: fan.set_percentage
      target:
        entity_id: fan.vmc_helty_soggiorno
      data:
        percentage: 80
```

### Dashboard Personalizzata

```yaml
cards:
  - type: entities
    title: "Controllo VMC Soggiorno"
    entities:
      - fan.vmc_helty_soggiorno
      - sensor.vmc_helty_soggiorno_temperatura_interna
      - sensor.vmc_helty_soggiorno_co2
      - switch.vmc_helty_soggiorno_modalita
      - light.vmc_helty_soggiorno_luce
```

## 🛠️ **Risoluzione Problemi**

### Problemi Comuni

**Dispositivi non trovati?**

- Verifica che i dispositivi VMC siano accesi e connessi alla rete
- Controlla che la subnet sia corretta
- Prova ad aumentare il timeout di connessione
- Verifica che la porta 5001 non sia bloccata dal firewall

**Scansione lenta?**

- Riduci la subnet (es. da /23 a /24)
- Diminuisci il timeout per reti veloci
- Usa la modalità incrementale per controllo granulare

**Errori di connessione?**

- Verifica la configurazione di rete del dispositivo VMC
- Controlla che Home Assistant possa raggiungere la subnet specificata
- Prova a riavviare il dispositivo VMC

### Log e Debug

Per abilitare log dettagliati, aggiungi al `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.vmc_helty_flow: debug
```

## 🔮 **Prossimi Sviluppi**

Abbiamo una roadmap di sviluppo attiva con funzionalità entusiasmanti in programma!

### 📋 Risorse di Sviluppo

- **[Roadmap Progetto](PROJECT_ROADMAP.md)** - Piano di sviluppo dettagliato con milestone, task e tracciamento progressi
- **[Piano Miglioramenti](IMPROVEMENT_PLAN.md)** - Analisi completa e miglioramenti proposti per le prossime versioni
- **[Guida Blueprint](blueprints/BLUEPRINT_GUIDE.md)** - Documentazione completa blueprint automazioni

### 🎯 Funzionalità in Arrivo (v1.2.0+)

**Priorità Alta**:
- 🔔 **Sistema Notifiche**: Alerting completo per eventi critici (filtro, qualità aria, offline)
- 📘 **6 Nuovi Blueprint Automazioni**: Adattamento qualità aria, controllo umidità, promemoria filtro e altro
- 📊 **Sensori Statistici**: Percentuale vita filtro, stima consumi energetici, tempo funzionamento
- 📦 **Package Dashboard Pronto**: Package completo importabile con helper, automazioni e viste

**Priorità Media** (v1.3.0):
- ⭐ **Quality Scale Gold**: Upgrade da Silver a certificazione Gold
- ⚡ **Integrazione Energy Dashboard**: Traccia consumi VMC nel pannello Energia di Home Assistant
- 🎭 **Scene Predefinite**: Modalità notte, boost, risparmio energetico

**Richieste Community**:
- 🤖 Machine Learning per predizione qualità aria
- 🗣️ Integrazioni avanzate assistenti vocali
- 📱 App companion mobile
- 🌐 Coordinamento VMC multi-zona

Consulta la [roadmap completa](PROJECT_ROADMAP.md) per timeline dettagliata e suddivisione task.

## 📞 **Supporto**

Per problemi, richieste di funzionalità o contributi:

- 🐛 [Apri una issue](https://github.com/darius1907/ha_vmc_helty_flow/issues) su GitHub
- 💬 Unisciti alla [discussione della community](https://community.home-assistant.io/)

### Come Contribuire

Accogliamo con piacere i contributi! Consulta le [Linee Guida per Contribuire](CONTRIBUTING.md) e la [Roadmap Progetto](PROJECT_ROADMAP.md) per le priorità correnti.

1. 🍴 Fork del repository
2. 🌱 Crea un branch per la feature
3. ✅ Aggiungi test per le modifiche (coverage >95%)
4. 📝 Aggiorna la documentazione
5. 🎯 Controlla [PROJECT_ROADMAP.md](PROJECT_ROADMAP.md) per i task prioritari
6. 🔄 Invia una pull request

---

## 📊 **Stato del Progetto**

![GitHub release (latest by date)][releases-shield]
![GitHub Release Date][release-date-shield]
![GitHub commits since latest release][commits-since-shield]
![GitHub last commit][last-commit-shield]

**Versione**: 1.0.0-RC2
**Compatibilità**: Home Assistant 2024.1+
**Licenza**: MIT
**Stato HACS**: ✅ Disponibile nel repository ufficiale HACS

---

**⭐ Se questa integrazione ti è utile, metti una stella al repository!**

**☕ Ti piace questa integrazione? Offrimi un caffè!**

[![Buy Me A Coffee](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/darius1907)

Il tuo supporto mi aiuta a mantenere e migliorare questa integrazione!

[hacs]: https://github.com/hacs/integration
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[discord]: https://discord.gg/Qa5fW2R
[discord-shield]: https://img.shields.io/discord/330944238910963714.svg?style=for-the-badge
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
[license]: https://github.com/darius1907/ha_vmc_helty_flow/blob/main/LICENSE
[license-shield]: https://img.shields.io/github/license/darius1907/ha_vmc_helty_flow.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-%40darius1907-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/darius1907/ha_vmc_helty_flow.svg?style=for-the-badge
[releases]: https://github.com/darius1907/ha_vmc_helty_flow/releases
[commits-shield]: https://img.shields.io/github/commit-activity/y/darius1907/ha_vmc_helty_flow.svg?style=for-the-badge
[commits]: https://github.com/darius1907/ha_vmc_helty_flow/commits/main
[user_profile]: https://github.com/darius1907
[buymecoffee]: https://www.buymeacoffee.com/darius1907
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge
[release-date-shield]: https://img.shields.io/github/release-date/darius1907/ha_vmc_helty_flow?style=for-the-badge
[commits-since-shield]: https://img.shields.io/github/commits-since/darius1907/ha_vmc_helty_flow/latest?style=for-the-badge
[last-commit-shield]: https://img.shields.io/github/last-commit/darius1907/ha_vmc_helty_flow?style=for-the-badge
