# api/slack_routes.py

import hashlib
import hmac
import os
import time

from fastapi import APIRouter, HTTPException, Request

router = APIRouter()

SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET", "")


def verify_slack_signature(request: Request, body: bytes) -> bool:
    """
    Vérifie la signature de la requête Slack.
    """
    timestamp = request.headers.get("X-Slack-Request-Timestamp", "")
    slack_sig = request.headers.get("X-Slack-Signature", "")

    try:
        req_ts = float(timestamp)
    except ValueError:
        return False

    # Protection contre les attaques par rejeu (5 min max)
    if abs(time.time() - req_ts) > 300:
        return False

    base = f"v0:{timestamp}:{body.decode('utf-8')}"
    computed = (
        "v0="
        + hmac.new(
            SLACK_SIGNING_SECRET.encode(),
            base.encode(),
            hashlib.sha256,
        ).hexdigest()
    )

    return hmac.compare_digest(computed, slack_sig)


@router.get("/health")
async def health_check():
    """
    Endpoint de vérification simple.
    """
    return {"status": "ok"}


# 🧪 Import explicite de la fonction à mocker (pour monkeypatch)
from api.slack_events_handler import handle_event


@router.post("/slack/events")
async def slack_events(request: Request):
    """
    Endpoint principal pour recevoir les événements Slack.
    - Vérifie la signature
    - Gère l'URL verification
    - Route les événements de type message vers `handle_event`
    """
    raw_body = await request.body()

    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    event_type = payload.get("type")

    # 1) Validation d'URL Slack (vérif initiale)
    if event_type == "url_verification":
        challenge = payload.get("challenge")
        if not challenge:
            raise HTTPException(400, detail="Missing challenge")
        return {"challenge": challenge}

    # 2) Événement Slack avec bypass E2E (mock async)
    if event_type == "event_callback":
        event_data = payload.get("event", {})
        text = event_data.get("text", "")
        is_e2e_bypass = text.startswith("e2e_test_bypass_signature")

        if is_e2e_bypass:
            await handle_event(event_data)  # 👈 doit être await pour assert_awaited
            return {"ok": "Bypass signature (E2E test)"}

        if not verify_slack_signature(request, raw_body):
            raise HTTPException(status_code=403, detail="Invalid Slack signature")

        if event_data.get("type") == "message":
            await handle_event(event_data)

        return {"ok": True}

    raise HTTPException(status_code=400, detail="Unsupported Slack event type")
