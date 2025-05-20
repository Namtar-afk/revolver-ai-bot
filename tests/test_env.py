import os
import re
import pytest
from dotenv import load_dotenv

# Charge automatiquement les variables d’environnement depuis le fichier .env
load_dotenv()

# Définition des variables obligatoires et de leur format attendu (regex)
REQUIRED_ENV_VARS = {
    "SLACK_BOT_TOKEN": r"^xoxb-[a-zA-Z0-9\-]+$",
    "SLACK_SIGNING_SECRET": r"^[a-f0-9]{32}$",
    "SERPAPI_API_KEY": r"^[a-f0-9]{64}$",
    "GMAIL_USER": r"^[^@]+@[^@]+\.[^@]+$",
    "GMAIL_APP_PASSWORD": r"^[a-z0-9 ]{16,}$",
    "GOOGLE_SHEET_ID": r"^[a-zA-Z0-9-_]{20,}$",
    "HOST": r"^(localhost|0\.0\.0\.0|127\.0\.0\.1|[0-9]{1,3}(\.[0-9]{1,3}){3})$",
    "PORT": r"^\d{2,5}$",
}

def test_all_required_env_vars_are_set_and_valid():
    """
    Vérifie que toutes les variables d’environnement critiques sont bien définies et valides.
    """
    missing_vars = []
    invalid_vars = []

    for var, pattern in REQUIRED_ENV_VARS.items():
        val = os.getenv(var)
        if val is None:
            missing_vars.append(var)
        elif not re.match(pattern, val):
            invalid_vars.append((var, val))

    if missing_vars or invalid_vars:
        error_msg = ""
        if missing_vars:
            error_msg += f"\n[❌] Variables manquantes : {', '.join(missing_vars)}"
        if invalid_vars:
            error_msg += "\n[⚠️] Variables invalides :"
            for var, val in invalid_vars:
                error_msg += f"\n   - {var} = {val} (format invalide)"

        raise AssertionError(error_msg.strip())

    print("[✅] Toutes les variables d’environnement sont définies et valides.")

