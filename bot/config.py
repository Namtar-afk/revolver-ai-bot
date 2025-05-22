import os
from pathlib import Path

from dotenv import load_dotenv

# Charge le .env situé dans le dossier secrets
env_path = Path(__file__).parent.parent / "secrets" / ".env"
load_dotenv(dotenv_path=env_path, override=False)


class Settings:
    SLACK_BOT_TOKEN: str = os.getenv("SLACK_BOT_TOKEN", "")
    SLACK_SIGNING_SECRET: str = os.getenv("SLACK_SIGNING_SECRET", "")
    GMAIL_USER: str = os.getenv("GMAIL_USER", "")
    GMAIL_APP_PASSWORD: str = os.getenv("GMAIL_APP_PASSWORD", "")
    SERPAPI_API_KEY: str = os.getenv("SERPAPI_API_KEY", "")
    GOOGLE_SHEET_ID: str = os.getenv("GOOGLE_SHEET_ID", "")


settings = Settings()
