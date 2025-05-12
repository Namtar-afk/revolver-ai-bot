# Revolver AI Bot

Agent IA pour l'ingestion de briefs, la veille média, et la génération automatique de livrables (PDF, PPTX) via Slack ou ligne de commande.

---

## 🚀 Installation rapide

1. **Cloner le dépôt :**

```bash
git clone https://github.com/Namtar-afk/revolver-ai-bot.git
cd revolver-ai-bot
```

2. **Créer un environnement virtuel :**

```bash
python3 -m venv venv
source venv/bin/activate
```

3. **Installer les dépendances :**

```bash
pip install -r requirements.txt
```

4. **Configurer les clés API :**

```bash
cp config.example.py config.py
# Puis éditer config.py avec vos jetons : Slack, Google, SerpAPI, OpenAI...
```

---

## 📁 Structure du projet

```
revolver-ai-bot/
├── bot/                # Slack handler, veille, analyse, orchestration
├── parser/             # Extraction PDF → texte → sections intelligibles
├── pptx_generator/     # Génération de slides avec python-pptx
├── prompts/            # Prompts LLM utilisés pour les générations
├── reco/               # Moteur de recommandation + modèles Pydantic
├── schema/             # JSON schemas pour valider les briefs en entrée
├── utils/              # Outils génériques et logs
├── scripts/            # Samples, générateurs, helpers
├── tests/              # Unitaires et intégration
├── data/               # Données générées (veille.csv, etc.)
├── run_parser.py       # CLI brief : parse + validate (+ --report)
├── run_monitor.py      # CLI veille média
└── README.md           # Ce fichier
```

---

## 💻 Utilisation CLI

### 1. Parser un brief statique

```bash
python run_parser.py
```

> Utilise `tests/samples/brief_sample.pdf` par défaut.

### 2. Générer un rapport PPTX complet

```bash
python run_parser.py --report output.pptx
```

> Chaine complète : brief → veille → analyse → reco → PPT.

### 3. Exécuter la veille

```bash
python run_monitor.py --out data/veille.csv
```

> Agrège RSS, tendances Google, signaux sociaux...

### 4. Analyse des données de veille

```bash
python bot/orchestrator.py --analyse
```

> Génère les thèmes à partir de la veille.

---

## 🔊 Intégration Slack

### Configuration (env vars)

```bash
export SLACK_BOT_TOKEN="xoxb-..."
export SLACK_APP_TOKEN="xapp-..."
```

### Démarrer le bot

```bash
python bot/slack_handler.py
```

### Commandes disponibles

* `!veille` : relance la veille et affiche les résultats
* `!analyse` : affiche les thèmes et tendances
* `!report` : génère un rapport complet PPT

### Mode simulateur

```bash
python bot/slack_handler.py --simulate
```

> Permet de tester les commandes sans Slack.

---

## 🧪 Tests unitaires

### Tout lancer :

```bash
export PYTHONPATH=$(pwd)
pytest -q
```

### Tester l'analyse localement

```bash
./run_cli_analyse_test.sh
```

---

### Version actuelle : `v0.2`

> Prochaine étape : génération de publication (article scientifique, annexes, simulations).
