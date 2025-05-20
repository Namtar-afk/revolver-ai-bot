.DEFAULT_GOAL := help

# -------------------------------
# Variables
# -------------------------------
VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
LATEX_SRC := main.tex
LATEX_OUT := main.pdf

# -------------------------------
# Aide
# -------------------------------
help:  ## Affiche l’aide
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# -------------------------------
# Environnement Python
# -------------------------------
venv:  ## Crée l’environnement virtuel
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip

install: venv  ## Installe les dépendances (prod + dev)
	$(PIP) install -r requirements.txt
	-$(PIP) install -r requirements-dev.txt

freeze:  ## Gèle les dépendances dans requirements.txt
	$(PIP) freeze > requirements.txt

# -------------------------------
# Code Quality / Tests
# -------------------------------
lint:  ## Lint avec flake8
	source $(VENV)/bin/activate && flake8 .

format:  ## Formatte le code avec black + isort
	source $(VENV)/bin/activate && black . && isort .

test:  ## Lance les tests avec pytest
	source $(VENV)/bin/activate && pytest --maxfail=1 -v

# -------------------------------
# Run & Serveur
# -------------------------------
run:  ## Lance le parseur CLI
	.venv/bin/python run_parser.py $(ARGS)

start-server:  ## Démarre l’API FastAPI
	uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# -------------------------------
# Docker
# -------------------------------
docker:  ## Lance Docker Compose (dev)
	docker compose -f docker-compose.dev.yml up --build

publish-ghcr:  ## Publie sur GitHub Container Registry
	GHCR_PAT=$(GHCR_PAT) ./scripts/publish_ghcr.sh $(VERSION)

# -------------------------------
# LaTeX
# -------------------------------
pdf:  ## Compile le PDF LaTeX
	latexmk -pdf -interaction=nonstopmode -output-directory=build $(LATEX_SRC)
	@mv build/$(LATEX_OUT) .

clean-pdf:  ## Nettoie les fichiers LaTeX temporaires
	@rm -rf build *.aux *.log *.out *.toc *.fls *.fdb_latexmk *.synctex.gz

# -------------------------------
# Nettoyage général
# -------------------------------
clean: clean-pdf  ## Nettoie tous les fichiers inutiles
	@rm -rf __pycache__ .pytest_cache .mypy_cache *.pyc .coverage
