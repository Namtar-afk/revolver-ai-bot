from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from parser.pdf_parser import extract_text_from_pdf
from parser.nlp_utils import extract_brief_sections

app = FastAPI(title="Revolver AI Bot - Brief Extractor")

@app.post("/extract-brief")
async def extract_brief(file: UploadFile = File(...)):
    contents = await file.read()

    with open("temp_brief_api.pdf", "wb") as f:
        f.write(contents)

    text = extract_text_from_pdf("temp_brief_api.pdf")
    if not text:
        return JSONResponse(status_code=400, content={"error": "PDF illisible"})

    try:
        data = extract_brief_sections(text)
        return JSONResponse(content=data)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

