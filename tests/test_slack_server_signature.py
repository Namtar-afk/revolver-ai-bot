import hashlib
import hmac
import json
import os
import time

import pytest
from fastapi.testclient import TestClient

# Force the signing secret for tests
os.environ["SLACK_SIGNING_SECRET"] = "test_secret"

from api.slack_server import app


@pytest.fixture
def client():
    return TestClient(app)


def make_signature(secret: str, timestamp: str, body: bytes) -> str:
    basestring = f"v0:{timestamp}:{body.decode()}"
    digest = hmac.new(secret.encode(), basestring.encode(), hashlib.sha256).hexdigest()
    return f"v0={digest}"


def test_missing_headers(client):
    r = client.post("/slack/events", data=b"{}")
    assert r.status_code == 400
    assert "Missing Slack verification headers" in r.text


def test_invalid_signature(client):
    ts = str(int(time.time()))
    headers = {
        "X-Slack-Request-Timestamp": ts,
        "X-Slack-Signature": "v0=bad",
    }
    r = client.post("/slack/events", data=b"{}", headers=headers)
    assert r.status_code == 403
    assert "Invalid Slack signature" in r.text


def test_challenge(client):
    ts = str(int(time.time()))
    payload = {"type": "url_verification", "challenge": "foo"}
    body = json.dumps(payload).encode()
    sig = make_signature(os.environ["SLACK_SIGNING_SECRET"], ts, body)
    headers = {
        "X-Slack-Request-Timestamp": ts,
        "X-Slack-Signature": sig,
        "Content-Type": "application/json",
    }
    r = client.post("/slack/events", data=body, headers=headers)
    assert r.status_code == 200
    assert r.json() == {"challenge": "foo"}


@pytest.mark.anyio(backend="asyncio")
async def test_event_dispatch(monkeypatch, client):
    called = {}

    async def fake_handler(payload):
        called["payload"] = payload

    monkeypatch.setattr(
        "bot.slack_handler.handle_slack_event", fake_handler, raising=True
    )

    ts = str(int(time.time()))
    ev = {"type": "event_callback", "event": {"text": "hey"}}
    body = json.dumps(ev).encode()
    sig = make_signature(os.environ["SLACK_SIGNING_SECRET"], ts, body)
    headers = {
        "X-Slack-Request-Timestamp": ts,
        "X-Slack-Signature": sig,
        "Content-Type": "application/json",
    }
    r = client.post("/slack/events", data=body, headers=headers)
    assert r.status_code == 200
    assert r.json() == {"ok": True}
    assert called["payload"] == {"event": {"text": "hey"}}
