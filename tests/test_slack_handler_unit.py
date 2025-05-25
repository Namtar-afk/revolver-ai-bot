# tests/test_slack_handler_unit.py
import subprocess
import tempfile
from pathlib import Path

import aiohttp
import pytest
from slack_sdk import WebClient

from bot.slack_handler import (
    handle_report_command,
    run_report_subprocess,
    upload_to_slack,
)


class DummyCommand:
    text = "out.pptx"
    channel_id = "#foo"


@pytest.fixture
def fake_client(monkeypatch):
    calls = {}

    class FakeClient:
        def __init__(self):
            pass

        def files_upload(self, *, channels, file, filename):
            calls["upload"] = (channels, file, filename)

        def chat_postMessage(self, channel, text):
            calls["msg"] = (channel, text)

    monkeypatch.setenv("SLACK_BOT_TOKEN", "xoxb-xxx")
    return FakeClient(), calls


def test_run_report_subprocess_success(tmp_path, monkeypatch):
    script = tmp_path / "script.py"
    script.write_text("import sys; sys.exit(0)")
    # on force subprocess.run réel
    out = tmp_path / "out.pptx"
    run_report_subprocess(str(script), str(out))
    assert out.exists()


def test_run_report_subprocess_failure(tmp_path):
    script = tmp_path / "script.py"
    script.write_text("import sys; sys.exit(1)")
    out = tmp_path / "out.pptx"
    with pytest.raises(subprocess.CalledProcessError):
        run_report_subprocess(str(script), str(out))


def test_upload_to_slack(fake_client):
    client, calls = fake_client
    upload_to_slack(client, "#chan", "/tmp/foo.pptx", "foo.pptx")
    assert calls["upload"] == ("#chan", "/tmp/foo.pptx", "foo.pptx")
    assert calls["msg"][0] == "#chan"
    assert "📊 Rapport généré" in calls["msg"][1]


def test_handle_report_command_all_success(monkeypatch, fake_client):
    client, calls = fake_client
    monkeypatch.setattr("bot.slack_handler.client", client)
    # stub subprocess to pass
    monkeypatch.setattr(
        "bot.slack_handler.run_report_subprocess",
        lambda s, o: Path(o).write_bytes(b"x"),
    )
    cmd = DummyCommand()
    # ack/respond are no-ops
    res = handle_report_command(lambda: None, None, cmd)
    assert "📊 Rapport généré" in res
    assert calls["upload"][0] == cmd.channel_id


def test_handle_report_command_upload_fail(monkeypatch, fake_client):
    client, calls = fake_client
    monkeypatch.setattr("bot.slack_handler.client", client)
    # subprocess ok
    monkeypatch.setattr(
        "bot.slack_handler.run_report_subprocess",
        lambda s, o: Path(o).write_bytes(b"x"),
    )

    # make upload error
    def bad_upload(*args, **kwargs):
        raise Exception("boom")

    monkeypatch.setattr("bot.slack_handler.upload_to_slack", bad_upload)
    cmd = DummyCommand()
    res = handle_report_command(lambda: None, None, cmd)
    assert "❌ Échec de l’upload" in res
