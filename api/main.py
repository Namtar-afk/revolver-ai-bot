from fastapi import FastAPI, Request, UploadFile, File, HTTPException
import os
import tempfile
import json
from bot.orchestrator import process_brief

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Revolver AI Bot API is running"}

@app.post("/extract-brief")
async def extract_brief(file: UploadFile = File(...)):
    """
    Upload a PDF brief and return extracted sections as JSON.
    """
    # Validate file type
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type")
    # Save uploaded file to a temporary location
    suffix = os.path.splitext(file.filename)[1] if file.filename else ".pdf"
    try:
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    # Process the brief
    try:
        sections = process_brief(tmp_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'tmp_path' in locals() and os.path.exists(tmp_path):
            os.unlink(tmp_path)
    return sections

@app.post("/slack/events")
async def slack_events(request: Request):
    payload = await request.json()
    # Respond to Slack URL verification challenge
    if payload.get("type") == "url_verification":
        return {"challenge": payload.get("challenge")}
    # Event callback
    if payload.get("type") == "event_callback":
        event = payload.get("event", {})
        # Handle message events
        if event.get("type") == "message":
            handle_event(event)
        # Handle other event types if needed
    # Always return OK
    return {}

def handle_event(event: dict) -> None:
    """
    Handle a Slack event. This function is intended to be stubbed in tests.
    """
    # Implementation stubbed in tests
    pass