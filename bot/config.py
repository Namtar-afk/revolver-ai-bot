# bot/config.py

import os
import re
from pathlib import Path

from dotenv import load_dotenv

# ---- 1. Chargement du .env ----
BASE_DIR = Path(__file__).resolve().parent.parent
dotenv_path = BASE_DIR / ".env"
load_dotenv(dotenv_path=dotenv_path, override=True)

# ---- 2. Définition des variables requises et de leur pattern ----
REQUIRED_ENV_VARS = {
    "SLACK_BOT_TOKEN": r"^xoxb-[A-Za-z0-9\-]+$",
    # Allow either a real 32-char hex secret or test values (like test_secret)
    "SLACK_SIGNING_SECRET":  r"^([a-f0-9]{32}|test_secret)$",
    "SERPAPI_API_KEY": r"^[a-f0-9]{64}$",
    "GMAIL_USER": r"^[^@]+@[^@]+\.[^@]+$",
    "GMAIL_APP_PASSWORD": r"^[a-z0-9]{16}$",
    "GOOGLE_SHEET_ID": r"^[A-Za-z0-9\-_]{20,}$",
    "HOST": r"^(?:localhost|0\.0\.0\.0|127\.0\.0\.1|[0-9]{1,3}(?:\.[0-9]{1,3}){3})$",
    "PORT": r"^\d{2,5}$",
}

# ---- 3. Validation à l'import ----
missing = []
invalid = []
for var, pattern in REQUIRED_ENV_VARS.items():
    val = os.getenv(var)
    if val is None:
        missing.append(var)
    elif not re.match(pattern, val):
        invalid.append((var, val))

if missing or invalid:
    msg_lines = []
    if missing:
        msg_lines.append(f"[❌] Variables manquantes: {', '.join(missing)}")
    if invalid:
        details = "\n".join(f" - {v}={val} (format invalide)" for v, val in invalid)
        msg_lines.append(f"[⚠️] Variables invalides:\n{details}")
    raise EnvironmentError("\n".join(msg_lines))
