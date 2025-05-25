# tests/test_handle_slack_event_upload.py
import os

import aiohttp
import pytest

from bot.slack_handler import handle_slack_event


class DummyResp:
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def read(self):
        return b"%PDF-1.4\n..."


class DummySession:
    def __init__(self, *args, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass

    # rendre get synchrone pour que "async with session.get(...)" fonctionne
    def get(self, url, headers):
        return DummyResp()


@pytest.mark.anyio
async def test_handle_slack_event_pdf(monkeypatch, tmp_path):
    # Event simulant l'envoi d'un PDF
    fake_event = {
        "event": {
            "files": [
                {
                    "filetype": "pdf",
                    "url_private_download": "http://example.com/fake.pdf",
                }
            ]
        }
    }

    # Prépare la variable d'env pour l'auth
    monkeypatch.setenv("SLACK_BOT_TOKEN", "xoxb-test-token")

    # Stubbe ClientSession pour retourner notre DummySession
    monkeypatch.setattr(
        "bot.slack_handler.aiohttp.ClientSession",
        lambda *args, **kwargs: DummySession(),
    )

    # Stubbe process_brief pour renvoyer un résultat connu
    monkeypatch.setattr("bot.slack_handler.process_brief", lambda path: {"foo": "bar"})

    res = await handle_slack_event(fake_event)

    # On doit recevoir le texte de succès incluant notre dict stubbé
    assert "✅ Brief analysé" in res["text"]
    assert "{'foo': 'bar'}" in res["text"]
