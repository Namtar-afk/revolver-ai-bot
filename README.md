# 🔧 Revolver AI Bot

[![PyPI](https://img.shields.io/pypi/v/revolver-ai-bot)](https://pypi.org/project/revolver-ai-bot/)
[![Tests](https://github.com/romeocavazza/revolver-ai-bot/actions/workflows/test.yml/badge.svg)](https://github.com/romeocavazza/revolver-ai-bot/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/romeocavazza/revolver-ai-bot/branch/main/graph/badge.svg)](https://codecov.io/gh/romeocavazza/revolver-ai-bot)
![Coverage](docs/assets/coverage.svg)

---

## 🤖 Présentation

Revolver AI Bot est un agent IA full-stack conçu pour :

* **Parser** des briefs PDF et en extraire des JSON structurés
* **Automatiser** la veille stratégique (RSS, Google, TikTok…)
* **Analyser** les données via LLM (insights, KPIs, tendances)
* **Générer** des livrables professionnels (PDF, PPTX)
* **Fournir** une API REST (FastAPI) pour intégration
* **Intégrer** un mode Slack bot interactif

## 🚀 Installation

### 1. Via PyPI

```bash
pip install revolver-ai-bot
```

### 2. En local (développement)

```bash
git clone https://github.com/romeocavazza/revolver-ai-bot.git
cd revolver-ai-bot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## ⚙️ Configuration

Copiez le fichier de configuration exemple et ajustez vos clés :

```bash
cp config.example.py config.py
# Éditez config.py (OpenAI, Slack, SerpAPI…)
```

## 🧠 Fonctionnalités principales

* **Parsing intelligent** de briefs PDF → JSON valide
* **Analyse automatique** (résumé, reformulation, KPIs)
* **Veille agrégée** et clustering d’actualités
* **Génération de slides** (.pptx)
* **API REST** (FastAPI) et docs Swagger `/docs`
* **Slack bot** multi-commandes

## 📂 Structure du projet

```plain
revolver-ai-bot/
├── bot/                # Gestion Slack, veille, analyse
├── parser/             # Extraction de texte et NLP
├── pptx_generator/     # Génération PowerPoint
├── prompts/            # Templates pour LLM
├── reco/               # Recommandations stratégiques
├── schema/             # JSON Schema de validation
├── api/                # Serveur FastAPI
├── tests/              # Tests unitaires et d’intégration
├── run_parser.py       # CLI : PDF → JSON/PPTX
└── run_monitor.py      # CLI : veille média
```

## 🧪 Tests

```bash
export PYTHONPATH=$(pwd)
pytest -v
```

## 🖥️ Utilisation CLI

* **Parser un brief PDF**

  ```bash
  python run_parser.py --brief path/to/brief.pdf
  ```

* **Générer un PPTX**

  ```bash
  python run_parser.py --report output.pptx
  ```

* **Lancer la veille média**

  ```bash
  python run_monitor.py --out data/veille.csv
  ```

## 🌐 API (FastAPI)

```bash
uvicorn api.main:app --reload --port 8001
# Accédez aux docs : http://127.0.0.1:8001/docs
```

## 💬 Slack Bot

```bash
export SLACK_BOT_TOKEN="xoxb-..."
export SLACK_APP_TOKEN="xapp-..."
python bot/slack_handler.py
```

* **!veille** : récupère et affiche la veille
* **!analyse** : synthèse & tendances
* **/report \[fichier]** : génère un PPTX

## 🐳 Docker (développement)

```bash
docker compose -f docker-compose.dev.yml up --build
# Pour simuler : docker compose run --rm slack-cli --simulate
```

---

*© 2025 Revolver AI Bot — par Romeo Cavazza*
