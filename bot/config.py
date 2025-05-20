import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import ConfigDict

# charge explicitement le .env à la racine du projet
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

class Settings(BaseSettings):
    model_config: ConfigDict = ConfigDict(env_file=".env", env_file_encoding="utf-8")
    slack_token: str | None = os.environ.get("SLACK_TOKEN")
    gmail_api_credentials: str | None = os.environ.get("GMAIL_API_CREDENTIALS")
    gspreadsheet_id: str | None = os.environ.get("GSPREADSHEET_ID")
    serpapi_key: str | None = os.environ.get("SERPAPI_KEY")

settings = Settings()

SLACK_TOKEN = settings.slack_token
GMAIL_API_CREDENTIALS = settings.gmail_api_credentials
GSPREADSHEET_ID = settings.gspreadsheet_id
SERPAPI_KEY = settings.serpapi_key