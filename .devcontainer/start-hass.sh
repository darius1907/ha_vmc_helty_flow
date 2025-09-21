#!/bin/bash

# Script per avviare Home Assistant con l'integrazione VMC Helty Flow per testing

set -e

# Colori per output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🏠 Avvio Home Assistant per testing VMC Helty Flow...${NC}"

# Directory di configurazione
CONFIG_DIR="/tmp/test_config"
CUSTOM_COMPONENTS_DIR="$CONFIG_DIR/custom_components"

# Assicurati che le directory esistano
mkdir -p "$CUSTOM_COMPONENTS_DIR"

# Crea symlink dell'integrazione se non esiste
if [ ! -L "$CUSTOM_COMPONENTS_DIR/vmc_helty_flow" ]; then
    echo -e "${YELLOW}📁 Creazione symlink per l'integrazione...${NC}"
    ln -sf "/workspaces/vmc_helty_flow/custom_components/vmc_helty_flow" "$CUSTOM_COMPONENTS_DIR/"
fi

# Verifica che il symlink esista
if [ ! -e "$CUSTOM_COMPONENTS_DIR/vmc_helty_flow" ]; then
    echo -e "${RED}❌ Errore: Symlink dell'integrazione non trovato!${NC}"
    exit 1
fi

# Crea configurazione di base se non esiste
if [ ! -f "$CONFIG_DIR/configuration.yaml" ]; then
    echo -e "${YELLOW}⚙️  Creazione configurazione di base...${NC}"
    cat > "$CONFIG_DIR/configuration.yaml" << 'EOF'
# Configurazione di test per VMC Helty Flow

homeassistant:
  name: "Test Home"
  latitude: 45.4642
  longitude: 9.1900
  elevation: 120
  unit_system: metric
  time_zone: "Europe/Rome"
  allowlist_external_dirs:
    - /tmp

# Logger per debugging
logger:
  default: info
  logs:
    custom_components.vmc_helty_flow: debug
    homeassistant.components.fan: debug
    homeassistant.components.light: debug
    homeassistant.components.sensor: debug

# Abilitazioni base
config:
frontend:
api:
history:
logbook:

# Database in memoria per test
recorder:
  db_url: "sqlite:///:memory:"

# System health
system_health:

# Automazioni semplici per test
automation: !include automations.yaml
script: !include scripts.yaml
scene: !include scenes.yaml
EOF

    # Crea file vuoti per evitare errori
    touch "$CONFIG_DIR/automations.yaml"
    touch "$CONFIG_DIR/scripts.yaml"
    touch "$CONFIG_DIR/scenes.yaml"
fi

# Mostra informazioni
echo -e "${GREEN}✅ Configurazione pronta${NC}"
echo -e "${BLUE}📍 Directory configurazione: $CONFIG_DIR${NC}"
echo -e "${BLUE}🔗 Integrazione: $CUSTOM_COMPONENTS_DIR/vmc_helty_flow${NC}"
echo ""

# Funzione per cleanup al termine
cleanup() {
    echo -e "\n${YELLOW}🧹 Pulizia in corso...${NC}"
    if [ -n "$HASS_PID" ] && kill -0 "$HASS_PID" 2>/dev/null; then
        echo -e "${YELLOW}⏹️  Terminazione Home Assistant...${NC}"
        kill "$HASS_PID"
        wait "$HASS_PID" 2>/dev/null || true
    fi
    echo -e "${GREEN}✅ Pulizia completata${NC}"
}

# Intercetta SIGINT (Ctrl+C) e SIGTERM
trap cleanup SIGINT SIGTERM

# Avvia Home Assistant
echo -e "${GREEN}🚀 Avvio Home Assistant...${NC}"
echo -e "${BLUE}🌐 Web UI sarà disponibile su: http://localhost:8123${NC}"
echo -e "${YELLOW}⚠️  Premi Ctrl+C per terminare${NC}"
echo ""

# Esporta variabili d'ambiente
export HASS_CONFIG_DIR="$CONFIG_DIR"
export PYTHONPATH="/workspaces/vmc_helty_flow:$PYTHONPATH"

# Avvia Home Assistant in background per poter catturare il PID
hass --config "$CONFIG_DIR" --verbose &
HASS_PID=$!

# Attendi che il processo termini o venga interrotto
wait "$HASS_PID" 2>/dev/null || true

echo -e "${GREEN}✅ Home Assistant terminato${NC}"
