# Specifiche Funzionali del Progetto VMC Control

## Panoramica
Il progetto vmc_helty_flow è un'integrazione per home assistant per rilevare nella subnet locale i dispositivi VMC Helty Flow (Ventilazione Meccanica Controllata) 
L'applicazione offre inoltre una dashboard lovelace per la gestione e il monitoraggio dello stato in tempo reale e controllo delle principali impostazioni.
L'obiettivo è fornire un'interfaccia utente intuitiva e centralizzata per la gestione dei dispositivi VMC, semplificando la configurazione e il monitoraggio.

## Architettura
L'applicazione è un custom component per Home Assistant, sviluppato in Python, che utilizza protocolli di rete per comunicare con i dispositivi VMC Helty Flow.
L'architettura si basa su una scansione della rete locale per individuare i dispositivi VMC, seguita da una gestione centralizzata delle connessioni e dello stato dei dispositivi.
L'interfaccia utente è realizzata tramite una dashboard lovelace personalizzata, che consente di visualizzare lo stato dei dispositivi e di inviare comandi.


## Funzionalità Dettagliate

### 1. Discovery dei Dispositivi
- **Scansione della rete**:
    - L'applicazione esegue una scansione asincrona della subnet locale (192.168.1.1-192.168.1.254) sulla porta 5001 per identificare i dispositivi VMC attivi.
    - Utilizza Socket TCP/IP asincroni per gestire connessioni multiple simultaneamente.
    - Implementa timeout configurabili per ogni tentativo di connessione, garantendo una scansione fluida ed efficiente.
    - La scansione viene eseguita in un isolate separato per non bloccare l'interfaccia utente.
    - La scansione viene eseguita tentando l'invio di un comando di stato `VMGH?` a ogni indirizzo IP della subnet e aspetta una risposta valida, 
    - Quando riceve una risposta valida considera il dispositivo come VMC ed effettua anche il comando VMNM? per ottenere il nome del dispositivo.
    - Ogni dispositivo rilevato viene aggiunto a una lista di dispositivi VMC.
    - La scansione termina quando tutti gli indirizzi IP della subnet sono stati tentati.
    - La scansione può essere interrotta manualmente dall'utente in qualsiasi momento.
    - La scansione può essere riavviata manualmente dall'utente in qualsiasi momento.
    - Se la scansione non rileva alcun dispositivo VMC, viene mostrato un messaggio "Nessun dispositivo VMC trovato".
    - Se la scansione non rileva alcun dispositivo viene proposto all'utente di modificare subnet e porta di scansione.
    - La scansione può essere configurata per utilizzare una subnet e porta personalizzate tramite le opzioni di configurazione dell'integrazione.
    - La UI deve seguire le linee guida di Home Assistant per l'integrazione.
- **Visualizzazione del progresso**:
    - Durante la scansione, viene mostrata una barra di avanzamento che indica la percentuale di completamento e il numero di dispositivi VMC trovati.
    - Il progresso viene aggiornato in tempo reale attraverso le funzionalità offerte da Home Assistant l'interfaccia utente.
    - Le informazioni visualizzate includono la percentuale di completamento, il numero di IP scansionati e il numero di dispositivi VMC trovati.
- **Conferma utente**:
    - Se sono già presenti dispositivi nello store home assistant, l'applicazione richiede una conferma all'utente prima di avviare una nuova scansione.
    - Questo previene la perdita accidentale di configurazioni esistenti.
    - Il dialogo di conferma mostra il numero di dispositivi già configurati.
- **Persistenza dei dispositivi**:
    - I dispositivi rilevati vengono salvati nello store di Home Assistant utilizzando le API di storage fornite.
    - Le informazioni salvate includono:
        - Nome del dispositivo rilevato dal comando VMNM?
        - Indirizzo IP
        - Ultima configurazione nota
    - Per ogni dispositivo viene creata un dispositivo separata in Home Assistant, permettendo una gestione individuale, monitoraggio e controllo
    - Al dispositivo viene associata un'icona rappresentativa di una ventola per facilitare l'identificazione visiva.
    - Al dispositivo vengono associati gli attributi rilevati dal comando di stato VMGH? (velocità ventola, stato sensori, stato LED pannello, livello luci, timer luci)
    - Al dispositivo vengono associati gli attributi rilevati dal comando dei sensori VMGI? (temperatura interna, temperatura esterna, umidità, livello CO2, livello VOC)
    - Al dispositivo viene associato l'attributo SSID della rete a cui è connesso, rilevato dal comando VMSL?
    - Al dispositivo vengono associate le entità di sensori per temperatura interna, temperatura esterna, umidità, livello CO2 e livello VOC
    - Al dispositivo viene associata un'entità di selezione per la velocità della ventola (0-4)
    - Al dispositivo viene associata un'entità di selezione per il livello delle luci (0, 25, 50, 75, 100)
    - Al dispositivo viene associata un'entità di selezione per il timer delle luci (0-300 secondi, step 5)
    - Al dispositivo viene associata un'entità di toggle per il LED del pannello (acceso/spento)
    - Al dispositivo viene associata un'entità di toggle per i sensori (attivi/inattivi)
    - Al dispositivo viene associata un'entità di toggle per la modalità iperventilazione (attiva/disattiva)
    - Al dispositivo viene associata un'entità di toggle per la modalità notturna (attiva/disattiva)
    - Al dispositivo viene associata un'entità di toggle per la modalità free cooling (attiva/disattivata)
    - Al dispositivo viene associata un'entità di azione per resettare il contatore del filtro
    - Al dispositivo viene associata un'entità di azione per rinominare il dispositivo
    - Al dispositivo viene associata un'entità di azione per modificare la configurazione di rete (SSID e password)
    - Al dispositivo viene associato un sensore di stato che indica se il dispositivo è online o offline, basato sull'ultima risposta ricevuta
    - Al dispositivo viene associato un sensore di stato che indica l'ultima volta che il dispositivo ha risposto a un comando, con timestamp aggiornato ad ogni risposta valida
    - Al dispositivo viene associato un sensore di stato che indica il numero di ore di utilizzo del filtro, basato su un contatore interno del dispositivo
    - Al dispositivo viene associato un sensore di stato che indica la velocità attuale della ventola, basato sull'ultimo comando di stato ricevuto
    - Al dispositivo viene associato un sensore di stato che indica il livello attuale delle luci, basato sull'ultimo comando di stato ricevuto
    - Al dispositivo viene associato un sensore di stato che indica il timer attuale delle luci, basato sull'ultimo comando di stato ricevuto
    - Al dispositivo viene associato un sensore di stato che indica se il LED del pannello è acceso o spento, basato sull'ultimo comando di stato ricevuto
    - Al dispositivo viene associato un sensore di stato che indica se i sensori sono attivi o inattivi, basato sull'ultimo comando di stato ricevuto
    - Al dispositivo viene associato un sensore di stato che indica se la modalità iperventilazione è attiva o disattivata, basato sull'ultimo comando di stato ricevuto
    - Al dispositivo viene associato un sensore di stato che indica se la modalità notturna è attiva o disattivata, basato sull'ultimo comando di stato ricevuto
    - Al dispositivo viene associato un sensore di stato che indica se la modalità free cooling è attiva o disattivata, basato sull'ultimo comando di stato ricevuto
    - Al dispositivo viene associato un sensore di stato che indica l'SSID della rete a cui è connesso, basato sull'ultimo comando di rete ricevuto
    - Al dispositivo viene associato un sensore di stato che indica l'indirizzo IP attuale del dispositivo, basato sull'ultimo comando di rete ricevuto
    - Al dispositivo viene associato un sensore di stato che indica la subnet mask attuale del dispositivo, basato sull'ultimo comando di rete ricevuto
    - Al dispositivo viene associato un sensore di stato che indica il gateway attuale del dispositivo, basato sull'ultimo comando di rete ricevuto
    - Al dispositivo viene associato un sensore di stato che indica il nome del dispositivo, basato sull'ultimo comando di nome ricevuto
    - Al dispositivo viene associato un sensore di stato che indica la password della rete a cui è connesso, basato sull'ultimo comando di rete ricevuto (mascherata per sicurezza)


### 2. Dashboard lovelace
- **Single Device**:
    - Permette di controllare un singolo dispositivo VMC.
    - Ogni dispositivo ha un pannello dedicato con i controlli specifici, fornendo un'interfaccia chiara e focalizzata.
    - Il pannello mostra lo stato del dispositivo in tempo reale, consentendo all'utente di monitorare le condizioni operative.
    - L'utente può modificare le impostazioni del dispositivo e visualizzare i dati dei sensori.
- **Broadcast**:
    - Permette di inviare comandi simultaneamente a tutti i dispositivi VMC rilevati.
    - Un unico pannello di controllo viene utilizzato per inviare i comandi a tutti i dispositivi, semplificando la gestione di più dispositivi contemporaneamente.
    - L'applicazione gestisce l'invio parallelo dei comandi per minimizzare i tempi di attesa, garantendo una risposta rapida.
    - Viene fornito un feedback sull'esito dei comandi per ogni dispositivo, consentendo all'utente di verificare che i comandi siano stati eseguiti correttamente.
    - La modalità broadcast è utile per applicare le stesse impostazioni a tutti i dispositivi in modo rapido e semplice.
- **Personalizzazione UI**: Permettere la personalizzazione delle card (icone, colori, layout).
  **Accessibilità**: La dashboard deve essere accessibile da mobile e segue le linee guida di Home Assistant per la UI.
  **Notifiche**: Le notifiche di errore vanno gestite tramite persistent_notification e toast, le notifiche di successo solo tramite toast.


### 3. Comandi Supportati
L'applicazione supporta i seguenti comandi per interagire con i dispositivi VMC:
- **Lettura dello stato**:
    - `get_status`: Ottiene lo stato generale del dispositivo.
        - Include la velocità della ventola, lo stato dei sensori, lo stato del LED del pannello, il livello delle luci e il timer.
        - I valori vengono decodificati e visualizzati in modo comprensibile nell'interfaccia utente, fornendo un quadro completo dello stato del dispositivo.
        - I dati vengono aggiornati periodicamente per garantire che l'interfaccia utente rifletta lo stato reale del dispositivo.
    - `get_name`: Ottiene il nome del dispositivo.
        - Il nome viene utilizzato come titolo del pannello del dispositivo, facilitando l'identificazione.
        - Permette di personalizzare l'identificazione dei dispositivi.
        - **Formato comando**: `VMNM?`
        - **Formato risposta**: `VMNM [nome_dispositivo]`
            - `nome_dispositivo`: Nome del dispositivo (stringa ASCII, max 32 caratteri)
    - `get_network_info`: Ottiene le informazioni sulla rete a cui è connesso il dispositivo.
        - Include l'SSID, la password (mascherata), l'indirizzo IP, la subnet mask e il gateway.
        - Le informazioni vengono visualizzate in un pannello espandibile, consentendo all'utente di visualizzare e modificare la configurazione di rete.
        - La password viene mascherata per proteggere la privacy dell'utente.
        - **Formato comando**: `VMSL?`
        - **Formato risposta**: Stringa di 64 caratteri, dove i primi 32 rappresentano l'SSID (riempito con `*`) e i successivi 32 rappresentano la password (riempita con `*`).
        - **Esempio**: `ValentinoNet********************Password************************00000000000000005001000000000000000000000000000000101`
        - **Elaborazione**: La risposta viene processata rimuovendo i caratteri `*` di riempimento e separando SSID e password.
        - **Feedback utente**: `{"SSID": "nome_rete", "Password": "password_mascherata"}`
    - `get_sensors_data`: Ottiene i dati dai sensori ambientali del dispositivo.
        - Include la temperatura interna ed esterna, l'umidità, il livello di CO2 e il livello di VOC.
        - I dati vengono visualizzati in una modale, fornendo un'interfaccia chiara e organizzata per la visualizzazione dei dati dei sensori.
        - I dati possono essere utilizzati per monitorare la qualità dell'aria e ottimizzare le impostazioni del dispositivo.
        - **Formato comando**: `VMGI?`
        - **Formato risposta**: `VMGI [temp_int] [temp_ext] [umidità] [CO2] [VOC]`
            - `temp_int`: Temperatura interna in °C (moltiplicata per 10)
            - `temp_ext`: Temperatura esterna in °C (moltiplicata per 10)
            - `umidità`: Umidità relativa in % (0-100)
            - `CO2`: Livello di CO2 in ppm
            - `VOC`: Livello di composti organici volatili (scala relativa)
        - **Elaborazione**: I valori di temperatura vengono divisi per 10 per ottenere il valore reale in °C.
        - **Feedback utente**: `{"temp_internal": 22.5, "temp_external": 18.3, "humidity": 65, "co2": 850, "voc": 120}`
- **Controllo del dispositivo**:
    - `set_fan_speed`: Imposta la velocità della ventola (0-4).
        - 0: Ventola spenta.
        - 1-4: Velocità della ventola.
        - Gestisce internamente le modalità speciali (iperventilazione, notte, free cooling), semplificando l'interazione con il dispositivo.
        - L'interfaccia utente riflette lo stato reale del dispositivo, mostrando la velocità della ventola e le modalità speciali attive.
        - **Formato comando**: `VMWH0000[velocità]`
            - `velocità`: Livello della ventola (0-4)
        - **Esempio**: `VMWH0000003` (imposta la ventola al livello 3)
        - **Risposta**: `OK` in caso di successo
        - **Effetto sulle modalità speciali**: L'impostazione manuale della velocità disattiva automaticamente eventuali modalità speciali attive
        - **Feedback utente**: `Velocità ventola impostata a 3`
    - `set_hyperventilation`: Attiva/disattiva la modalità di iperventilazione.
        - Se attiva, imposta la ventola a 4.
        - Disattiva le altre modalità speciali, garantendo che solo una modalità speciale sia attiva alla volta.
        - **Formato comando**: `VMWH0000005` (attiva)
        - **Risposta**: `OK` in caso di successo
        - **Effetto**: Quando attivata, imposta automaticamente la ventola alla massima velocità (4)
        - **Feedback utente**: `Modalità iperventilazione attivata`
    - `set_night_mode`: Attiva/disattiva la modalità notturna.
        - Se attiva, imposta la ventola a 1.
        - Disattiva le altre modalità speciali.
        - **Formato comando**: `VMWH0000006` (attiva)
        - **Risposta**: `OK` in caso di successo
        - **Effetto**: Quando attivata, imposta automaticamente la ventola alla velocità minima (1)
        - **Feedback utente**: `Modalità notturna attivata`
    - `set_free_cooling`: Attiva/disattiva la modalità free cooling.
        - Se attiva, imposta la ventola a 0.
        - Disattiva le altre modalità speciali.
        - **Formato comando**: `VMWH0000007` (attiva)
        - **Risposta**: `OK` in caso di successo
        - **Effetto**: Quando attivata, spegne automaticamente la ventola (livello 0)
        - **Feedback utente**: `Modalità free cooling attivata`
    - `set_sensors_on`: Attiva i sensori.
        - Permette di visualizzare i dati ambientali.
        - **Formato comando**: `VMWH0300000`
        - **Risposta**: `OK` in caso di successo
        - **Effetto**: Attiva i sensori di temperatura, umidità, CO2 e VOC
        - **Consumo energetico**: L'attivazione dei sensori aumenta leggermente il consumo energetico del dispositivo
        - **Feedback utente**: `Sensori attivati`
    - `set_sensors_off`: Disattiva i sensori.
        - Consente di risparmiare energia.
        - **Formato comando**: `VMWH0300002`
        - **Risposta**: `OK` in caso di successo
        - **Effetto**: Disattiva tutti i sensori ambientali per risparmiare energia
        - **Feedback utente**: `Sensori disattivati`
    - `set_panel_led_on`: Accende il LED del pannello.
        - Permette di visualizzare lo stato del dispositivo.
        - **Formato comando**: `VMWH0100010`
        - **Risposta**: `OK` in caso di successo
        - **Effetto**: Attiva l'illuminazione LED sul pannello fisico del dispositivo
        - **Feedback utente**: `LED pannello attivato`
    - `set_panel_led_off`: Spegne il LED del pannello.
        - Consente di risparmiare energia.
        - **Formato comando**: `VMWH0100000`
        - **Risposta**: `OK` in caso di successo
        - **Effetto**: Disattiva l'illuminazione LED sul pannello fisico del dispositivo
        - **Feedback utente**: `LED pannello disattivato`
    - `set_lights`: Imposta il livello delle luci (0-100).
        - Permette di regolare l'illuminazione dell'ambiente.
        - **Formato comando**: Non documentato nell'implementazione corrente
            - `livello`: Intensità dell'illuminazione (0-100, con step di 25)
        - **Risposta**: `OK` in caso di successo
        - **Limitazioni**: Il livello viene automaticamente arrotondato allo step più vicino (0, 25, 50, 75, 100)
        - **Feedback utente**: `Livello luci impostato a 75%`
    - `set_lights_timer`: Imposta il timer per le luci (0-300 secondi).
        - Permette di spegnere automaticamente le luci dopo un certo periodo di tempo.
        - **Formato comando**: Non documentato nell'implementazione corrente
            - `secondi`: Durata del timer in secondi (0-300)
        - **Risposta**: `OK` in caso di successo
        - **Comportamento**: Quando il timer scade, le luci si spengono automaticamente (livello 0)
        - **Valore 0**: Disattiva il timer (le luci rimangono al livello impostato)
        - **Feedback utente**: `Timer luci impostato a 120 secondi`
    - `set_filter_reset`: Resetta il contatore del filtro.
        - Permette di tenere traccia della durata del filtro e pianificare la manutenzione.
        - **Formato comando**: `VMWH0417744`
        - **Risposta**: `OK` in caso di successo
        - **Effetto**: Azzera il contatore delle ore di utilizzo del filtro
        - **Quando utilizzare**: Da eseguire dopo ogni sostituzione del filtro
        - **Feedback utente**: `Contatore filtro resettato`
    - `set_name`: Imposta il nome del dispositivo.
        - Permette di personalizzare l'identificazione del dispositivo.
        - **Formato comando**: `VMNM [nome_dispositivo]`
            - `nome_dispositivo`: Nome da assegnare al dispositivo (stringa ASCII, max 32 caratteri)
        - **Esempio**: `VMNM SoggiornoPrincipale`
        - **Risposta**: `OK` in caso di successo
        - **Limitazioni**: Il nome non può contenere caratteri speciali o spazi, solo lettere, numeri e underscore
        - **Persistenza**: Il nome viene salvato nella memoria non volatile del dispositivo e rimane disponibile anche dopo il riavvio
        - **Feedback utente**: `Nome dispositivo impostato correttamente`
    - `set_network`: Imposta la configurazione di rete del dispositivo.
        - Permette di connettere il dispositivo a una rete Wi-Fi diversa.
        - **Formato comando**: `VMSL [ssid] [password]`
            - `ssid`: SSID della rete Wi-Fi (stringa ASCII, max 32 caratteri)
            - `password`: Password della rete Wi-Fi (stringa ASCII, max 32 caratteri)
        - **Esempio**: `VMSL MiaReteWiFi Password123`
        - **Risposta**: `OK` in caso di successo, seguito dal riavvio della connessione di rete
        - **Tempo di riconnessione**: Circa 10-15 secondi per applicare le nuove impostazioni di rete
        - **Sicurezza**: Supporta reti WPA/WPA2/WPA3
        - **Feedback utente**: `Configurazione di rete aggiornata. Il dispositivo si riconnetterà.`
    - `set_password`: Imposta la password del dispositivo.
        - Permette di proteggere l'accesso al dispositivo.
        - **Formato comando**: `VMPW [password]`
            - `password`: Nuova password per l'accesso al dispositivo (stringa ASCII, 8-16 caratteri)
        - **Esempio**: `VMPW NuovaPassword123****************`
        - **Risposta**: `OK` in caso di successo
        - **Requisiti password**: Minimo 8 caratteri, deve contenere almeno una lettera maiuscola, una minuscola e un numero
        - **Effetto**: La nuova password sarà richiesta per tutte le connessioni future al dispositivo
        - **Reset**: In caso di password dimenticata, è possibile resettare il dispositivo tramite il pulsante fisico di reset
        - **Feedback utente**: `Password dispositivo aggiornata correttamente`

#### Dettaglio campi output VMGH? (Stato dispositivo)

Il comando `VMGH?` restituisce una stringa con 15 valori:

| Posizione | Campo         | Significato                                      | Unità/Range         |
|-----------|--------------|--------------------------------------------------|---------------------|
| 1         | fan_speed    | Velocità ventola / modalità speciale             | 0-7                 |
| 2         | panel_led    | LED pannello acceso/spento                       | 0/1                 |
| 3         | reserved_1   | Riservato (non utilizzato)                       | -                   |
| 4         | sensors      | Sensori attivi/inattivi                          | 0/1                 |
| 5-10      | reserved_2-7 | Riservato (non utilizzato)                       | -                   |
| 11        | lights_level | Livello luci                                     | 0-100 (%)           |
| 12-14     | reserved_8-10| Riservato (non utilizzato)                       | -                   |
| 15        | lights_timer | Timer luci                                       | 0-300 (secondi)     |

Esempio: `VMGO,00001,00000,00004,00002,00000,00010,00000,01200,00200,00220,09000,00600,00000,00000,00060`

---

#### Dettaglio campi output VMGI? (Dati sensori)

Il comando `VMGI?` restituisce una stringa con 15 valori:

| Posizione | Campo         | Significato                                      | Unità/Range         |
|-----------|--------------|--------------------------------------------------|---------------------|
| 1         | temp_int     | Temperatura interna                              | decimi di °C        |
| 2         | temp_ext     | Temperatura esterna                              | decimi di °C        |
| 3         | humidity     | Umidità relativa                                 | decimi di %         |
| 4         | co2          | Livello CO2                                      | ppm                 |
| 5-13      | reserved_1-9 | Riservato (non utilizzato)                       | -                   |
| 14        | voc          | Livello VOC                                      | ppb                 |

Esempio: `VMGI,00260,00257,00469,00320,16384,06043,00247,00112,04354,00125,00015,00247,00468,00000,00001`

- temp_int: 225 (22.5°C)
- temp_ext: 183 (18.3°C)
- humidity: 650 (65.0%)
- co2: 850 ppm
- voc: 120 ppb

---

#### Gestione degli errori
- **Timeout di connessione**: Se un dispositivo non risponde entro il timeout configurato, viene considerato offline e viene mostrato un messaggio di errore.
- **Comando non riuscito**: Se un comando non viene eseguito correttamente, viene mostrato un messaggio di errore con il motivo del fallimento.
- **Input non valido**: Se l'utente inserisce un valore non valido, viene mostrato un messaggio di errore e il valore non viene inviato al dispositivo.
- **Ritrasmissione automatica**: In caso di errore di comunicazione, il comando viene ritrasmesso automaticamente fino a un massimo di 3 tentativi.
- **Log degli errori**: Tutti gli errori vengono registrati in un file di log per facilitare la diagnosi e la risoluzione dei problemi.
- **Notifiche all'utente**: L'utente viene informato degli errori tramite notifiche nell'interfaccia utente, con suggerimenti per la risoluzione
- **Rate limiting**: Per prevenire il sovraccarico del dispositivo, i comandi inviati non possono superare una frequenza di 1 comando ogni 2 secondi per dispositivo.

### 4. Dashboard e Interfaccia Utente
L'interfaccia utente è progettata per essere intuitiva e facile da usare. 

Le principali componenti sono:
- **Pannelli dei dispositivi**:
    - Ogni dispositivo VMC rilevato ha un pannello dedicato con le informazioni sullo stato e i controlli.
    - I pannelli sono organizzati in modo chiaro e conciso, con un layout a tre colonne (etichetta, input, bottoni/icone).
    - Permettono di gestire facilmente i singoli dispositivi.
- **Card dei comandi**:
    - Organizzata in tre colonne:
        - Etichette: Descrizione del comando.
        - Input: Elementi per inserire i valori (slider, switch, input di testo).
        - Bottoni/Icone: Elementi per inviare il comando o visualizzare lo stato.
    - La tabella è responsive e si adatta alle diverse dimensioni dello schermo.
- **Slider**:
    - Utilizzati per impostare la velocità della ventola, il livello delle luci e il timer.
    - Ventola: range 0-4, visualizza un'icona specifica per ogni livello.
    - Luci: range 0-100, step 25.
    - Timer: range 0-300, step 5.
    - I valori vengono visualizzati in tempo reale, fornendo un feedback immediato all'utente.
- **Switch**:
    - Utilizzati per attivare/disattivare le varie modalità (LED, sensori, iperventilazione, modalità notturna, free cooling).
    - Iperventilazione, Modalità Notte, Free Cooling: Mutuamente esclusive.
    - LED, Sensori: Indipendenti.
    - Lo stato degli switch viene sincronizzato con lo stato del dispositivo, garantendo che l'interfaccia utente rifletta lo stato reale del dispositivo.
- **Logica Ventola/Modalità Speciali**:
    - Se è attiva una modalità speciale (iperventilazione, notte, free cooling), lo slider della ventola viene impostato automaticamente al valore corrispondente (4, 1, 4 rispettivamente).
    - Quando si imposta la velocità della ventola tramite lo slider, le modalità speciali vengono disattivate, fornendo un controllo preciso sulla velocità della ventola.
    - L'interfaccia utente riflette sempre lo stato reale del dispositivo, mostrando lo stato attivo delle modalità speciali e il livello della ventola.
- **Input di testo**:
    - Utilizzati per impostare il nome del dispositivo, l'SSID e la password della rete.
    - I campi password sono mascherati per proteggere la privacy dell'utente.
    - La lunghezza dei campi è limitata per prevenire errori e problemi di sicurezza.
- **Icone della ventola**:
    - Visualizzano graficamente il livello della ventola.
    - Utilizzano immagini PNG per una migliore resa visiva.
    - Cambiano dinamicamente in base al livello della ventola, fornendo un feedback visivo immediato.
- **Pannello informazioni di rete**:
    - Mostra le informazioni di rete del dispositivo (indirizzo IP, SSID, password).
    - È espandibile tramite un'icona, consentendo all'utente di visualizzare e modificare la configurazione di rete solo quando necessario.
    - Permette di visualizzare e modificare la configurazione di rete del dispositivo.
- **Modale dati sensori**:
    - Visualizza i dati provenienti dai sensori del dispositivo (temperatura, umidità, CO2, VOC).
    - Utilizza un layout chiaro e organizzato, facilitando la lettura e l'interpretazione dei dati.
    - Permette di monitorare facilmente le condizioni ambientali e ottimizzare le impostazioni del dispositivo.
- **Feedback utente**:
    - Utilizza notifiche toast per informare l'utente sull'esito delle operazioni
    - Mostra messaggi di errore chiari e informativi in caso di problemi
    - Fornisce suggerimenti per la risoluzione dei problemi comuni
    - Feedback immediato all'utente sull'esito dei comandi
    - Messaggi di errore chiari e informativi
    - Suggerimenti per la risoluzione dei problemi
- **Logging e diagnostica**:
    - Log dettagliati delle operazioni di rete e dei comandi
    - Mascheramento automatico delle password nei log
    - Debug mode per informazioni aggiuntive durante lo sviluppo
- **Decodifica dello stato della ventola**:
    - Gestione automatica delle modalità speciali:
        - 5: Modalità notte attiva (ventola a 1)
        - 6: Iperventilazione attiva (ventola a 4)
        - 7: Free cooling attivo (ventola a 0)
    - Aggiornamento automatico dell'interfaccia utente in base alla modalità attiva
- **Stato del dispositivo**:
  - Un dispositivo che non risponde ai comandi viene considerato offline dopo 3 tentativi falliti.
  - Lo stato online/offline viene visualizzato chiaramente nell'interfaccia utente.
  - Viene mostrato l'ultimo timestamp di risposta valida del dispositivo.
  - Viene mostrato il numero di ore di utilizzo del filtro, basato su un contatore interno del dispositivo.
  - Viene mostrato l'indirizzo IP attuale del dispositivo.
  - Viene mostrato l'SSID della rete a cui è connesso il dispositivo.

### 6. Sicurezza
- **Mascheramento password**: Le password non vengono mai mostrate in chiaro nell'interfaccia utente o nei log.
- **Validazione input**: I dati inseriti dall'utente vengono validati per prevenire errori e problemi di sicurezza.
- **Gestione connessioni**: Le connessioni socket vengono gestite in modo sicuro con timeout e chiusura appropriata.
- **Protezione dati**: I dati sensibili vengono salvati in modo sicuro utilizzando le API di sistema appropriate per ogni piattaforma.

### 7. Gestione Connessioni
- **Connessioni Socket**:
    - Gestione asincrona delle connessioni TCP/IP
    - Implementazione di timeout configurabili
    - Gestione automatica della riconnessione in caso di perdita della connessione
    - Chiusura appropriata delle connessioni quando non più necessarie
- **Gestione Errori**:
    - Timeout per operazioni di rete
    - Gestione disconnessioni impreviste
    - Feedback all'utente sullo stato della connessione
    - Tentativi automatici di riconnessione

### 8. Persistenza

- **Storage Integrato Home Assistant**:
    - L'integrazione sfrutta le API di storage di Home Assistant per la persistenza dei dati, utilizzando la classe `Store` (`homeassistant.helpers.storage.Store`) per salvare e recuperare le informazioni dei dispositivi VMC e delle relative configurazioni.
    - I dati vengono memorizzati in formato JSON all'interno della directory `.storage/` di Home Assistant, garantendo sicurezza, compatibilità e aggiornabilità automatica del formato.
    - L'accesso ai dati persistenti avviene tramite l'oggetto `hass.data` e le funzioni asincrone di caricamento/salvataggio, assicurando la sincronizzazione tra stato reale e interfaccia utente.

- **Dati Salvati**:
    - Per ogni dispositivo VMC vengono salvati:
        - Nome del dispositivo (rilevato o personalizzato)
        - Indirizzo IP
    - I dati sono strutturati per permettere la gestione individuale di ogni dispositivo e la sincronizzazione automatica con lo stato reale.

- **Recupero e Aggiornamento**:
    - All’avvio di Home Assistant, l’integrazione carica automaticamente i dati persistenti, ripristinando la configurazione e lo stato dei dispositivi.
    - Ogni modifica (aggiunta, aggiornamento, rimozione di dispositivi o parametri) viene immediatamente salvata nello storage, garantendo la coerenza tra interfaccia utente e stato reale.
    - In caso di reset o nuova scansione, l’utente può scegliere se sovrascrivere i dati esistenti o mantenerli, tramite dialogo di conferma.

- **Sicurezza e Privacy**:
    - Le password e i dati sensibili vengono salvati in formato mascherato e non sono mai esposti in chiaro né nell’interfaccia utente né nei log.
    - L’accesso ai dati persistenti è limitato all’integrazione e alle API di Home Assistant, garantendo la protezione da accessi non autorizzati.

- **Compatibilità e Aggiornabilità**:
    - Il formato dei dati salvati è compatibile con le future versioni di Home Assistant, grazie all’uso delle API ufficiali di storage.
    - In caso di aggiornamento dell’integrazione, i dati vengono migrati automaticamente al nuovo formato, senza perdita di informazioni.

- **Backup e Restore**:
    - L'integrazione prevede una procedura di backup e ripristino dei dati dei dispositivi VMC, utile in caso di migrazione dell'istanza Home Assistant o ripristino da un errore.
    - Il backup può essere effettuato esportando manualmente i file di storage dalla directory `.storage/` oppure tramite automazioni/script che copiano i dati in una posizione sicura.
    - Il restore avviene importando i file di storage nella nuova istanza o ripristinando i file originali, garantendo la continuità della configurazione e dello stato dei dispositivi.
    - La documentazione dell'integrazione fornisce istruzioni dettagliate per eseguire backup e restore in modo sicuro e compatibile con le versioni future di Home Assistant.

### 9. Test e Validazione
- **Copertura di test automatici**:
    - L'integrazione prevede una copertura di test automatici (unitari e di integrazione) pari ad almeno l'80% del codice.
    - I test unitari verificano la correttezza delle singole funzioni e classi.
    - I test di integrazione simulano il comportamento dell'integrazione in Home Assistant, inclusa la discovery, la persistenza, la dashboard e la comunicazione con i dispositivi VMC.
    - I test vengono eseguiti automaticamente tramite pipeline CI/CD ad ogni modifica del codice.
    - La documentazione include istruzioni su come eseguire i test manualmente e interpretare i risultati, sia tramite comandi da terminale che tramite strumenti di Home Assistant.

### 10. Internazionalizzazione
- **Supporto lingue**:
    - L'integrazione supporta la localizzazione completa in italiano e inglese.
    - Tutti i messaggi, le notifiche, le descrizioni e le etichette dell'interfaccia utente sono tradotti tramite le funzionalità di localizzazione di Home Assistant.
    - La lingua visualizzata viene selezionata automaticamente in base alle impostazioni di Home Assistant o può essere configurata dall'utente.
    - La documentazione include istruzioni su come contribuire con nuove traduzioni e come segnalare errori di localizzazione.

### 11. Aggiornamenti e Manutenzione
- **Gestione degli aggiornamenti**:
    - Gli aggiornamenti dell'integrazione vengono gestiti tramite HACS (Home Assistant Community Store) o repository ufficiale Home Assistant.
    - Ad ogni aggiornamento, viene verificata la compatibilità con la versione corrente di Home Assistant.
    - In caso di modifiche al formato dei dati persistenti, la migrazione viene eseguita automaticamente per garantire la continuità del servizio e la retrocompatibilità.
    - La documentazione include istruzioni dettagliate per l'aggiornamento, il rollback e la gestione delle versioni.
    - Viene garantita la retrocompatibilità con le versioni precedenti ove possibile, e vengono segnalate eventuali breaking changes.
    - Gli utenti sono informati tramite changelog e notifiche in Home Assistant sulle novità e sulle procedure consigliate per l'aggiornamento.


### 13. Protocollo di Comunicazione VMC
- **Tipo di Protocollo**: TCP/IP su porta 5001.
- **Formato dei Comandi**: Stringhe ASCII terminate da `\r\n`.
- **Encoding**: ASCII (i caratteri non ASCII vengono ignorati).
- **Struttura dei Comandi**:
    - I comandi iniziano con un identificativo (es. `VMNM`, `VMSL`, `VMGH`, `VMWH`).
    - Alcuni comandi richiedono parametri, separati da spazi (es. `VMNM NomeDispositivo`).
    - La lunghezza massima dei comandi è di circa 200 caratteri.
- **Risposte**:
    - Le risposte sono stringhe ASCII.
    - I comandi di "lettura" (es. `VMNM?`, `VMSL?`, `VMGH?`, `VMGI?`) restituiscono stringhe contenenti i dati richiesti.
    - I comandi di "scrittura" (es. `VMWH*`, `VMNM`) generalmente restituiscono `OK` se l'operazione ha avuto successo.
    - In caso di errore, il dispositivo può restituire una stringa di errore o non rispondere affatto.
- **Formato dello Stato (`VMGH?`)**:
    - La risposta inizia con `VMGO,` seguito da 15 valori separati da virgole.
    - I valori rappresentano:
        1. Velocità della ventola (0-7, vedi sezione "Logica Ventola/Modalità Speciali").
        2. Stato del LED del pannello (0 o 1).
        3. Riservato.
        4. Stato dei sensori (0 = attivi, 1 = inattivi).
        5. -10. Riservati.
        11. Livello delle luci (0-100).
        12. -14. Riservati.
        15. Timer delle luci (in secondi).
- **Logica Ventola/Modalità Speciali**:
    - Il valore della velocità della ventola nello stato (`VMGH?`) può indicare anche la modalità speciale attiva:
        - 5: Modalità notte attiva, ventola a 1.
        - 6: Iperventilazione attiva, ventola a 4.
        - 7: Free cooling attivo, ventola a 0.
    - L'applicazione gestisce questa decodifica internamente per mostrare lo stato corretto nell'interfaccia utente.
- **Gestione degli Errori**:
    - L'applicazione implementa timeout per evitare blocchi in caso di mancata risposta del dispositivo.
    - Le risposte non valide o inattese vengono gestite con messaggi di errore appropriati.
    - Le password vengono mascherate nei log per motivi di sicurezza.


#### 13.1. Comandi Supportati
L'applicazione supporta i seguenti comandi per interagire con i dispositivi VMC:
- **Lettura dello stato**:
    - `get_status`: Ottiene lo stato generale del dispositivo.
        - Include la velocità della ventola, lo stato dei sensori, lo stato del LED del pannello, il livello delle luci e il timer.
        - I valori vengono decodificati e visualizzati in modo comprensibile nell'interfaccia utente, fornendo un quadro completo dello stato del dispositivo.
        - I dati vengono aggiornati periodicamente per garantire che l'interfaccia utente rifletta lo stato reale del dispositivo.
    - `get_name`: Ottiene il nome del dispositivo.
        - Il nome viene utilizzato come titolo del pannello del dispositivo, facilitando l'identificazione.
        - Permette di personalizzare l'identificazione dei dispositivi.
    - `get_network_info`: Ottiene le informazioni sulla rete a cui è connesso il dispositivo.
        - Include l'SSID, la password (mascherata), l'indirizzo IP, la subnet mask e il gateway.
        - Le informazioni vengono visualizzate in un pannello espandibile, consentendo all'utente di visualizzare e modificare la configurazione di rete.
        - La password viene mascherata per proteggere la privacy dell'utente.
        - **Formato comando**: `VMSL?`
        - **Formato risposta**: Stringa di 64 caratteri, dove i primi 32 rappresentano l'SSID (riempito con `*`) e i successivi 32 rappresentano la password (riempita con `*`).
        - **Elaborazione**: La risposta viene processata rimuovendo i caratteri `*` di riempimento e separando SSID e password.
        - **Feedback utente**: `{"SSID": "nome_rete", "Password": "password_mascherata"}`
    - `get_sensors_data`: Ottiene i dati dai sensori ambientali del dispositivo.
        - Include la temperatura interna ed esterna, l'umidità, il livello di CO2 e il livello di VOC.
        - I dati vengono visualizzati in una modale, fornendo un'interfaccia chiara e organizzata per la visualizzazione dei dati dei sensori.
        - I dati possono essere utilizzati per monitorare la qualità dell'aria e ottimizzare le impostazioni del dispositivo.
        - **Formato comando**: `VMGI?`
        - **Formato risposta**: `VMGI [temp_int] [temp_ext] [umidità] [CO2] [VOC]`
            - `temp_int`: Temperatura interna in °C (moltiplicata per 10)
            - `temp_ext`: Temperatura esterna in °C (moltiplicata per 10)
            - `umidità`: Umidità relativa in % (0-100)
            - `CO2`: Livello di CO2 in ppm
            - `VOC`: Livello di composti organici volatili (scala relativa)
        - **Elaborazione**: I valori di temperatura vengono divisi per 10 per ottenere il valore reale in °C.
        - **Feedback utente**: `{"temp_internal": 22.5, "temp_external": 18.3, "humidity": 65, "co2": 850, "voc": 120}`
- **Controllo del dispositivo**:
    - `set_fan_speed`: Imposta la velocità della ventola (0-4).
        - 0: Ventola spenta.
        - 1-4: Velocità della ventola.
        - Gestisce internamente le modalità speciali (iperventilazione, notte, free cooling), semplificando l'interazione con il dispositivo.
        - L'interfaccia utente riflette lo stato reale del dispositivo, mostrando la velocità della ventola e le modalità speciali attive.
    - `set_hyperventilation`: Attiva/disattiva la modalità di iperventilazione.
        - Se attiva, imposta la ventola a 4.
        - Disattiva le altre modalità speciali, garantendo che solo una modalità speciale sia attiva alla volta.
    - `set_night_mode`: Attiva/disattiva la modalità notturna.
        - Se attiva, imposta la ventola a 1.
        - Disattiva le altre modalità speciali.
    - `set_free_cooling`: Attiva/disattiva la modalità free cooling.
        - Se attiva, imposta la ventola a 0.
        - Disattiva le altre modalità speciali.
    - `set_sensors_on`: Attiva i sensori.
        - Permette di visualizzare i dati ambientali.
    - `set_sensors_off`: Disattiva i sensori.
        - Consente di risparmiare energia.
    - `set_panel_led_on`: Accende il LED del pannello.
        - Permette di visualizzare lo stato del dispositivo.
    - `set_panel_led_off`: Spegne il LED del pannello.
        - Consente di risparmiare energia.
    - `set_lights`: Imposta il livello delle luci (0-100).
        - Permette di regolare l'illuminazione dell'ambiente.
    - `set_lights_timer`: Imposta il timer per le luci (0-300 secondi).
        - Permette di spegnere automaticamente le luci dopo un certo periodo di tempo.
    - `set_filter_reset`: Resetta il contatore del filtro.
        - Permette di tenere traccia della durata del filtro e pianificare la manutenzione.
    - `set_name`: Imposta il nome del dispositivo.
        - Permette di personalizzare l'identificazione del dispositivo.
    - `set_network`: Imposta la configurazione di rete del dispositivo.
        - Permette di connettere il dispositivo a una rete Wi-Fi diversa.
    - `set_password`: Imposta la password del dispositivo.
        - Permette di proteggere l'accesso al dispositivo.

### 14. Interpretazione delle Risposte VMC
- **Generalità**:
    - Le risposte dei dispositivi VMC sono stringhe ASCII.
    - La prima parte della stringa indica il tipo di risposta (es. `VMGO`, `VMNM`, `VMSL`, `VMGI`).
    - I dati sono separati da virgole.
- **Risposta `get_status` (VMGH?)**:
    - Formato: `VMGO,fan_speed,panel_led,reserved,sensors,reserved,...,lights_level,reserved,...,lights_timer`
    - `fan_speed`: Velocità della ventola (0-7). Vedi "Logica Ventola/Modalità Speciali".
    - `panel_led`: Stato del LED del pannello (0 = spento, 1 = acceso).
    - `sensors`: Stato dei sensori (0 = attivi, 1 = inattivi).
    - `lights_level`: Livello delle luci (0-100).
    - `lights_timer`: Timer delle luci (in secondi).
- **Risposta `get_name` (VMNM?)**:
    - Formato: `VMNM nome_dispositivo`
    - `nome_dispositivo`: Nome del dispositivo (stringa ASCII).
- **Risposta `get_network_info` (VMSL?)**:
    - Formato: `ssidpassword0000000000000000500100000000000000000000000000000001`
    - `ssid`: SSID della rete Wi-Fi (32 caratteri, riempiti con `*` se più corto).
    - `password`: Password della rete Wi-Fi (32 caratteri, riempiti con `*` se più corta).
    - L'applicazione rimuove i caratteri di riempimento (`*`) per visualizzare solo l'SSID e la password effettivi.
- **Risposta `get_sensors_data` (VMGI?)**:
    - Formato: `VMGI,temp_int,temp_ext,humidity,co2,reserved,...,voc`
    - `temp_int`: Temperatura interna (decimi di grado Celsius).
    - `temp_ext`: Temperatura esterna (decimi di grado Celsius).
    - `humidity`: Umidità (decimi di percentuale).
    - `co2`: Livello di CO2 (ppm).
    - `voc`: Livello di VOC (ppb).
    - L'applicazione converte i valori in unità di misura comprensibili (es. gradi Celsius, percentuale, ppm, ppb).
- **Risposte ai Comandi di Scrittura**:
    - Generalmente, i comandi di scrittura (es. `set_fan_speed`, `set_lights`, `set_name`) restituiscono `OK` in caso di successo.
    - In caso di errore, il dispositivo può restituire una stringa di errore o non rispondere affatto.
    - L'applicazione gestisce questi casi e fornisce un feedback appropriato all'utente.
- **Logica Ventola/Modalità Speciali**:
    - Il valore della velocità della ventola nello stato (`VMGH?`) può indicare anche la modalità speciale attiva:
        - 5: Modalità notte attiva, valore ventola visualizzato a 1.
        - 6: Iperventilazione attiva, valore ventola visualizzato a 4.
        - 7: Free cooling attivo, valore ventola visualizzato a 0.
        - Se il valore della ventola reale è compreso tra 0 e 4, le modalità speciali sono disattivate e la velocità della ventola è impostata manualmente.
    - L'applicazione gestisce questa decodifica internamente per mostrare lo stato corretto nell'interfaccia utente.
- **Gestione degli Errori**:
    - L'applicazione implementa timeout per evitare blocchi in caso di mancata risposta del dispositivo.
    - Le risposte non valide o inattese vengono gestite con messaggi di errore appropriati.
    - Le password vengono mascherate nei log per motivi di sicurezza.

