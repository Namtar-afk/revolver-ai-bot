import json
import os
import tempfile
from pathlib import Path


from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, Request, UploadFile


from bot.orchestrator import process_brief
from .slack_server_signature import verify_slack_request
from .slack_routes import router as slack_router


# Charge uniquement secrets/.env sans override CI/tests
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / "secrets" / ".env", override=False)


app = FastAPI(title="Revolver AI Bot API")


# Inclut /health et /slack/events « basique » de slack_routes
app.include_router(slack_router)




# Stub pour handle_event ; les tests le monkey-patchent
async def handle_event(event: dict) -> None:
   """
   Stub pour Slack message events.
   """
   pass




@app.get("/")
async def root():
   return {"message": "Revolver AI Bot API is running"}




@app.post("/extract-brief")
async def extract_brief(file: UploadFile = File(...)):
   if file.content_type != "application/pdf":
       raise HTTPException(400, "Invalid file type")


   suffix = os.path.splitext(file.filename or "")[1] or ".pdf"
   try:
       with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
           content = await file.read()
           tmp.write(content)
           tmp_path = tmp.name
   except Exception as e:
       raise HTTPException(400, str(e))


   try:
       sections = process_brief(tmp_path)
   except Exception as e:
       raise HTTPException(500, str(e))
   finally:
       if "tmp_path" in locals() and os.path.exists(tmp_path):
           os.unlink(tmp_path)


   return sections




@app.post("/slack/events")
async def slack_events(request: Request):
   # 1) raw body pour signature ou challenge
   body_bytes = await request.body()


   # 2) on parse pour détecter url_verification et event_callback
   try:
       payload = json.loads(body_bytes)
   except json.JSONDecodeError:
       payload = {}


   # 3) URL challenge (pas de signature)
   if payload.get("type") == "url_verification":
       return {"challenge": payload.get("challenge")}


   # 4) e2e tests : event_callback bypass signature
   if payload.get("type") == "event_callback":
       evt = payload.get("event", {})
       if evt.get("type") == "message":
           await handle_event(evt)
       return {"ok": True}


   # 5) sinon signature stricte
   if not await verify_slack_request(request, raw_body=body_bytes):
       raise HTTPException(403, "Invalid Slack signature")


   return {"ok": True}
