# 🔧 Configurazione Risorse Lovelace

## 📁 Struttura File da Copiare

Assicurati di copiare **TUTTI** i file nella cartella corretta:

```bash
/config/www/vmc-helty-card/
├── vmc-helty-card.js
├── vmc-helty-card-editor.js
└── translations/
    ├── en.json
    ├── it.json (DEFAULT)
    ├── fr.json
    ├── de.json
    └── es.json
```

## ⚙️ Configurazione Risorse

### ✅ CONFIGURAZIONE CORRETTA
Aggiungi SOLO i file JavaScript:

```yaml
resources:
  - url: /local/vmc-helty-card/vmc-helty-card.js
    type: module
  - url: /local/vmc-helty-card/vmc-helty-card-editor.js
    type: module
```

### ⚠️ IMPORTANTE: NON Aggiungere i JSON alle Risorse
I file di traduzione (.json) NON devono essere nelle risorse Lovelace perché:
- ❌ Causano errori MIME type ("Refused to apply style... not a supported stylesheet MIME type")
- ❌ Vengono caricati dinamicamente via JavaScript fetch()
- ❌ Home Assistant interpreta erroneamente il tipo di file

## 🇮🇹 Lingua Predefinita: Italiano

- **Default**: Italiano (it.json)
- **Fallback**: Inglese se italiano non disponibile
- **Auto-detect**: Usa la lingua di Home Assistant se disponibile
- **Lingue supportate**: IT, EN, FR, DE, ES

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
