import os

from dotenv import load_dotenv

# charge explicitement le .env à la racine du projet
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

SLACK_TOKEN = os.environ.get("SLACK_TOKEN")
GMAIL_API_CREDENTIALS = os.environ.get("GMAIL_API_CREDENTIALS")
GSPREADSHEET_ID = os.environ.get("GSPREADSHEET_ID")
SERPAPI_KEY = os.environ.get("SERPAPI_KEY")
