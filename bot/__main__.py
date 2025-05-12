from fastapi import FastAPI
from reco.generator import generate_recommendation
from reco.models import BriefReminder, TrendItem

app = FastAPI()

@app.post("/recommendation")
def get_recommendation(brief: BriefReminder, trends: list[TrendItem]):
    return generate_recommendation(brief, trends)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("bot.__main__:app", host="127.0.0.1", port=8000, reload=True)
