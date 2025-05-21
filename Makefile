.DEFAULT_GOAL := help

# ---------------------------------
# Variables
# ---------------------------------
VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
LATEX_SRC := main.tex
LATEX_OUT := main.pdf

# ---------------------------------
# Aide
# ---------------------------------
help:  ## Affiche l’aide
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ---------------------------------
# Environnement Python
# ---------------------------------
venv:  ## Crée l’environnement virtuel Python
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip

install: venv  ## Installe les dépendances (prod + dev)
	$(PIP) install -r requirements.txt
	-$(PIP) install -r requirements-dev.txt

freeze:  ## Gèle les dépendances dans requirements.txt
	$(PIP) freeze > requirements.txt

dev: install  ## Ouvre un shell bash dans l'environnement virtuel
	@echo "Activation de l'environnement virtuel. Tapez 'exit' pour quitter."
	@bash --rcfile <(echo "source $(VENV)/bin/activate")

# ---------------------------------
# Qualité du code & Tests
# ---------------------------------
lint:  ## Analyse statique avec flake8
	source $(VENV)/bin/activate && flake8 .

format:  ## Formatte le code avec black et isort
	source $(VENV)/bin/activate && black . && isort .

format-check:  ## Vérifie si le code est bien formaté
	source $(VENV)/bin/activate && black --check . && isort --check-only .

test:  ## Lance les tests
	source $(VENV)/bin/activate && pytest --maxfail=1 -v

coverage:  ## Tests + couverture
	source $(VENV)/bin/activate && pytest --cov=./ --cov-report=term-missing

# ---------------------------------
# Exécution & Serveur
# ---------------------------------
run:  ## Lance le parseur CLI
	$(PYTHON) run_parser.py $(ARGS)

start-server:  ## Démarre l’API FastAPI
	uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# ---------------------------------
# Docker
# ---------------------------------
docker:  ## Lance Docker Compose dev
	docker compose -f docker-compose.dev.yml up --build

publish-ghcr:  ## Publie sur GHCR
	GHCR_PAT=$(GHCR_PAT) ./scripts/publish_ghcr.sh $(VERSION)

# ---------------------------------
# LaTeX
# ---------------------------------
pdf:  ## Compile PDF avec latexmk
	latexmk -pdf -interaction=nonstopmode -output-directory=build $(LATEX_SRC)
	@mv build/$(LATEX_OUT) .

clean-pdf:  ## Nettoie les fichiers LaTeX
	@rm -rf build *.aux *.log *.out *.toc *.fls *.fdb_latexmk *.synctex.gz

# ---------------------------------
# Nettoyage
# ---------------------------------
clean-pycache:  ## Supprime les caches Python
	@rm -rf __pycache__ */__pycache__ .pytest_cache .mypy_cache *.pyc .coverage

clean:  ## Nettoyage des artefacts Python + locks
	find . -name "__pycache__" -type d -exec rm -rf {} +
	find . -name "*.pyc" -delete
	rm -f .git/index.lock .git/HEAD.lock

clean-all: clean  ## Nettoyage total
	@rm -rf $(VENV) build dist *.egg-info

unlock:  ## Déverrouille Git (.git/index.lock uniquement)
	rm -f .git/index.lock

unlock-full:  ## Déverrouille Git totalement (.git/index.lock + HEAD.lock)
	rm -f .git/index.lock .git/HEAD.lock

