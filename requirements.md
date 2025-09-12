# Specifiche Funzionali del Progetto VMC Control

## Panoramica
Il progetto VMC Control è un'applicazione cross-platform sviluppata in Flutter che permette di gestire da remoto dispositivi VMC (Ventilazione Meccanica Controllata) attraverso una rete locale. L'applicazione offre funzionalità di discovery automatica dei dispositivi, monitoraggio dello stato in tempo reale e controllo delle principali impostazioni. L'obiettivo è fornire un'interfaccia utente intuitiva e centralizzata per la gestione dei dispositivi VMC, semplificando la configurazione e il monitoraggio.

## Architettura
Il sistema è implementato come un'applicazione Flutter monolitica che gestisce direttamente la comunicazione con i dispositivi VMC. L'architettura è strutturata secondo il pattern Provider per la gestione dello stato e segue i principi di Clean Architecture:

- **Models**: Definizioni delle strutture dati per dispositivi VMC e comandi
- **Providers**: Gestione dello stato dell'applicazione e della logica di business
- **Services**: 
    - Gestione della comunicazione socket TCP/IP con i dispositivi VMC
    - Gestione della configurazione di rete
    - Persistenza dei dati dei dispositivi
- **Screens**: Interfacce utente per le varie funzionalità
- **Widgets**: Componenti riutilizzabili dell'interfaccia

L'applicazione è progettata per essere:
- Cross-platform (Android, iOS, Windows, macOS, Linux, Web)
- Modulare e facilmente estendibile
- Performante nella gestione delle comunicazioni di rete
- Reattiva agli aggiornamenti di stato dei dispositivi

## Funzionalità Dettagliate

### 1. Discovery dei Dispositivi
- **Scansione della rete**:
    - L'applicazione esegue una scansione asincrona della subnet locale (192.168.1.1-192.168.1.254) sulla porta 5001 per identificare i dispositivi VMC attivi.
    - Utilizza Socket TCP/IP asincroni (dart:io) per gestire connessioni multiple simultaneamente.
    - Implementa timeout configurabili per ogni tentativo di connessione, garantendo una scansione fluida ed efficiente.
    - La scansione viene eseguita in un isolate separato per non bloccare l'interfaccia utente.
- **Visualizzazione del progresso**:
    - Durante la scansione, viene mostrata una barra di avanzamento che indica la percentuale di completamento e il numero di dispositivi VMC trovati.
    - Il progresso viene aggiornato in tempo reale attraverso uno Stream che comunica tra l'isolate di scansione e l'interfaccia utente.
    - Le informazioni visualizzate includono la percentuale di completamento, il numero di IP scansionati e il numero di dispositivi VMC trovati.
- **Conferma utente**:
    - Se sono già presenti dispositivi nelle SharedPreferences, l'applicazione richiede una conferma all'utente prima di avviare una nuova scansione.
    - Questo previene la perdita accidentale di configurazioni esistenti.
    - Il dialogo di conferma mostra il numero di dispositivi già configurati.
- **Persistenza dei dispositivi**:
    - I dispositivi rilevati vengono salvati nelle SharedPreferences in formato JSON.
    - Le informazioni salvate includono:
        - Nome mnemonico del dispositivo
        - Indirizzo IP
        - Ultima configurazione nota
    - I dati vengono caricati automaticamente all'avvio dell'applicazione.

### 2. Modalità di Controllo
- **Single Device**:
    - Permette di controllare un singolo dispositivo VMC alla volta.
    - Ogni dispositivo ha un pannello dedicato con i controlli specifici, fornendo un'interfaccia chiara e focalizzata.
    - Il pannello mostra lo stato del dispositivo in tempo reale, consentendo all'utente di monitorare le condizioni operative.
    - L'utente può modificare le impostazioni del dispositivo e visualizzare i dati dei sensori.
- **Broadcast**:
    - Permette di inviare comandi simultaneamente a tutti i dispositivi VMC rilevati.
    - Un unico pannello di controllo viene utilizzato per inviare i comandi a tutti i dispositivi, semplificando la gestione di più dispositivi contemporaneamente.
    - L'applicazione gestisce l'invio parallelo dei comandi per minimizzare i tempi di attesa, garantendo una risposta rapida.
    - Viene fornito un feedback sull'esito dei comandi per ogni dispositivo, consentendo all'utente di verificare che i comandi siano stati eseguiti correttamente.
    - La modalità broadcast è utile per applicare le stesse impostazioni a tutti i dispositivi in modo rapido e semplice.

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


### 4. Interfaccia Utente
L'interfaccia utente è progettata per essere intuitiva e facile da usare. Le principali componenti sono:
- **Pannelli dei dispositivi**:
    - Ogni dispositivo VMC rilevato ha un pannello dedicato con le informazioni sullo stato e i controlli.
    - I pannelli sono organizzati in modo chiaro e conciso, con un layout a tre colonne (etichetta, input, bottoni/icone).
    - Permettono di gestire facilmente i singoli dispositivi.
- **Tabella dei comandi**:
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

### 5. Gestione dello Stato e Feedback
- **Provider per la gestione dello stato**:
    - Utilizzo del pattern Provider per gestire lo stato dell'applicazione
    - VMCProvider mantiene lo stato di tutti i dispositivi e notifica i widget quando necessario
    - Gestione centralizzata delle connessioni e dello stato dei dispositivi
- **Indicatori di stato**: 
    - Icone colorate (verde/rosso) indicano lo stato di connessione del dispositivo
    - Badge sui dispositivi per indicare modalità speciali attive
    - Animazioni per indicare operazioni in corso
- **Aggiornamento automatico**: 
    - I controlli dell'interfaccia utente vengono aggiornati automaticamente tramite ChangeNotifier
    - Polling periodico dello stato dei dispositivi con intervallo configurabile
    - Stream di eventi per aggiornamenti in tempo reale
- **Notifiche Toast**: 
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

### 8. File di Configurazione e Persistenza
- La persistenza dei dati viene gestita attraverso `shared_preferences` per salvare le configurazioni dei dispositivi
- I dati vengono salvati in formato JSON e includono:
    - Lista dei dispositivi VMC con relativi nomi e indirizzi IP
    - Preferenze dell'utente
    - Configurazioni di rete

### 9. Librerie Utilizzate
- **provider**: Gestione dello stato dell'applicazione
- **shared_preferences**: Persistenza dei dati
- **dart:io**: Socket TCP/IP e operazioni di rete
- **flutter_test**: Testing dell'applicazione
- **mockito**: Mock objects per i test

### 10. Struttura del Codice
- **lib/**
    - **models/**: Definizioni delle strutture dati
        - `vmc_device.dart`: Modello dispositivo VMC
        - `command_request.dart`: Modello richieste comandi
    - **providers/**: Gestione dello stato
        - `vmc_provider.dart`: Gestione stato dispositivi VMC
    - **screens/**: Schermate dell'applicazione
        - `home_screen.dart`: Schermata principale
    - **services/**: Servizi e logica di business
        - `network_service.dart`: Gestione rete
        - `vmc_service.dart`: Logica business VMC
        - `vmc_socket_service.dart`: Comunicazione socket
    - **widgets/**: Componenti UI riutilizzabili
        - `vmc_card.dart`: Card dispositivo VMC
- **test/**: Test automatizzati
    - Test di unità per servizi e provider
    - Test widget per l'interfaccia utente
    - Test di integrazione per la comunicazione di rete

### 11. Protocollo di Comunicazione VMC
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

#### 11.1. Comandi Supportati
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

### 12. Interpretazione delle Risposte VMC
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
    - Generalmente, i comandi di scrittura (es. `set_fan_speed`, `set_lights`, `set_name`) restituiscono `OK` se l'operazione ha avuto successo.
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
