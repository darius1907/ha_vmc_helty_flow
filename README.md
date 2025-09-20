# 🌬️ VMC Helty Flow - Integrazione Home Assistant

Integrazione completa per sistemi di Ventilazione Meccanica Controllata (VMC) Helty Flow con Home Assistant.

## ✨ Caratteristiche Principali

### 🔍 **Scoperta Dispositivi Avanzata**
- **Scansione Incrementale**: Trova e configura i dispositivi uno alla volta con controllo completo dell'utente
- **Scansione Completa**: Scansiona l'intera rete e seleziona tutti i dispositivi alla fine
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

## 🚀 Configurazione Guidata

L'integrazione offre due modalità di configurazione per adattarsi alle diverse esigenze:

### 📡 **Modalità Scansione Incrementale** (Consigliata)

**Perfetta per reti con molti dispositivi o quando vuoi controllo completo**

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

### ⚡ **Modalità Scansione Completa**

**Ideale per reti semplici o quando conosci già i tuoi dispositivi**

1. **Configurazione Rapida**
   - Stessi parametri della modalità incrementale
   - Seleziona "Scansione completa"

2. **Scansione Automatica**
   - Scansiona automaticamente tutta la subnet
   - Mostra progresso con barra di avanzamento
   - Possibilità di interrompere in qualsiasi momento

3. **Selezione Dispositivi**
   - Al termine, mostra tutti i dispositivi trovati
   - Seleziona quali dispositivi configurare
   - Conferma per completare la configurazione

### 🔧 **Validazioni e Sicurezza**

- **Formato Subnet**: Validazione automatica formato CIDR
- **Limite IP**: Massimo 254 indirizzi per scansione (per performance)
- **Controllo Porte**: Validazione range porte (1-65535)
- **Timeout Intelligente**: Bilanciamento tra velocità e affidabilità
- **Gestione Duplicati**: Prevenzione configurazioni duplicate automatica

## 📋 **Esempi di Configurazione**

### Configurazione Base
```
Subnet: 192.168.1.0/24
Porta: 5001
Timeout: 10 secondi
Modalità: Scansione incrementale
```

### Configurazione Rete Personalizzata
```
Subnet: 10.0.0.0/24
Porta: 8080
Timeout: 5 secondi
Modalità: Scansione completa
```

### Configurazione Rete Estesa
```
Subnet: 192.168.0.0/23
Porta: 5001
Timeout: 15 secondi
Modalità: Scansione incrementale (consigliata per reti grandi)
```

## 🔄 **Automazioni e Integrazioni**

Tutte le entità sono completamente integrate con Home Assistant:

### Automazione Qualità Aria
```yaml
automation:
  - alias: "VMC Boost su CO2 Alto"
    trigger:
      platform: numeric_state
      entity_id: sensor.soggiorno_co2
      above: 800
    action:
      service: fan.set_percentage
      target:
        entity_id: fan.soggiorno_vmc
      data:
        percentage: 80
```

### Dashboard Personalizzata
```yaml
cards:
  - type: entities
    title: "Controllo VMC Soggiorno"
    entities:
      - fan.soggiorno_vmc
      - sensor.soggiorno_temperatura_interna
      - sensor.soggiorno_co2
      - switch.soggiorno_modalita
      - light.soggiorno_luce_vmc
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

- **Rilevamento Automatico**: Discovery automatico dispositivi nella rete locale
- **Profili Stagionali**: Configurazioni automatiche estate/inverno
- **Integrazioni Avanzate**: Collegamento con sensori esterni e stazioni meteo
- **Dashboard Dedicata**: Interface utente specializzata per controllo VMC

## 📞 **Supporto**

Per problemi, richieste di funzionalità o contributi:
- Apri una issue su GitHub
- Fornisci log dettagliati per problemi di connessione
- Includi informazioni sul modello VMC e configurazione di rete

---

**Versione**: 2.0.0
**Compatibilità**: Home Assistant 2024.1+
**Licenza**: MIT
