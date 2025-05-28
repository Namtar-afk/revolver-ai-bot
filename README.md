# 🔧 Revolver AI Bot

[![PyPI](https://img.shields.io/pypi/v/revolver-ai-bot)](https://pypi.org/project/revolver-ai-bot/)
[![Tests](https://github.com/romeocavazza/revolver-ai-bot/actions/workflows/test.yml/badge.svg)](https://github.com/romeocavazza/revolver-ai-bot/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/romeocavazza/revolver-ai-bot/branch/main/graph/badge.svg?token=XXXX)](https://codecov.io/gh/romeocavazza/revolver-ai-bot)
![Coverage](https://img.shields.io/badge/coverage-96%25-brightgreen)

---

## 🤖 Présentation

Revolver AI Bot est un **agent IA full-stack** conçu pour :

- 🔍 **Parser** des briefs PDF → JSON conforme
- 📡 **Automatiser** la veille stratégique (Google, RSS, TikTok…)
- 🧠 **Analyser** avec LLM : insights, KPIs, synthèses
- 📊 **Générer** des slides PPTX professionnels
- 🔗 **Exposer** une API REST FastAPI
- 💬 **Interagir** en bot Slack avec commandes intelligentes

---

## 🚀 Installation

### 1. Depuis PyPI (recommandé)

```bash
pip install revolver-ai-bot
2. En local (développement)
bash
Copy
Edit
git clone https://github.com/romeocavazza/revolver-ai-bot.git
cd revolver-ai-bot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
⚙️ Configuration
Copiez et éditez les secrets nécessaires :

bash
Copy
Edit
cp .env.example secrets/.env
# puis éditez secrets/.env
🧠 Fonctionnalités principales
✅ Parsing PDF → JSON validé

🧠 Analyse automatique (résumé, reformulation, KPIs)

📈 Veille RSS, clustering, Google Trends

🖼️ Génération de slides PowerPoint

🌐 API REST (FastAPI)

💬 Slack bot multi-commandes (/report, !veille, etc.)

📂 Arborescence du projet
graphql
Copy
Edit
revolver-ai-bot/
├── bot/                # Slack, analyse, email
├── api/                # API REST FastAPI
├── parser/             # NLP et parsing PDF
├── pptx_generator/     # Slides PPTX
├── prompts/            # Templates LLM
├── reco/               # Générateur de recommandations
├── schema/             # JSON Schemas
├── tests/              # Unittests & e2e tests
└── run_parser.py       # CLI principale
🧪 Lancer les tests
bash
Copy
Edit
make test
# ou
pytest --cov=bot --cov=api --cov-report=term
🚀 CLI
Parser un brief PDF :

bash
Copy
Edit
python run_parser.py --brief path/to/file.pdf
Générer un rapport PPTX :

bash
Copy
Edit
python run_parser.py --report path/to/output.pptx
Lancer la veille média :

bash
Copy
Edit
python run_monitor.py --out data/veille.csv
🌐 API REST (FastAPI)
bash
Copy
Edit
uvicorn api.main:app --reload --port 8001
# Accès Swagger : http://localhost:8001/docs
💬 Slack Bot
bash
Copy
Edit
export SLACK_BOT_TOKEN="xoxb-..."
export SLACK_APP_TOKEN="xapp-..."
python bot/slack_handler.py
Commandes disponibles :

/report (PDF → slide)

!veille (veille média)

!analyse (résumé + tendances)

🐳 Docker (dev)
bash
Copy
Edit
docker compose -f docker-compose.dev.yml up --build
© 2025 – Revolver AI Bot — par Romeo Cavazza