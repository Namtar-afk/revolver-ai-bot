import pytest
import json
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_slack_events_file_and_message():
    mock_handle_event = MagicMock()
    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setattr("api.main.handle_event", mock_handle_event)
        # Construire un événement Slack simulé
        payload = {
            "token": "test-token",
            "team_id": "T123",
            "api_app_id": "A123",
            "event": {
                "type": "message",
                "text": "Hello bot!",
                "files": [
                    {"filetype": "pdf", "url_private_download": "https://example.com/fake.pdf"}
                ]
            },
            "type": "event_callback",
            "event_id": "Ev123",
            "event_time": 1234567890
        }
        response = client.post(
            "/slack/events",
            data=json.dumps(payload),
            headers={
                "Content-Type": "application/json",
                "X-Slack-Signature": "v0=invalid",  # vous pouvez mocker la validation si besoin
                "X-Slack-Request-Timestamp": "1234567890"
            }
        )
        assert response.status_code == 200
        # Vérifier que notre handler a bien été appelé
        mock_handle_event.assert_called_once()

def test_slack_events_url_verification():
    payload = {
        "token": "test-token",
        "challenge": "test_challenge",
        "type": "url_verification"
    }
    response = client.post(
        "/slack/events",
        data=json.dumps(payload),
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 200
    assert response.json() == {"challenge": "test_challenge"}

def test_slack_events_message():
    mock_handle_event = MagicMock()
    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setattr("api.main.handle_event", mock_handle_event)
        payload = {
            "token": "test-token",
            "team_id": "T123",
            "api_app_id": "A123",
            "event": {
                "type": "message",
                "text": "Hello bot!"
            },
            "type": "event_callback",
            "event_id": "Ev123",
            "event_time": 1234567890
        }
        response = client.post(
            "/slack/events",
            data=json.dumps(payload),
            headers={
                "Content-Type": "application/json",
                "X-Slack-Signature": "v0=invalid",
                "X-Slack-Request-Timestamp": "1234567890"
            }
        )
        assert response.status_code == 200
        mock_handle_event.assert_called_once()