# Esempi di configurazione per la VMC Helty Card

Questa pagina mostra alcuni esempi pratici di configurazione della custom card `vmc-helty-card` per Home Assistant.

---

## Esempio base

```yaml
- type: custom:vmc-helty-card
  entity_fan: fan.vmc_helty_camera
  entity_airflow: sensor.vmc_helty_camera_portata_d_aria
  entity_temperature: sensor.vmc_helty_camera_temperatura_interna
  entity_humidity: sensor.vmc_helty_camera_umidita
  entity_co2: sensor.vmc_helty_camera_co2
  entity_absolute_humidity: sensor.vmc_helty_camera_umidita_assoluta
  entity_dew_point: sensor.vmc_helty_camera_punto_di_rugiada
  entity_comfort_index: sensor.vmc_helty_camera_indice_comfort_igrometrico
  entity_filter_hours: sensor.vmc_helty_camera_filter_hours
  entity_last_response: sensor.vmc_helty_camera_last_response
  name: "VMC Camera"
```

---

## Esempio con luci e timer

```yaml
- type: custom:vmc-helty-card
  entity_fan: fan.vmc_helty_soggiorno
  entity_light: light.vmc_helty_soggiorno_light
  entity_light_timer: light.vmc_helty_soggiorno_light_timer
  entity_airflow: sensor.vmc_helty_soggiorno_portata_d_aria
  entity_temperature: sensor.vmc_helty_soggiorno_temperatura_interna
  entity_humidity: sensor.vmc_helty_soggiorno_umidita
  entity_co2: sensor.vmc_helty_soggiorno_co2
  entity_absolute_humidity: sensor.vmc_helty_soggiorno_umidita_assoluta
  entity_dew_point: sensor.vmc_helty_soggiorno_punto_di_rugiada
  entity_comfort_index: sensor.vmc_helty_soggiorno_indice_comfort_igrometrico
  entity_filter_hours: sensor.vmc_helty_soggiorno_filter_hours
  entity_last_response: sensor.vmc_helty_soggiorno_last_response
  name: "VMC Soggiorno"
```

---

## Esempio con switch modalità speciali

```yaml
- type: custom:vmc-helty-card
  entity_fan: fan.vmc_helty_bagno
  entity_hyperventilation: switch.vmc_helty_bagno_iperventilazione
  entity_night: switch.vmc_helty_bagno_modalita_notte
  entity_free_cooling: switch.vmc_helty_bagno_free_cooling
  entity_panel_led: switch.vmc_helty_bagno_panel_led
  entity_sensors: switch.vmc_helty_bagno_sensors
  entity_airflow: sensor.vmc_helty_bagno_portata_d_aria
  entity_temperature: sensor.vmc_helty_bagno_temperatura_interna
  entity_humidity: sensor.vmc_helty_bagno_umidita
  entity_filter_hours: sensor.vmc_helty_bagno_filter_hours
  name: "VMC Bagno"
```

---

## Note

- Sostituisci i nomi delle entità (`fan.vmc_helty_camera`, `sensor.vmc_helty_camera_portata_d_aria`, ecc.) con quelli effettivamente presenti nella tua installazione Home Assistant.

- Puoi omettere le entità che non ti interessano: la card mostrerà solo i controlli disponibili.

- Per la lista completa delle opzioni consulta la documentazione ufficiale della card.
