import os
import sys
import tempfile
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import RedirectResponse

from bot.orchestrator import process_brief
from api.slack_routes import router as slack_router


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

app = FastAPI(
    title="Revolver AI Bot API",
    version="0.1.0",
    description="API pour extraire des briefs PDF et gérer les événements Slack",
)

app.include_router(slack_router)


@app.get("/", tags=["Health"])
async def root():
    return {"message": "✅ Revolver AI Bot API is running"}


@app.get("/docs", include_in_schema=False)
async def docs_redirect():
    return RedirectResponse(url="/docs")


@app.post("/extract-brief", tags=["Extraction"])
async def extract_brief(file: UploadFile = File(...)):  # noqa: B008
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
        detail_msg = f"Erreur lors du traitement du brief: {str(e)}"
        raise HTTPException(status_code=500, detail=detail_msg)
    finally:
        if tmp_path_str and Path(tmp_path_str).exists():
            try:
                os.remove(tmp_path_str)
            except Exception:
                pass
