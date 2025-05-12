from fastapi import FastAPI
from reco.generator import generate_recommendation
from reco.models import BriefReminder, TrendItem

app = FastAPI()

@app.post("/recommendation")
def get_recommendation(brief: BriefReminder, trends: list[TrendItem]):
    return generate_recommendation(brief, trends)
