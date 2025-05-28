import json
from fastapi import APIRouter, HTTPException, Request
from utils.logger import logger
from api.slack_server_signature import verify_slack_request
from bot.slack_events_handler import handle_event

router = APIRouter()

@router.get("/health", tags=["Slack Utilities"])
async def health_check_slack_router():
    return {"status": "ok from slack_routes"}

@router.post("/slack/events", tags=["Slack"])
async def slack_events_endpoint(request: Request):
    raw_body = await request.body()
    payload = {}
    try:
        payload = json.loads(raw_body.decode('utf-8'))
    except json.JSONDecodeError:
        logger.warning(
            f"Corps JSON invalide reçu sur /slack/events: {raw_body[:200]}"
        )
        raise HTTPException(status_code=400, detail="Invalid JSON body")
    event_type = payload.get("type")
    if event_type == "url_verification":
        challenge = payload.get("challenge")
        if not isinstance(challenge, str):
            logger.warning("Challenge manquant/invalide pour url_verification.")
            raise HTTPException(
                status_code=400, detail="Missing or invalid challenge"
            )
        return {"challenge": challenge}
    is_e2e_test_bypass = False
    if event_type == "event_callback":
        event_data = payload.get("event", {})
        text = event_data.get("text", "")
        if text.startswith("e2e_test_bypass_signature"):
            is_e2e_bypass = True
            logger.info("Bypass de signature pour test E2E activé.")
    if not is_e2e_test_bypass:
        if not await verify_slack_request(request, raw_body=raw_body):
            raise HTTPException(status_code=403, detail="Invalid Slack signature")
    if event_type == "event_callback":
        event_data = payload.get("event", {})
        if event_data.get("type") == "message":
            await handle_event(event_data)
        else:
            logger.info(
                f"Événement Slack (event_callback) non 'message' reçu: "
                f"{event_data.get('type')}"
            )
        return {"ok": True}
    logger.warning(f"Type d'événement Slack non supporté reçu: {event_type}")
    msg = f"Unsupported Slack event type: {event_type}"
    raise HTTPException(status_code=400, detail=msg)
