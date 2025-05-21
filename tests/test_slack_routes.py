import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.slack_routes import router


@pytest.fixture
def client():
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


def test_health_check_route_exists(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_slack_url_verification(client):
    payload = {"type": "url_verification", "challenge": "abc123"}
    response = client.post("/slack/events", json=payload)
    assert response.status_code == 200
    assert response.json() == {"challenge": "abc123"}


def test_slack_event_callback_noop(client):
    payload = {"type": "event_callback", "event": {"type": "message", "text": "hello"}}
    response = client.post("/slack/events", json=payload)
    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_slack_events_unsupported_type(client):
    payload = {"type": "something_else"}
    response = client.post("/slack/events", json=payload)
    assert response.status_code == 400
    assert "Unsupported Slack event type" in response.json()["detail"]
