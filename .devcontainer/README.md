# DevContainer per VMC Helty Flow

Questa configurazione devcontainer ti permette di sviluppare e testare l'integrazione VMC Helty Flow per Home Assistant in un ambiente isolato e standardizzato.

## 🚀 Avvio rapido

1. **Apri in VS Code**: Assicurati di avere VS Code con l'estensione "Dev Containers" installata
2. **Ricostruisci container**: `Ctrl+Shift+P` → "Dev Containers: Rebuild Container"
3. **Attendi la configurazione**: Il setup automatico installerà tutte le dipendenze

## 🛠️ Funzionalità incluse

### Strumenti di sviluppo
- **Python 3.12** con ambiente virtuale configurato
- **Home Assistant Core** pre-installato
- **Pytest** per testing
- **Pylint** e **MyPy** per quality assurance
- **Black** e **Ruff** per formattazione automatica
- **Pre-commit** hooks per controlli automatici

### Estensioni VS Code
- Python support completo (Pylance, debugging)
- Linting e type checking integrati
- GitHub Copilot
- YAML support per Home Assistant

### Configurazioni predefinite
- Ambiente di test Home Assistant in `/tmp/test_config`
- Symlink automatico dell'integrazione
- Configurazioni per linting, testing e formattazione
- Tasks VS Code per operazioni comuni

## 📋 Comandi principali

### Tasks VS Code (Ctrl+Shift+P → "Tasks: Run Task")
- **Run Tests**: Esegue tutti i test
- **Run Tests with Coverage**: Test con report di copertura
- **Lint Code**: Verifica qualità del codice
- **Type Check**: Controllo tipi con MyPy
- **Format Code**: Formattazione con Black
- **Start Home Assistant**: Avvia HA per testing
- **Run Pre-commit**: Esegue tutti i controlli di qualità

### Debugging
- **F5**: Debug del file corrente
- **Ctrl+F5**: Esegui senza debug
- Configurazioni preimpostate per Home Assistant e test

### Comandi terminale
```bash
# Test
pytest tests/                              # Tutti i test
pytest tests/ -v                          # Test verbose
pytest tests/ -k test_name                 # Test specifico
pytest tests/ --cov --cov-report=html     # Con coverage

# Quality assurance
pylint custom_components/vmc_helty_flow/   # Linting
mypy custom_components/vmc_helty_flow/     # Type checking
black .                                    # Formattazione
ruff check .                               # Linting veloce

# Pre-commit
pre-commit run --all-files                # Tutti i controlli
pre-commit install                         # Installa hooks

# Home Assistant
.devcontainer/start-hass.sh               # Avvia Home Assistant
hass --config /tmp/test_config             # Avvio manuale
```

## 🏠 Testing con Home Assistant

L'ambiente include una configurazione Home Assistant pre-configurata:

- **URL**: http://localhost:8123
- **Config**: `/tmp/test_config`
- **Integrazione**: Automaticamente collegata via symlink
- **Database**: SQLite in memoria (per test)
- **Logging**: Debug abilitato per l'integrazione

### Configurazione di test

La configurazione in `/tmp/test_config/configuration.yaml` include:
- Setup base di Home Assistant
- Logging debug per VMC Helty Flow
- Frontend web abilitato
- Database in memoria per test veloci

## 🔧 Struttura file di configurazione

```
.devcontainer/
├── devcontainer.json          # Configurazione principale
├── setup.sh                   # Script di inizializzazione
├── start-hass.sh              # Script per avviare Home Assistant
└── .env                       # Variabili d'ambiente

.vscode/
├── tasks.json                 # Tasks predefiniti
├── launch.json                # Configurazioni debug
└── settings.json              # Impostazioni specifiche

# File di configurazione qualità codice
pyproject.toml                 # Pytest, MyPy, Ruff, Black
.pylintrc                      # Configurazione Pylint
.pre-commit-config.yaml        # Pre-commit hooks
```

## 📊 Coverage e reporting

I test generano automaticamente:
- **Coverage HTML**: `htmlcov/index.html`
- **Coverage terminal**: Output diretto
- **Pytest reports**: File di log dettagliati

## 🔍 Debugging avanzato

### Configurazioni disponibili
1. **Python: Current File** - Debug del file corrente
2. **Python: Test Current File** - Debug del test corrente
3. **Home Assistant** - Debug di Home Assistant completo
4. **Debug Tests** - Debug di tutti i test

### Breakpoints
- Imposta breakpoints normalmente in VS Code
- `justMyCode: false` permette debug nel codice di Home Assistant
- Variabili d'ambiente automaticamente configurate

## 🚨 Troubleshooting

### Container non si avvia
```bash
# Ricostruisci da zero
Ctrl+Shift+P → "Dev Containers: Rebuild Container"
```

### Test falliscono
```bash
# Verifica dipendenze
pip install -r requirements_test.txt

# Controlla configurazione
pytest --collect-only
```

### Home Assistant non si avvia
```bash
# Controlla symlink
ls -la /tmp/test_config/custom_components/

# Riavvia script
.devcontainer/start-hass.sh
```

### Problemi di permessi
```bash
# Imposta permessi script
chmod +x .devcontainer/*.sh
```

## 📚 Risorse utili

- [Home Assistant Developer Docs](https://developers.home-assistant.io/)
- [Home Assistant Integration Quality Scale](https://developers.home-assistant.io/docs/integration_quality_scale/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Pre-commit Documentation](https://pre-commit.com/)

## 🎯 Best practices

1. **Esegui sempre i test** prima di fare commit
2. **Usa pre-commit hooks** per controlli automatici
3. **Mantieni alta la coverage** (target: 80%+)
4. **Segui le convenzioni** di Home Assistant
5. **Testa con Home Assistant** reale prima del rilascio
