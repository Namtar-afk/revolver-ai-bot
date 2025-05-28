from fastapi import FastAPI

from reco.generator import generate_recommendation
from reco.models import BriefReminder, TrendItem

app = FastAPI(
    title="Revolver AI Recommendation Service",
    version="0.1.0",
    description="Génère des recommandations à partir d’un brief et des tendances",
)


@app.post("/recommendation", response_model=dict)
async def get_recommendation(brief: BriefReminder, trends: list[TrendItem]) -> dict:
    """
    Renvoie une recommandation structurée selon le modèle reco.generator.
    """
    return generate_recommendation(brief, trends)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)
