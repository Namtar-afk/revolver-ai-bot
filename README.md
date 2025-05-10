# Revolver AI Bot

**Agent IA pour l’ingestion de briefs, veille média et génération de livrables (PDF, PPT) via Slack & CLI**

## Installation

1. Cloner le dépôt :
   ```bash
   git clone https://github.com/Namtar-afk/revolver-ai-bot.git
   cd revolver-ai-bot
   ```
2. Créer et activer un environnement virtuel :
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
3. Installer les dépendances :
   ```bash
   pip install -r requirements.txt
   ```
4. Copier la configuration exemple :
   ```bash
   cp config.example.py config.py
   ```
5. Renseigner vos jetons et clés (Slack, Google, SerpAPI…) dans `config.py` ou via variables d'environnement.

## Structure du projet

```
├── bot/                # Handlers Slack, orchestrator, monitoring, email
├── parser/             # Extraction PDF → texte → sections NLU
├── schema/             # JSON Schema pour validation des briefs
├── utils/              # Logger et outils génériques
├── scripts/            # Génération de samples et utilitaires
├── tests/              # Tests unitaires et d’intégration
├── run_parser.py       # CLI : parsing + validation
├── run_monitor.py      # CLI : veille média (RSS, Trends, Social)
├── data/               # Dossier de sortie (veille.csv…)
└── README.md           # Documentation
```

## CLI

### Parsing de brief
```bash
python run_parser.py            # Exécute parsing/validation sur tests/samples/brief_sample.pdf
```

### Veille média
```bash
python run_monitor.py --out data/veille.csv
```
- Agrège RSS, Google Trends et scraping social
- Enregistre `data/veille.csv`

### Slack (simulateur)
```bash
# Simule l’upload d’un PDF local
python bot/slack_handler.py --simulate

# Lance la veille depuis Slack en CLI
python bot/slack_handler.py --veille
```

## Slack (production)

1. Démarrer le bot en mode réel :
   ```bash
   export SLACK_BOT_TOKEN="xoxb-..."
   export SLACK_APP_TOKEN="xapp-..."
   python bot/slack_handler.py
   ```
2. Dans un canal :
   - Taper `!veille` → le bot relance la veille et renvoie le nombre d’items.
   - Uploader un PDF → le bot extrait et affiche les sections `{problem, objectives, KPIs}`.

## Tests

```bash
export PYTHONPATH=$(pwd)
pytest -q
```

## Roadmap rapide

1. **Jour 1** – Fondations & parsing
2. **Jour 2** – Veille automatisée & stockage
3. **Jour 3** – Analyse & recommandations (PDF/PPT)
4. **Jour 4** – Containerisation, CI/CD & livrables académiques

---

*Revolver AI Bot – Architecture modulaire 100% Python, full Slack & CLI.*