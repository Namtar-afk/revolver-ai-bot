# api/main.py

import json
import os
import tempfile
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, Request, UploadFile

from bot.orchestrator import process_brief

from .slack_server_signature import verify_slack_request

# Load .env (override any existing vars only if not already set)
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

app = FastAPI(title="Revolver AI Bot API")


# Stub for Slack event handling; tests can monkeypatch this
async def handle_event(event: dict) -> None:
    """
    Stub for handling Slack events; real logic lives elsewhere.
    """
    pass


@app.get("/")
async def root():
    return {"message": "Revolver AI Bot API is running"}


@app.post("/extract-brief")
async def extract_brief(file: UploadFile = File(...)):
    """
    Upload a PDF brief and return extracted sections as JSON.
    """
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type")

    suffix = os.path.splitext(file.filename)[1] if file.filename else ".pdf"
    try:
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        sections = process_brief(tmp_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if "tmp_path" in locals() and os.path.exists(tmp_path):
            os.unlink(tmp_path)

    return sections


@app.post("/slack/events")
async def slack_events(request: Request):
    # 1) Grab the exact raw body bytes
    body_bytes = await request.body()

    # 2) Parse JSON ourselves (for URL challenge)
    try:
        payload = json.loads(body_bytes)
    except json.JSONDecodeError:
        payload = {}

    # 3) Handle URL verification without signature check
    if payload.get("type") == "url_verification":
        return {"challenge": payload.get("challenge")}

    # 4) Verify signature (using the raw body)
    if not await verify_slack_request(request, raw_body=body_bytes):
        raise HTTPException(status_code=403, detail="Invalid Slack signature")

    # 5) Dispatch event callbacks
    if payload.get("type") == "event_callback":
        event = payload.get("event", {})
        if event.get("type") == "message":
            await handle_event(event)

    return {}
