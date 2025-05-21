# api/slack_server.py
import hashlib
import hmac
import json
import os
import time
from typing import Any, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

import bot.slack_handler

SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET", "")

app = FastAPI(title="Revolver AI Slack Server")


class SlackEvent(BaseModel):
    type: str
    challenge: Optional[str] = Field(
        None, description="Challenge pour la vérification d’URL"
    )
    event: Optional[dict[str, Any]] = Field(
        None, description="Détails de l’événement Slack"
    )


def verify_signature(request: Request, body: bytes) -> None:
    timestamp = request.headers.get("X-Slack-Request-Timestamp")
    slack_signature = request.headers.get("X-Slack-Signature")
    if not timestamp or not slack_signature:
        raise HTTPException(400, "Missing Slack verification headers")
    # Prevent replay attacks (5 minutes window)
    if abs(time.time() - int(timestamp)) > 60 * 5:
        raise HTTPException(400, "Stale request")
    basestring = f"v0:{timestamp}:{body.decode('utf-8')}"
    computed = (
        "v0="
        + hmac.new(
            SLACK_SIGNING_SECRET.encode(), basestring.encode(), hashlib.sha256
        ).hexdigest()
    )
    if not hmac.compare_digest(computed, slack_signature):
        raise HTTPException(403, "Invalid Slack signature")


@app.post("/slack/events")
async def slack_events(request: Request):
    body = await request.body()
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        raise HTTPException(400, "Invalid JSON payload")

    # URL verification challenge: no signature required
    if data.get("type") == "url_verification" and data.get("challenge"):
        return JSONResponse({"challenge": data["challenge"]})

    # All other requests must be signed
    verify_signature(request, body)

    # Validate shape
    evt = SlackEvent(**data)

    # Dispatch actual event callbacks
    if evt.event:
        try:
            # Use full module path so monkeypatch works
            await bot.slack_handler.handle_slack_event({"event": evt.event})
        except Exception as e:
            raise HTTPException(500, f"Event handling failed: {e}")
        return JSONResponse({"ok": True})

    return JSONResponse({"ok": True})


@app.get("/")
def root() -> dict[str, str]:
    return {"status": "Slack server is running."}
