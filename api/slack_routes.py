# api/slack_routes.py
from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter(prefix="/slack")

class URLVerification(BaseModel):
    token: str
    challenge: str
    type: str

@router.post("/events")
async def handle_event(req: Request):
    body = await req.json()
    if body.get("type") == "url_verification":
        return {"challenge": body["challenge"]}
    # here you can forward to your orchestrator or just ack:
    return {"ok": True}
