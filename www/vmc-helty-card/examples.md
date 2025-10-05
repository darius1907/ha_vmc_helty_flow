# Esempi di configurazione per la VMC Helty Card

Questa pagina mostra alcuni esempi pratici di configurazione della custom card `vmc-helty-card` per Home Assistant.

---

## Esempio base

```yaml
- type: custom:vmc-helty-card
  entity_fan: fan.vmc_helty_camera
  name: "VMC Camera"
```

---

## Note

- Sostituisci i nomi delle entità (`fan.vmc_helty_camera`) con quelli effettivamente presenti nella tua installazione Home Assistant.