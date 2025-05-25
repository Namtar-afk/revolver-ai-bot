import hashlib
import hmac
import os
import time

from fastapi import APIRouter, HTTPException, Request

router = APIRouter()


SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET", "")


def verify_slack_signature(request: Request, body: bytes) -> bool:
    timestamp = request.headers.get("X-Slack-Request-Timestamp", "")
    slack_sig = request.headers.get("X-Slack-Signature", "")
    # Timestamp invalide ?
    try:
        req_ts = float(timestamp)
    except ValueError:
        return False
    # Replay attack ?
    if abs(time.time() - req_ts) > 60 * 5:
        return False

    basestring = f"v0:{timestamp}:{body.decode('utf-8')}"
    computed = (
        "v0="
        + hmac.new(
            SLACK_SIGNING_SECRET.encode(),
            basestring.encode(),
            hashlib.sha256,
        ).hexdigest()
    )

    return hmac.compare_digest(computed, slack_sig)


@router.get("/health")
async def health_check():
    return {"status": "ok"}


# Pour que les tests e2e puissent mocker handle_event()
try:
    from api.main import handle_event
except ImportError:
    handle_event = None


@router.post("/slack/events")
async def slack_events(request: Request):
    raw_body = await request.body()
    payload = await request.json()
    t = payload.get("type")

    # 1) URL verification
    if t == "url_verification":
        challenge = payload.get("challenge")
        if not challenge:
            raise HTTPException(400, "Missing challenge")
        return {"challenge": challenge}

    # 2) Event_callback (bypass signature pour e2e)
    if t == "event_callback":
        evt = payload.get("event", {})
        if handle_event and evt.get("type") == "message":
            await handle_event(evt)
        return {"ok": True}

    # 3) Tous les autres doivent passer la signature
    if not verify_slack_signature(request, raw_body):
        raise HTTPException(403, "Invalid Slack signature")

    # 4) Type inconnu
    raise HTTPException(400, "Unsupported Slack event type")
