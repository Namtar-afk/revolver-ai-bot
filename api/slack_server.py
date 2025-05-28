#!/usr/bin/env python3
import hashlib
import hmac
import json
import os
import time
from typing import Any, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

import bot.slack_handler  # import the module, not the function directly

# FastAPI app
app = FastAPI(title="Revolver AI Slack Server")

# Signing secret env var
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET", "")


class SlackEvent(BaseModel):
    """
    Pydantic model for incoming Slack payloads.
    """

    type: str
    challenge: Optional[str] = Field(None, description="URL verification challenge")
    event: Optional[dict[str, Any]] = Field(None, description="Event data payload")


def verify_signature(request: Request, body: bytes) -> None:
    """
    Verify Slack request signature and timestamp to prevent replay attacks.
    Raises HTTPException on failure.
    """
    timestamp = request.headers.get("X-Slack-Request-Timestamp")
    slack_sig = request.headers.get("X-Slack-Signature")
    if not timestamp or not slack_sig:
        raise HTTPException(
            status_code=400, detail="Missing Slack verification headers"
        )

    # Prevent replay: allow 5‐minute window
    if abs(time.time() - int(timestamp)) > 60 * 5:
        raise HTTPException(status_code=400, detail="Stale request timestamp")

    basestring = f"v0:{timestamp}:{body.decode('utf-8')}"
    computed = (
        "v0="
        + hmac.new(
            SLACK_SIGNING_SECRET.encode(),
            basestring.encode(),
            hashlib.sha256,
        ).hexdigest()
    )
    if not hmac.compare_digest(computed, slack_sig):
        raise HTTPException(status_code=403, detail="Invalid Slack signature")


@app.post("/slack/events")
async def slack_events(request: Request):
    """
    Webhook endpoint for Slack Events API.
     - Responds to URL verification challenges
     - Dispatches event callbacks (event_callback) without signature
     - Otherwise verifies signature, then dispatches
    """
    body = await request.body()
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    # URL verification: skip signature
    if data.get("type") == "url_verification" and data.get("challenge"):
        return JSONResponse({"challenge": data["challenge"]})

    # Event callback: skip signature and dispatch immediately
    if data.get("type") == "event_callback" and data.get("event"):
        payload = {"event": data["event"]}
        try:
            # reference the module attribute so monkeypatch works
            await bot.slack_handler.handle_slack_event(payload)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Event handling failed: {e}")
        return JSONResponse({"ok": True})

    # All other requests must be signed
    verify_signature(request, body)

    # Validate shape and (just in case) dispatch if present
    evt = SlackEvent(**data)
    if evt.event:
        try:
            await bot.slack_handler.handle_slack_event({"event": evt.event})
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Event handling failed: {e}")
    return JSONResponse({"ok": True})


@app.get("/")
def root() -> dict[str, str]:
    """
    Health check endpoint.
    """
    return {"status": "Slack server is running."}
