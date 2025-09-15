.PHONY: help test test-cov lint typecheck format install clean hass setup pre-commit

# Colori per output
RED=\033[0;31m
GREEN=\033[0;32m
YELLOW=\033[1;33m
BLUE=\033[0;34m
NC=\033[0m # No Color

help: ## Mostra questo help
	@echo -e "${BLUE}Comandi disponibili per VMC Helty Flow:${NC}\n"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "${GREEN}%-15s${NC} %s\n", $$1, $$2}'

test: ## Esegue tutti i test
	@echo -e "${YELLOW}🧪 Esecuzione test...${NC}"
	pytest tests/ -v

test-cov: ## Esegue test con coverage
	@echo -e "${YELLOW}📊 Esecuzione test con coverage...${NC}"
	pytest tests/ --cov=custom_components.vmc_helty_flow --cov-report=html --cov-report=term

test-fast: ## Esegue test veloci (senza coverage)
	@echo -e "${YELLOW}⚡ Test veloci...${NC}"
	pytest tests/ -x --tb=short

lint: ## Esegue pylint
	@echo -e "${YELLOW}🔍 Linting codice...${NC}"
	pylint custom_components/vmc_helty_flow/

typecheck: ## Esegue controllo tipi con mypy
	@echo -e "${YELLOW}🔎 Type checking...${NC}"
	mypy custom_components/vmc_helty_flow/

format: ## Formatta il codice con black e ruff
	@echo -e "${YELLOW}🎨 Formattazione codice...${NC}"
	black .
	ruff check . --fix

quality: lint typecheck ## Esegue tutti i controlli di qualità
	@echo -e "${GREEN}✅ Controlli qualità completati${NC}"

install: ## Installa dipendenze di sviluppo
	@echo -e "${YELLOW}📦 Installazione dipendenze...${NC}"
	pip install --upgrade pip
	pip install -r requirements_test.txt
	pip install -e .

install-pre-commit: ## Installa pre-commit hooks
	@echo -e "${YELLOW}🔧 Installazione pre-commit hooks...${NC}"
	pre-commit install

setup: install install-pre-commit ## Setup completo ambiente
	@echo -e "${GREEN}✅ Setup ambiente completato${NC}"

clean: ## Pulisce file temporanei
	@echo -e "${YELLOW}🧹 Pulizia file temporanei...${NC}"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/

hass: ## Avvia Home Assistant per testing
	@echo -e "${BLUE}🏠 Avvio Home Assistant...${NC}"
	.devcontainer/start-hass.sh

hass-config: ## Mostra configurazione Home Assistant di test
	@echo -e "${BLUE}📁 Configurazione Home Assistant:${NC}"
	@echo -e "${YELLOW}Directory:${NC} /tmp/test_config"
	@echo -e "${YELLOW}URL:${NC} http://localhost:8123"
	@ls -la /tmp/test_config/ 2>/dev/null || echo "Configurazione non ancora creata"

pre-commit: ## Esegue pre-commit su tutti i file
	@echo -e "${YELLOW}🔧 Esecuzione pre-commit...${NC}"
	pre-commit run --all-files

check-all: format quality test ## Esegue tutti i controlli (format, quality, test)
	@echo -e "${GREEN}🎉 Tutti i controlli completati con successo!${NC}"

# Target per CI/CD
ci: install quality test ## Target per CI/CD
	@echo -e "${GREEN}✅ Pipeline CI completata${NC}"

dev: setup ## Alias per setup
	@echo -e "${GREEN}🚀 Ambiente di sviluppo pronto!${NC}"
	@echo -e "${BLUE}Comandi utili:${NC}"
	@echo -e "  ${GREEN}make test${NC}     - Esegui test"
	@echo -e "  ${GREEN}make hass${NC}     - Avvia Home Assistant"
	@echo -e "  ${GREEN}make quality${NC}  - Controlli qualità"
	@echo -e "  ${GREEN}make help${NC}     - Mostra tutti i comandi"
