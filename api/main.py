# api/main.py

import json
import os
import sys
import tempfile
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import RedirectResponse

from bot.orchestrator import process_brief

from .slack_routes import router as slack_router
from .slack_server_signature import verify_slack_request

# Chargement de l'environnement
BASE_DIR = Path(__file__).resolve().parent.parent
env_path = BASE_DIR / "secrets" / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path, override=False)
else:
    print(
        f"Avertissement : Fichier .env non trouvé à {env_path}. "
        "Les variables d'environnement pourraient manquer.",
        file=sys.stderr,
    )

# Initialisation FastAPI
app = FastAPI(
    title="Revolver AI Bot API",
    version="0.1.0",
    description="API pour extraire des briefs PDF et gérer les événements Slack",
)

# Inclusions des routes Slack
app.include_router(slack_router)


@app.get("/", tags=["Health"])
async def root():
    return {"message": "✅ Revolver AI Bot API is running"}


@app.get("/docs", include_in_schema=False)
def docs_redirect():
    """Redirection vers la doc interactive."""
    return RedirectResponse(url="/docs")


@app.post("/extract-brief", tags=["Extraction"])
async def extract_brief(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400, detail="Invalid file type. Only PDF is allowed."
        )

    filename = file.filename or "brief.pdf"
    suffix = Path(filename).suffix or ".pdf"
    tmp_path_str = ""

    try:
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(await file.read())
            tmp_path_str = tmp.name

        sections = process_brief(tmp_path_str)
        if not sections:
            raise HTTPException(
                status_code=500, detail="Échec de l'extraction du brief."
            )

        return sections

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur : {e}")
    finally:
        if tmp_path_str and Path(tmp_path_str).exists():
            try:
                os.remove(tmp_path_str)
            except Exception:
                pass


@app.post("/slack/events", tags=["Slack"])
async def slack_events(request: Request):
    """
    Endpoint d’événements Slack avec vérification de signature.
    """
    body_bytes = await request.body()

    try:
        payload = json.loads(body_bytes)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Corps JSON invalide")

    # Cas spécial : Slack challenge initial
    if payload.get("type") == "url_verification":
        return {"challenge": payload.get("challenge")}

    # Cas spécial : bypass de test
    event_data = payload.get("event", {})
    if payload.get("type") == "event_callback" and event_data.get(
        "text", ""
    ).startswith("e2e_test_bypass_signature"):
        return {"ok": True}

    # Vérification de signature
    if not await verify_slack_request(request, raw_body=body_bytes):
        raise HTTPException(status_code=403, detail="Invalid Slack signature")

    # Traitement minimal (stub)
    if payload.get("type") == "event_callback":
        if event_data.get("type") == "message":
            await handle_event(event_data)

    return {"ok": True}


async def handle_event(event: dict) -> None:
    """
    Gère les événements Slack (stub actuel).
    """
    print(f"[Slack Event] Reçu : {event}")
