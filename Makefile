.DEFAULT_GOAL := help

VENV_DIR_NAME := .venv
VENV_PATH := $(CURDIR)/$(VENV_DIR_NAME)
PYTHON := $(VENV_PATH)/bin/python
PIP := $(VENV_PATH)/bin/pip
SRC_DIRS := bot api tests parser scripts
COV_DIR := tests

.PHONY: help
help:  ## Affiche la liste des commandes disponibles
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Environnement
.PHONY: venv
venv: ## Crée l’environnement virtuel Python
	@echo ">>> Création de l'environnement dans $(VENV_PATH)..."
	python3 -m venv $(VENV_DIR_NAME)
	$(PYTHON) -m pip install --upgrade pip setuptools wheel

.PHONY: install
install: venv ## Installe les dépendances
	@echo ">>> Dépendances requirements.txt"
	$(PIP) install -r requirements.txt
	@echo ">>> Dépendances requirements-dev.txt"
	-$(PIP) install -r requirements-dev.txt || true

.PHONY: rebuild-env
rebuild-env: clean-all install ## Supprime et reconstruit l'environnement

# Lint & format
.PHONY: format
format: ## Formate le code
	$(PYTHON) -m black $(SRC_DIRS) --exclude $(VENV_DIR_NAME)
	$(PYTHON) -m isort $(SRC_DIRS) --skip $(VENV_DIR_NAME)
	$(PYTHON) -m flake8 $(SRC_DIRS) --exclude $(VENV_DIR_NAME)

.PHONY: check
check: ## Vérifie le format (dry run)
	$(PYTHON) -m black $(SRC_DIRS) --check --exclude $(VENV_DIR_NAME)
	$(PYTHON) -m isort $(SRC_DIRS) --check-only --skip $(VENV_DIR_NAME)
	$(PYTHON) -m flake8 $(SRC_DIRS) --exclude $(VENV_DIR_NAME)

.PHONY: lint-fix
lint-fix: ## Auto-correction avec autopep8
	$(PYTHON) -m autopep8 $(SRC_DIRS) --in-place --aggressive --recursive

# Tests
.PHONY: test
test: ## Lance tous les tests
	$(PYTHON) -m pytest $(COV_DIR)

.PHONY: test-unit
test-unit: ## Lance les tests unitaires uniquement
	$(PYTHON) -m pytest $(COV_DIR) -m "not e2e"

.PHONY: test-e2e
test-e2e: ## Lance les tests end-to-end uniquement
	$(PYTHON) -m pytest $(COV_DIR) -m "e2e"

.PHONY: coverage
coverage: ## Affiche la couverture HTML
	$(PYTHON) -m pytest $(COV_DIR) --cov=bot --cov=api --cov-report=html

# Utilitaires
.PHONY: run
run: ## Lance l'application principale
	$(PYTHON) -m bot

.PHONY: doctor
doctor: ## Vérifie l’environnement
	@which $(PYTHON)
	@$(PYTHON) --version
	@$(PYTHON) -c "import black, isort, flake8, pytest; print('✅ Environnement OK')"

.PHONY: clean
clean: ## Nettoie les caches Python
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.py[co]" -delete
	rm -rf .pytest_cache .mypy_cache .coverage htmlcov .tox coverage.xml

.PHONY: clean-all
clean-all: clean ## Supprime l'env virtuel et les builds
	rm -rf $(VENV_DIR_NAME) dist build *.egg-info

.PHONY: unlock
unlock:
	rm -f .git/index.lock .git/HEAD.lock .git/packed-refs.lock .git/refs/heads/*.lock
