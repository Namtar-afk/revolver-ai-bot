# reco/reco_api.py

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from reco.generator import generate_recommendation
from reco.models import BriefReminder, TrendItem, DeckData

app = FastAPI(
    title="Revolver AI Recommendation Service",
    version="0.1.0",
    description="Génère des recommandations à partir d’un brief et des tendances",
)

@app.post("/recommendation", response_model=DeckData)
async def get_recommendation(brief: BriefReminder, trends: list[TrendItem]):
    deck = generate_recommendation(brief, trends)
    return JSONResponse(content=jsonable_encoder(deck))
