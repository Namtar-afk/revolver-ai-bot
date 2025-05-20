import os
import hmac
import hashlib
import json
from typing import Any, Optional
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from bot.slack_handler import handle_slack_event

# ------------------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------------------
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET", "")
app = FastAPI(title="Revolver AI Slack Server")

# ------------------------------------------------------------------------------
# Modèles Pydantic
# ------------------------------------------------------------------------------
class SlackEvent(BaseModel):
    """
    Modèle du payload Slack.
    """
    type: str
    challenge: Optional[str] = Field(None, description="Challenge pour la vérification d’URL")
    event: Optional[dict[str, Any]] = Field(None, description="Détails de l’événement Slack")

# ------------------------------------------------------------------------------
# Sécurité
# ------------------------------------------------------------------------------
def verify_signature(request: Request, body: bytes) -> None:
    """
    Vérifie la signature Slack pour garantir l’intégrité de la requête.
    """
    timestamp = request.headers.get("X-Slack-Request-Timestamp")
    slack_signature = request.headers.get("X-Slack-Signature")
    if not timestamp or not slack_signature:
        raise HTTPException(400, "Missing Slack verification headers")
    # Construit la base string et calcule le HMAC SHA256
    base = f"v0:{timestamp}:{body.decode('utf-8')}"
    computed_signature = "v0=" + hmac.new(
        SLACK_SIGNING_SECRET.encode(),
        base.encode(),
        hashlib.sha256
    ).hexdigest()
    if not hmac.compare_digest(computed_signature, slack_signature):
        raise HTTPException(403, "Invalid Slack signature")

# ------------------------------------------------------------------------------
# Routes
# ------------------------------------------------------------------------------
@app.post("/slack/events")
async def slack_events(request: Request):
    """
    Webhook d’événements Slack :
    - Vérification d’URL (challenge)
    - Dispatch des événements (appels à handle_slack_event)
    """
    body = await request.body()
    verify_signature(request, body)
    payload = await request.json()
    evt = SlackEvent(**payload)
    # Réponse au challenge de vérification d’URL
    if evt.type == "url_verification" and evt.challenge:
        return JSONResponse({"challenge": evt.challenge})
    # Dispatch de l’événement
    if evt.event:
        try:
            await handle_slack_event(evt.event)
        except Exception as e:
            raise HTTPException(500, f"Event handling failed: {e}")
        return JSONResponse({"ok": True})
    return JSONResponse({"ok": True})

@app.get("/")
def root() -> dict[str, str]:
    """
    Point de contrôle basique pour vérifier le statut du serveur.
    """
    return {"status": "Slack server is running."}