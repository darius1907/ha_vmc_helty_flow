#!/bin/bash

# Script per aggiornare i link da gitea.lan a GitHub
# Uso: ./update_links.sh YOUR_GITHUB_USERNAME

if [ -z "$1" ]; then
    echo "❌ Errore: Fornisci il tuo username GitHub"
    echo "Uso: ./update_links.sh YOUR_GITHUB_USERNAME"
    exit 1
fi

GITHUB_USER=$1
REPO_NAME="ha_vmc_helty_flow"

echo "🔄 Aggiornamento link per GitHub..."
echo "👤 Username: $GITHUB_USER"
echo "📦 Repository: $REPO_NAME"
echo ""

# Aggiorna manifest.json
echo "📝 Aggiornamento manifest.json..."
sed -i "s|https://github.com/darius1907/ha_vmc_helty_flow|https://github.com/$GITHUB_USER/$REPO_NAME|g" custom_components/vmc_helty_flow/manifest.json

# Aggiorna README.md
echo "📝 Aggiornamento README.md..."
sed -i "s|darius1907/ha_vmc_helty_flow|$GITHUB_USER/$REPO_NAME|g" README.md
sed -i "s|dpezzoli/ha_vmc_helty_flow|$GITHUB_USER/$REPO_NAME|g" README.md

# Aggiorna INFO.md
echo "📝 Aggiornamento INFO.md..."
sed -i "s|darius1907/ha_vmc_helty_flow|$GITHUB_USER/$REPO_NAME|g" INFO.md
sed -i "s|dpezzoli/ha_vmc_helty_flow|$GITHUB_USER/$REPO_NAME|g" INFO.md

# Aggiorna PUBLISHING_GUIDE.md
echo "📝 Aggiornamento PUBLISHING_GUIDE.md..."
sed -i "s|YOUR_USERNAME|$GITHUB_USER|g" PUBLISHING_GUIDE.md

echo ""
echo "✅ Aggiornamento completato!"
echo ""
echo "📋 Prossimi passi:"
echo "1. Verifica le modifiche con: git diff"
echo "2. Commit: git add . && git commit -m 'chore: Update links to GitHub'"
echo "3. Push su GitHub: git push origin main"
echo "4. Crea release v1.0.0"
echo ""
echo "📚 Consulta PUBLISHING_GUIDE.md per i dettagli completi"
