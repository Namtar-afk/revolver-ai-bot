.DEFAULT_GOAL := help

VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

help:  ## Affiche cette aide
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

venv:  ## Crée un environnement virtuel Python
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip

install: venv  ## Installe les dépendances du projet
	$(PIP) install -r requirements.txt
	$(PIP) install -r requirements-dev.txt || true

test:  ## Lance les tests avec pytest
	source $(VENV)/bin/activate && pytest --maxfail=1 -v

lint:  ## Lint le code Python
	source $(VENV)/bin/activate && flake8 .

run:  ## Lance le parseur CLI
	source $(VENV)/bin/activate && $(PYTHON) run_parser.py --help

docker:  ## Lance le projet avec Docker Compose
	docker compose -f docker-compose.dev.yml up --build

publish-ghcr:
	GHCR_PAT=$(GHCR_PAT) ./scripts/publish_ghcr.sh $(VERSION)
