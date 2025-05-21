from fastapi import APIRouter, HTTPException, Request

router = APIRouter()


@router.get("/health")
def health_check():
    """
    Health check endpoint returning service status.
    """
    return {"status": "ok"}


@router.post("/slack/events")
async def slack_events(request: Request):
    """
    Slack events endpoint. Handles URL verification and event callbacks.
    """
    body = await request.json()
    event_type = body.get("type")

    # Slack URL verification
    if event_type == "url_verification":
        challenge = body.get("challenge")
        if not challenge:
            raise HTTPException(status_code=400, detail="Missing challenge")
        return {"challenge": challenge}

    # Event callback: noop
    if event_type == "event_callback":
        # TODO: traiter les events si besoin
        return {"ok": True}

    # Unsupported type
    raise HTTPException(status_code=400, detail="Unsupported Slack event type")
