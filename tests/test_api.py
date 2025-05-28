import os
import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_extract_brief_success():
    pdf_path = "tests/samples/brief_sample.pdf"
    assert os.path.exists(pdf_path), "Fichier PDF de test manquant"
    with open(pdf_path, "rb") as f:
        files_data = {"file": ("brief_sample.pdf", f, "application/pdf")}
        response = client.post("/extract-brief", files=files_data)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "titre" in data

def test_extract_brief_failure():
    files_data = {"file": ("empty.txt", b"", "text/plain")}
    response = client.post("/extract-brief", files=files_data)
    assert response.status_code == 400
    # L'assertion doit être ici, à l'intérieur de la fonction :
    assert response.json()["detail"] == "Invalid file type. Only PDF is allowed."

def test_extract_brief_internal_error(monkeypatch: pytest.MonkeyPatch):
    def mock_process_brief_error(file_path: str):
        raise ValueError("Simulated internal processing error")
    monkeypatch.setattr("api.main.process_brief", mock_process_brief_error)
    files_data = {
        "file": (
            "brief_sample.pdf",
            b"dummy pdf content",
            "application/pdf",
        )
    }
    response = client.post("/extract-brief", files=files_data)
    assert response.status_code == 500
    assert "Simulated internal processing error" in response.json()["detail"]