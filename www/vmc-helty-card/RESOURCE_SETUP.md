# 🔧 Configurazione Risorse Lovelace

## 📁 Struttura File da Copiare

Assicurati di copiare **TUTTI** i file nella cartella corretta:

```bash
/config/www/vmc-helty-card/
├── vmc-helty-card.js
├── vmc-helty-card-editor.js
└── translations/
    ├── en.json
    ├── it.json
    ├── fr.json
    ├── de.json
    └── es.json
```

## ⚙️ Configurazione Risorse

### Opzione 1: Solo File JS (Consigliata)
Le traduzioni vengono caricate dinamicamente:

```yaml
resources:
  - url: /local/vmc-helty-card/vmc-helty-card.js
    type: module
  - url: /local/vmc-helty-card/vmc-helty-card-editor.js
    type: module
```

### Opzione 2: Con Traduzioni Esplicite
Per garantire il pre-caricamento:

```yaml
resources:
  - url: /local/vmc-helty-card/vmc-helty-card.js
    type: module
  - url: /local/vmc-helty-card/vmc-helty-card-editor.js
    type: module
  # Translation files
  - url: /local/vmc-helty-card/translations/en.json
    type: json
  - url: /local/vmc-helty-card/translations/it.json
    type: json
  - url: /local/vmc-helty-card/translations/fr.json
    type: json
  - url: /local/vmc-helty-card/translations/de.json
    type: json
  - url: /local/vmc-helty-card/translations/es.json
    type: json
```

## 🔍 Verifica Installazione

1. **Apri Developer Tools** (F12)
2. **Console Tab**
3. **Ricarica la pagina**
4. **Cerca i log**:
   ```
   Loading translations for language: en
   Successfully loaded English translations from: /local/vmc-helty-card/translations/en.json
   Final translations object: {...}
   ```

## 🚨 Troubleshooting

### Errore "Failed to load from /local/..."
- ✅ Verifica che i file siano in `/config/www/vmc-helty-card/translations/`
- ✅ Controlla i permessi dei file
- ✅ Riavvia Home Assistant

### Traduzioni non visibili
- ✅ Apri Developer Tools e verifica i log della console
- ✅ Cancella cache del browser (Ctrl+F5)
- ✅ Verifica che la lingua di HA sia supportata

### Path Alternativi
Se `/local/` non funziona, la card proverà automaticamente:
- `/hacsfiles/vmc_helty_flow/www/vmc-helty-card/translations/`
- `./translations/` (path relativo)

## 📋 Controllo Rapido

```bash
# Verifica che i file esistano
ls -la /config/www/vmc-helty-card/translations/

# Deve mostrare:
# en.json it.json fr.json de.json es.json
```
