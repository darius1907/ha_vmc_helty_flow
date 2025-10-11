#!/bin/bash

echo "🚀 Configurazione ambiente di sviluppo per VMC Helty Flow..."

# Aggiorna il PATH per assicurarsi che l'ambiente virtuale sia utilizzato
export PATH="/home/vscode/.local/ha-venv/bin:$PATH"

# Installa le dipendenze di sviluppo se non già installate
echo "📦 Installazione dipendenze di sviluppo..."
pip install --upgrade pip
pip install -e .

# Installa le dipendenze di test
echo "🧪 Installazione dipendenze di test..."
if [ -f "requirements_test.txt" ]; then
    pip install -r requirements_test.txt
fi

# Installa pre-commit hooks
echo "🔧 Configurazione pre-commit..."
if [ -f "requirements_test_pre_commit.txt" ]; then
    pip install -r requirements_test_pre_commit.txt
fi

# Configura pre-commit se il file .pre-commit-config.yaml esiste
if [ -f ".pre-commit-config.yaml" ]; then
    pre-commit install
    echo "✅ Pre-commit hooks configurati"
fi

# Crea la directory di configurazione di Home Assistant per i test
echo "🏠 Configurazione ambiente di test Home Assistant..."
mkdir -p /tmp/test_config
mkdir -p /tmp/test_config/custom_components

# Crea un symlink dell'integrazione nella directory di test
ln -sf /workspaces/vmc_helty_flow/custom_components/vmc_helty_flow /tmp/test_config/custom_components/

# Crea una configurazione minima di Home Assistant per i test
cat > /tmp/test_config/configuration.yaml << 'EOF'
# Configurazione di test per VMC Helty Flow

# Core Home Assistant configuration
homeassistant:
  name: Test Home
  latitude: 45.4642
  longitude: 9.1900
  elevation: 120
  unit_system: metric
  time_zone: Europe/Rome

# Enable the VMC Helty Flow integration
vmc_helty_flow:

# Logger configuration for debugging
logger:
  default: info
  logs:
    custom_components.vmc_helty_flow: debug

# Enable configuration UI
config:

# Enable frontend
frontend:

# Enable API
api:

# Enable recorder (in memory for tests)
recorder:
  db_url: "sqlite:///:memory:"

# Enable history
history:
EOF

# Setup per IntelliJ IDEA
IDEA_DIR="/workspaces/vmc_helty_flow/.idea"
INTELLIJ_CONFIG_DIR="/workspaces/vmc_helty_flow/.devcontainer/intellij"

# Crea la cartella .idea se non esiste
mkdir -p "$IDEA_DIR"

# Crea un file misc.xml minimale per l'interprete Python
cat > "$IDEA_DIR/misc.xml" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<project version="4">
  <component name="ProjectRootManager" version="2" project-jdk-name="Home Assistant Python" project-jdk-type="Python SDK" />
</project>
EOF

# Copia configurazioni aggiuntive se presenti
if [ -d "$INTELLIJ_CONFIG_DIR" ]; then
    cp -r "$INTELLIJ_CONFIG_DIR"/* "$IDEA_DIR/"
fi

echo "✅ Ambiente di sviluppo configurato!"
echo ""
echo "🔍 Comandi utili:"
echo "  - pytest tests/                    # Esegui tutti i test"
echo "  - pytest tests/ -v                # Esegui test in modalità verbose"
echo "  - pytest tests/ -k test_name      # Esegui test specifico"
echo "  - python -m pylint custom_components/vmc_helty_flow/  # Linting"
echo "  - python -m mypy custom_components/vmc_helty_flow/    # Type checking"
echo "  - hass --config /tmp/test_config  # Avvia Home Assistant per test"
echo ""
echo "📁 Configurazione di test creata in: /tmp/test_config"
