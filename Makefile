# === Config ===
PYTHON := python
PIP := pip
VENV := .venv
ACTIVATE := source $(VENV)/bin/activate

# === Commands ===

.PHONY: help init install test lint format run clean reset

help:
	@echo "Makefile – commandes disponibles :"
	@echo "  make init         → crée l'environnement virtuel"
	@echo "  make install      → installe les dépendances"
	@echo "  make test         → lance les tests unitaires"
	@echo "  make lint         → vérifie la qualité du code"
	@echo "  make format       → reformate avec black + isort"
	@echo "  make run          → exécute le script CLI principal"
	@echo "  make clean        → supprime les fichiers temporaires"
	@echo "  make reset        → reset complet (venv + caches)"

# === Setup ===

init:
	@test -d $(VENV) || python3 -m venv $(VENV)
	@$(ACTIVATE) && $(PIP) install --upgrade pip

install:
	@$(ACTIVATE) && $(PIP) install -r requirements.txt

# === Dev tools ===

test:
	@$(ACTIVATE) && pytest -vv tests

lint:
	@$(ACTIVATE) && flake8 reco parser

format:
	@$(ACTIVATE) && black . && isort .

# === Run main CLI ===

run:
	@$(ACTIVATE) && $(PYTHON) run_parser.py --help

# === Maintenance ===

clean:
	find . -type d -name '__pycache__' -exec rm -rf {} +
	rm -rf .pytest_cache .mypy_cache .coverage htmlcov

reset: clean
	rm -rf $(VENV)
