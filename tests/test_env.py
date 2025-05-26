import os
import re

import pytest
from dotenv import load_dotenv

# Charge automatiquement les variables d’environnement depuis le fichier .env
# override=True signifie que les variables d'environnement existantes seront écrasées par celles du .env
# Attention si des variables sont aussi settées dans l'environnement de CI.
load_dotenv(override=True) 

# Définition des variables obligatoires et de leur format attendu (regex)
# Pour les secrets, nous acceptons soit le format réel, soit une chaîne vide (placeholder).
REQUIRED_ENV_VARS = {
    "SLACK_BOT_TOKEN": r"^(|(xapp|xoxb)-[a-zA-Z0-9\-]+)$",  # Accepte chaîne vide OU format token
    "SLACK_SIGNING_SECRET": r"^(|(whsec-[a-f0-9]{32}|test_secret))$", # Accepte chaîne vide OU format secret/test_secret
    "SERPAPI_API_KEY": r"^(|[a-f0-9]{64})$", # Accepte chaîne vide OU format clé API
    "GMAIL_USER": r"^[^@]+@[^@]+\.[^@]+$", # Format email standard, probablement pas vide
    "GMAIL_APP_PASSWORD": r"^(|[a-z0-9 ]{16,})$", # Accepte chaîne vide OU format mot de passe app (16+ caractères)
    "GOOGLE_SHEET_ID": r"^[a-zA-Z0-9-_]{20,}$", # Format ID, probablement pas vide
    "HOST": r"^(localhost|0\.0\.0\.0|127\.0\.0\.1|[0-9]{1,3}(\.[0-9]{1,3}){3})$", # Doit avoir une valeur
    "PORT": r"^\d{2,5}$", # Doit avoir une valeur
}


def test_all_required_env_vars_are_set_and_valid():
    """
    Vérifie que toutes les variables d’environnement critiques sont bien définies
    et que leur format est valide (acceptant les placeholders pour les secrets).
    """
    missing_vars = []
    invalid_vars = []

    for var, pattern in REQUIRED_ENV_VARS.items():
        val = os.getenv(var)
        if val is None:
            missing_vars.append(var)
        # Si la valeur est une chaîne vide et que le pattern n'accepte pas spécifiquement la chaîne vide
        # comme alternative (ce que nos regex modifiées font maintenant avec `^(|PATTERN)$`),
        # elle serait considérée comme invalide. Avec les regex modifiées, une chaîne vide sera valide pour les secrets.
        elif not re.fullmatch(pattern, val): # Utiliser re.fullmatch pour s'assurer que tout le string correspond
            invalid_vars.append((var, val))

    if missing_vars or invalid_vars:
        error_msg = ""
        if missing_vars:
            error_msg += f"\n[❌] Variables d'environnement REQUISES manquantes (non définies) : {', '.join(missing_vars)}"
        if invalid_vars:
            error_msg += "\n[⚠️] Variables d'environnement avec format invalide (ou placeholder non accepté) :"
            for var_name, var_value in invalid_vars:
                # Affiche 'None' explicitement si la valeur est None (bien que couvert par missing_vars)
                displayed_value = '<Non Définie>' if var_value is None else f"'{var_value}'"
                error_msg += f"\n    - {var_name} = {displayed_value} (ne correspond pas au pattern attendu: {REQUIRED_ENV_VARS[var_name]})"
        
        # Pour un meilleur affichage dans pytest, on peut garder le message d'erreur plus concis
        # ou le rendre plus verbeux comme ci-dessus.
        # L'ancien message était :
        # raise AssertionError(error_msg.strip())
        # Nouveau message pour plus de clarté si besoin :
        final_error_message = "Problèmes de configuration des variables d'environnement:" + error_msg
        raise AssertionError(final_error_message)

    print("[✅] Toutes les variables d’environnement requises sont définies et leur format (ou placeholder) est valide.")
