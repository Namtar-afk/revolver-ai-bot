import os
import pytest
from dotenv import load_dotenv

# Charger automatiquement les variables d'environnement depuis un fichier .env à la racine du projet
load_dotenv()

REQUIRED_ENV_VARS = [
    # Slack
    "SLACK_BOT_TOKEN",
    "SLACK_SIGNING_SECRET",

    # SerpAPI
    "SERPAPI_API_KEY",

    # Gmail
    "GMAIL_USER",
    "GMAIL_APP_PASSWORD",

    # Google Sheets
    "GOOGLE_SHEET_ID",

    # Serveur
    "HOST",
    "PORT"
]


def test_all_required_env_vars_are_set():
    """
    Vérifie que toutes les variables d’environnement critiques sont bien définies.
    """
    missing_vars = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
    
    if missing_vars:
        missing_str = ", ".join(missing_vars)
        raise AssertionError(
            f"Les variables d’environnement suivantes sont manquantes ou vides : {missing_str}"
        )

