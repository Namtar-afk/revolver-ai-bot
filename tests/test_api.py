import os
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_extract_brief_success():
    pdf_path = "tests/samples/brief_sample.pdf"
    assert os.path.exists(pdf_path), "Fichier PDF de test manquant"
    
    with open(pdf_path, "rb") as f:
        response = client.post("/extract-brief", files={"file": ("brief_sample.pdf", f, "application/pdf")})
    
    assert response.status_code == 200
    data = response.json()
    assert "title" in data
    assert "objectives" in data
    assert isinstance(data["objectives"], list)

def test_extract_brief_failure():
    # simulate upload of an invalid file
    response = client.post("/extract-brief", files={"file": ("empty.txt", b"", "text/plain")})
    assert response.status_code == 400 or response.status_code == 500

