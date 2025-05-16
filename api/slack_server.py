# api/slack_server.py
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import hmac
import hashlib
import os
from fastapi import FastAPI
app = FastAPI()

@app.get("/")
def healthcheck():
    return {"status": "Slack server is running."}

SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET", "your-signing-secret")

class SlackEvent(BaseModel):
    type: str
    challenge: str = None
    event: dict = None


def verify_signature(request: Request, body: bytes):
    timestamp = request.headers.get("X-Slack-Request-Timestamp")
    signature = request.headers.get("X-Slack-Signature")
    
    if not timestamp or not signature:
        raise HTTPException(status_code=400, detail="Missing Slack headers")

    sig_basestring = f"v0:{timestamp}:{body.decode()}"
    my_signature = "v0=" + hmac.new(
        SLACK_SIGNING_SECRET.encode(),
        sig_basestring.encode(),
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(my_signature, signature):
        raise HTTPException(status_code=403, detail="Invalid request signature")


@app.post("/slack/events")
async def slack_events(request: Request):
    raw_body = await request.body()
    verify_signature(request, raw_body)

    payload = await request.json()
    slack_event = SlackEvent(**payload)

    # Ping init
    if slack_event.type == "url_verification":
        return JSONResponse(content={"challenge": slack_event.challenge})

    # Handle events
    if slack_event.event:
        await handle_slack_event(slack_event.event)
        return JSONResponse(content={"ok": True})

    return JSONResponse(content={"ok": True})


@app.get("/")
def root():
    return {"status": "Slack server is running."}
