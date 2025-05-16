from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from parser.pdf_parser import extract_text_from_pdf
from parser.nlp_utils import extract_brief_sections
import os

app = FastAPI(title="Revolver AI Bot - Brief Extractor", version="0.2.0")


@app.get("/")
async def root():
    return {"status": "Slack server is running."}


@app.post("/extract-brief")
async def extract_brief(file: UploadFile = File(...)):
    try:
        # Crée un chemin temporaire
        temp_path = "temp_brief_api.pdf"

        # Sauvegarde du fichier reçu
        contents = await file.read()
        with open(temp_path, "wb") as f:
            f.write(contents)

        # Extraction du texte
        text = extract_text_from_pdf(temp_path)
        if not text:
            return JSONResponse(status_code=400, content={"error": "PDF illisible"})

        # Traitement NLP
        data = extract_brief_sections(text)
        return JSONResponse(content=data)

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

    finally:
        # Nettoyage du fichier temporaire
        if os.path.exists(temp_path):
            os.remove(temp_path)

