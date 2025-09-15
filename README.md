# ha_vmc_helty_flow

Integrazione Home Assistant per VMC Helty Flow

## Entità disponibili

- **VmcHeltyFan**: controllo ventola
- **VmcHeltySensor**: sensori ambientali (Temperatura Interna, Esterna, Umidità, CO2, VOC)
- **VmcHeltyOnOffSensor**: stato accensione/spegnimento
- **VmcHeltyResetFilterButton**: reset filtro
- **VmcHeltyNameText**: nome dispositivo
- **VmcHeltySSIDText**: SSID WiFi
- **VmcHeltyPasswordText**: password WiFi
- **VmcHeltyIPAddressSensor**: indirizzo IP
- **VmcHeltySubnetMaskSensor**: subnet mask
- **VmcHeltyGatewaySensor**: gateway
- **VmcHeltyLastResponseSensor**: ultimo stato
- **VmcHeltyFilterHoursSensor**: ore filtro
- **VmcHeltyNetworkSSIDSensor**: SSID di rete
- **VmcHeltyNetworkPasswordSensor**: password di rete
- **VmcHeltyModeSwitch**: modalità (hyperventilation, night, free_cooling)
- **VmcHeltyPanelLedSwitch**: LED pannello
- **VmcHeltySensorsSwitch**: attivazione sensori
- **VmcHeltyLight**: luce
- **VmcHeltyLightTimer**: timer luce

## Configurazione guidata

Durante la configurazione, la UI permette di:
- Impostare la subnet, la porta TCP e il timeout della scansione (1-60 secondi)
- Visualizzare una barra di avanzamento durante la scansione
- Interrompere la scansione in qualsiasi momento
- Validare la subnet (formato e numero IP, max 50)
- Ricevere messaggi di errore/avviso se la subnet è troppo ampia o i parametri non sono validi

### Esempio di configurazione

1. Avvia la configurazione dall'interfaccia Home Assistant.
2. Inserisci la subnet (es. `192.168.1.0/24`), la porta (es. `5001`) e il timeout desiderato.
3. Avvia la scansione e osserva la barra di avanzamento.
4. Se necessario, interrompi la scansione.
5. Seleziona i dispositivi trovati e conferma.

## Note
- La scansione è limitata a subnet che generano al massimo 50 IP.
- Tutte le entità sono disponibili per automazioni e dashboard.
