import hashlib
import hmac
import json
import os
import time
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def slack_signature(secret, body, timestamp=None):
    if timestamp is None:
        timestamp = str(int(time.time()))
    basestring = f"v0:{timestamp}:{body}"
    my_sig = (
        "v0="
        + hmac.new(secret.encode(), basestring.encode(), hashlib.sha256).hexdigest()
    )
    return my_sig, timestamp


@pytest.fixture
def mock_handle_event(monkeypatch):
    mock = AsyncMock()
    monkeypatch.setattr("api.slack_routes.handle_event", mock)
    return mock


def test_slack_events_file_and_message(mock_handle_event):
    """Test de réception Slack avec message + fichier PDF"""
    payload = {
        "token": "test-token",
        "team_id": "T123",
        "api_app_id": "A123",
        "event": {
            "type": "message",
            "text": "Hello bot!",
            "files": [
                {
                    "filetype": "pdf",
                    "url_private_download": "https://example.com/fake.pdf",
                }
            ],
        },
        "type": "event_callback",
        "event_id": "Ev123",
        "event_time": 1234567890,
    }
    body = json.dumps(payload)
    secret = os.environ.get("SLACK_SIGNING_SECRET", "test")
    sig, ts = slack_signature(secret, body)
    response = client.post(
        "/slack/events",
        data=body,
        headers={
            "Content-Type": "application/json",
            "X-Slack-Signature": sig,
            "X-Slack-Request-Timestamp": ts,
        },
    )
    assert response.status_code == 200
    mock_handle_event.assert_called_once()


def test_slack_events_url_verification():
    """Test du challenge Slack (URL Verification)"""
    payload = {
        "token": "test-token",
        "challenge": "test_challenge",
        "type": "url_verification",
    }
    response = client.post(
        "/slack/events",
        json=payload,
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 200
    assert response.json() == {"challenge": "test_challenge"}


def test_slack_events_message(mock_handle_event):
    """Test d’un simple message texte Slack"""
    payload = {
        "token": "test-token",
        "team_id": "T123",
        "api_app_id": "A123",
        "event": {"type": "message", "text": "Hello bot!"},
        "type": "event_callback",
        "event_id": "Ev123",
        "event_time": 1234567890,
    }
    body = json.dumps(payload)
    secret = os.environ.get("SLACK_SIGNING_SECRET", "test")
    sig, ts = slack_signature(secret, body)
    response = client.post(
        "/slack/events",
        data=body,
        headers={
            "Content-Type": "application/json",
            "X-Slack-Signature": sig,
            "X-Slack-Request-Timestamp": ts,
        },
    )
    assert response.status_code == 200
    mock_handle_event.assert_called_once()
