.DEFAULT_GOAL := help

# ===============================
# VARIABLES
# ===============================
VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
LATEX_SRC := main.tex
LATEX_OUT := main.pdf

# ===============================
# AIDE
# ===============================
help:  ## Affiche cette aide
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ===============================
# ENVIRONNEMENT PYTHON
# ===============================
venv:  ## Crée l’environnement virtuel Python
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip

install: venv  ## Installe les dépendances
	$(PIP) install -r requirements.txt
	-$(PIP) install -r requirements-dev.txt

freeze:  ## Gèle les dépendances dans requirements.txt
	$(PIP) freeze > requirements.txt

dev: install  ## Active l'environnement virtuel dans un shell
	@echo "Activation de l'environnement virtuel. Tapez 'exit' pour quitter."
	@bash --rcfile <(echo "source $(VENV)/bin/activate")

# ===============================
# QUALITÉ & TESTS
# ===============================
lint:  ## Analyse statique avec flake8
	source $(VENV)/bin/activate && flake8 .

lint-fix:  ## Formatte et nettoie automatiquement le code
	black .
	isort .
	flake8 .

format:  ## Formatte le code avec black + isort
	source $(VENV)/bin/activate && black . && isort .

format-check:  ## Vérifie que le code est bien formaté
	source $(VENV)/bin/activate && black --check . && isort --check-only .

test:  ## Lance les tests unitaires (avec log)
	source $(VENV)/bin/activate && pytest --maxfail=1 -v

coverage:  ## Affiche le taux de couverture
	source $(VENV)/bin/activate && pytest --cov=./ --cov-report=term-missing

badge-coverage:  ## Génère un badge de couverture
	pytest --cov > coverage.log
	coverage-badge -o coverage.svg -f
	mkdir -p docs/assets
	mv coverage.svg docs/assets/

validate-schema:  ## Valide les JSON avec jsonschema
	$(PYTHON) scripts/validate_schema.py

check:  ## Vérifie le code : format, lint, validation JSON
	source $(VENV)/bin/activate && \
	black --check . && \
	isort --check-only . && \
	flake8 . && \
	$(PYTHON) scripts/validate_schema.py

# ===============================
# EXÉCUTION
# ===============================
run:  ## Exécute run_parser.py
	$(PYTHON) run_parser.py $(ARGS)

start-server:  ## Lance l'API FastAPI
	uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

frontend:  ## Lance l’interface Streamlit
	streamlit run streamlit_app/app.py

# ===============================
# DOCKER
# ===============================
docker:  ## Lance Docker Compose (mode dev)
	docker compose -f docker-compose.dev.yml up --build

publish-ghcr:  ## Publie l'image sur GitHub Container Registry
	GHCR_PAT=$(GHCR_PAT) ./scripts/publish_ghcr.sh $(VERSION)

# ===============================
# LATEX
# ===============================
pdf:  ## Compile le LaTeX en PDF
	latexmk -pdf -interaction=nonstopmode -output-directory=build $(LATEX_SRC)
	@mv build/$(LATEX_OUT) .

clean-pdf:  ## Supprime les fichiers LaTeX intermédiaires
	@rm -rf build *.aux *.log *.out *.toc *.fls *.fdb_latexmk *.synctex.gz

# ===============================
# RELEASE SÉCURISÉE
# ===============================
secure-release:  ## Compile PDF, calcule le SHA256, archive le tout
	make pdf
	shasum -a 256 main.pdf > main.pdf.sha256
	tar -czf release.tar.gz main.pdf main.pdf.sha256

# ===============================
# NETTOYAGE
# ===============================
clean-pycache:  ## Supprime les caches Python
	@rm -rf __pycache__ */__pycache__ .pytest_cache .mypy_cache *.pyc .coverage

clean:  ## Supprime les fichiers temporaires & locks
	find . -name "__pycache__" -type d -exec rm -rf {} +
	find . -name "*.pyc" -delete
	rm -f .git/index.lock .git/HEAD.lock .git/packed-refs.lock .git/refs/heads/main.lock

clean-all: clean  ## Supprime tout : environnement, dist, build…
	@rm -rf $(VENV) build dist *.egg-info

unlock:  ## Déverrouille le fichier .git/index.lock
	rm -f .git/index.lock

unlock-full:  ## Supprime tous les verrous Git potentiels
	rm -f .git/index.lock .git/HEAD.lock .git/packed-refs.lock .git/refs/heads/main.lock
