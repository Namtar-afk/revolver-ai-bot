![Tests](https://github.com/romeocavazza/revolver-ai-bot/actions/workflows/test.yml/badge.svg)
[![codecov](https://codecov.io/gh/romeocavazza/revolver-ai-bot/branch/main/graph/badge.svg)](https://codecov.io/gh/romeocavazza/revolver-ai-bot)

# 🤖 Revolver AI Bot

Agent IA full-stack pour ingestion de briefs, veille stratégique, analyse automatique et génération de livrables professionnels (PDF, PPTX, API). Compatible Slack, CLI et FastAPI.

---

## 🚀 Installation rapide

### 1. Cloner le dépôt

```bash
git clone https://github.com/Namtar-afk/revolver-ai-bot.git
cd revolver-ai-bot
```

### 2. Environnement virtuel

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Clés API et config

```bash
cp config.example.py config.py
# Puis éditez `config.py` avec vos clés (OpenAI, Slack, Google, SerpAPI...)
```

## 🧠 Fonctionnalités principales

- ✨ Parsing intelligent de briefs PDF → JSON valide
- 📊 Analyse automatisée via LLM (insights, KPIs, hypothèses…)
- 📈 Agrégation et clustering de veille (RSS, Google, TikTok…)
- 🗞️ Génération de slides .pptx (Deck complet)
- 🧪 API REST (FastAPI) pour intégration facile
- 💬 Mode Slack bot interactif

## 🗂 Structure du projet

```
revolver-ai-bot/
├── bot/                ← Slack handler + veille + analyse
├── parser/             ← Extraction et NLP des briefs PDF
├── pptx_generator/     ← Génération de PowerPoint
├── prompts/            ← Templates markdown pour GPT
├── reco/               ← Recommandation stratégique (LLM + logique)
├── schema/             ← JSON Schema pour validation
├── api/                ← FastAPI server (REST endpoints)
├── tests/              ← Unitaires, intégration et snapshots
├── run_parser.py       ← CLI : PDF → JSON/PPTX
├── run_monitor.py      ← CLI : veille
└── README.md
```

## 🧪 Tests unitaires

```bash
export PYTHONPATH=$(pwd)
pytest -v
```

Couverture : extraction, parsing, génération, intégration, Slack.

## 🖥 Utilisation CLI

### 1. Parser un brief

```bash
python run_parser.py
```

### 2. Générer un rapport complet (.pptx)

```bash
python run_parser.py --report output.pptx
```

### 3. Lancer la veille

```bash
python run_monitor.py --out data/veille.csv
```

## 🌐 API (FastAPI)

Démarrer le serveur :

```bash
uvicorn api.main:app --reload --port 8001
```

→ Accès live : http://127.0.0.1:8001/docs

## 💬 Slack bot

Démarrer :

```bash
export SLACK_BOT_TOKEN="xoxb-..."
export SLACK_APP_TOKEN="xapp-..."
python bot/slack_handler.py
```

Commandes supportées :

- `!veille` — récupère et affiche la veille
- `!analyse` — affiche les clusters de tendance
- `!report` — génère un rapport PPT depuis Slack

### Mode debug :

```bash
python bot/slack_handler.py --simulate
```