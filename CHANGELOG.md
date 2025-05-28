# Changelog

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

## [Unreleased]

### Ajouté
- Simulation CLI Slack (`--simulate`), commandes `!veille` et `!analyse` via Docker `slack-cli`.
- Endpoint FastAPI pour upload PDF dans `api/main.py`.

### Corrigé
- Erreurs `python-multipart` manquant dans l’API.
- Chemin des modules utils/slack_handler ajusté.

---

## [v0.1.0] - 2025-05-17

### Ajouté
- Première version stable du parseur de brief (`run_parser.py`).
- Intégration de `pdfplumber` pour l’extraction de texte.
- Handlers Slack + simulation CLI + tests pytest.

### Changé
- Passage à FastAPI 0.115 et python-multipart pour l’upload de PDF.
- Standardisation des logs avec `utils/logger`.

