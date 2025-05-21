# api/main.py

import hashlib
import hmac
import os
import time
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import ConfigDict
from pydantic_settings import BaseSettings

from bot.orchestrator import \
    process_brief  # veille, analyse, etc. restent dans bot/orchestrator


class Settings(BaseSettings):
    slack_app_token: str
    slack_signing_secret: str
    serpapi_api_key: str
    gmail_user: str
    gmail_app_password: str
    google_sheet_id: str
    env: str

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()

app = FastAPI(
    title="Revolver AI Bot API",
    version="0.1.0",
    description="API pour extraire des briefs PDF",
)


@app.get("/", tags=["Health"])
async def health_check() -> dict[str, str]:
    """Point de santé basique."""
    return {"status": "OK - API running"}


@app.post("/extract-brief", tags=["Extraction"])
async def extract_brief(file: UploadFile = File(...)) -> JSONResponse:
    """
    Upload d’un PDF de brief, extraction des sections et renvoi en JSON.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    try:
        tmp_dir = Path("/tmp")
        tmp_dir.mkdir(exist_ok=True)
        tmp_path = tmp_dir / file.filename
        content = await file.read()
        tmp_path.write_bytes(content)

        result = process_brief(str(tmp_path))
        return JSONResponse(content=result)

    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/slack/events", tags=["Slack"])
async def slack_events(request: Request) -> JSONResponse:
    """
    Endpoint pour Slack Events API.
    Vérifie la signature et gère la validation d’URL.
    """
    timestamp = request.headers.get("X-Slack-Request-Timestamp")
    signature = request.headers.get("X-Slack-Signature", "")
    body = await request.body()

    # Anti-replay (fenêtre de 5 min)
    if not timestamp or abs(int(timestamp) - int(time.time())) > 300:
        raise HTTPException(status_code=403, detail="Invalid or replayed timestamp")

    base = f"v0:{timestamp}:".encode() + body
    expected = (
        "v0="
        + hmac.new(
            settings.slack_signing_secret.encode(), base, hashlib.sha256
        ).hexdigest()
    )

    if not hmac.compare_digest(expected, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

    payload = await request.json()
    if payload.get("type") == "url_verification":
        return JSONResponse(content={"challenge": payload.get("challenge")})

    return JSONResponse(content={"ok": True})


@app.get("/docs", include_in_schema=False)
def docs_redirect():
    """Redirection vers la doc interactive."""
    return RedirectResponse(url="/docs")
