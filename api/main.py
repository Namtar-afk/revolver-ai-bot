from fastapi import FastAPI
from pydantic import BaseModel
from reco.generator import generate_recommendation
from reco.models import BriefReminder, TrendItem, DeckData

app = FastAPI(title="Revolver AI Bot API", version="0.2.0")


class RecommendationRequest(BaseModel):
    brief: BriefReminder
    trends: list[TrendItem]


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API Revolver AI Bot"}


@app.post("/brief", response_model=DeckData)
def post_brief(data: RecommendationRequest):
    return generate_recommendation(data.brief, data.trends)


@app.post("/generate", response_model=DeckData)
def generate_deck(data: RecommendationRequest):
    return generate_recommendation(data.brief, data.trends)


@app.post("/report")
def generate_report(data: RecommendationRequest):
    import tempfile
    from pptx_generator.slide_builder import build_ppt

    deck = generate_recommendation(data.brief, data.trends)
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pptx")
    build_ppt(deck, tmp_file.name)
    return {"pptx_path": tmp_file.name}
