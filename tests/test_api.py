import os
import pytest
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
    assert isinstance(data, dict)  # Expecting a dictionary as a result
    # You might want to add more specific assertions about the content of the 'data' dictionary
    # based on what process_brief is expected to return. For example:
    # assert "title" in data
    # assert "sections" in data

def test_extract_brief_failure():
    # simulate upload of an invalid file
    response = client.post("/extract-brief", files={"file": ("empty.txt", b"", "text/plain")})
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid file type"

def test_extract_brief_internal_error():
    # Simulate a scenario where process_brief raises an exception
    with pytest.MonkeyPatch.context() as monkeypatch:
        def mock_process_brief(file_path: str):
            raise ValueError("Simulated processing error")
        monkeypatch.setattr("api.main.process_brief", mock_process_brief)
        response = client.post("/extract-brief", files={"file": ("brief_sample.pdf", b"dummy content", "application/pdf")})
        assert response.status_code == 500
        assert "Simulated processing error" in response.json()["detail"]