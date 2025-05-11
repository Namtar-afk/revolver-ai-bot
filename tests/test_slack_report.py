# tests/test_slack_report.py
import pytest
from types import SimpleNamespace
from bot.slack_handler import handle_report_command

class DummyClient:
    def __init__(self):
        self.uploaded = False
        self.messages = []

    def files_upload(self, **kwargs):
        # Simule l’upload et vérifie qu’on génère bien un .pptx
        assert kwargs.get("filename", "").endswith(".pptx")
        self.uploaded = True
        return {"ok": True}

    def chat_postMessage(self, **kwargs):
        # Slack Bolt respond() utilise client.chat_postMessage en interne
        text = kwargs.get("text", "")
        self.messages.append(text)

@pytest.fixture(autouse=True)
def patch_slack(monkeypatch):
    dummy = DummyClient()
    # Patch du client utilisé dans bot/slack_handler.py
    monkeypatch.setattr("bot.slack_handler.client.files_upload", dummy.files_upload)
    monkeypatch.setattr("bot.slack_handler.client.chat_postMessage", dummy.chat_postMessage)
    return dummy

def test_slack_report(patch_slack):
    # Préparez un ack() qui note qu'il a été appelé
    ack_called = {"ok": False}
    def ack(response=None):
        ack_called["ok"] = True

    # prepare a dummy respond()—nous n’en avons pas besoin ici
    def respond(msg):
        # handle_report_command renvoie un texte via return, pas via respond()
        pass

    # Simulez la commande Slash /report sans arguments
    command = SimpleNamespace(text="", channel_id="C123", user_id="U123")

    # Exécutez
    result = handle_report_command(ack, respond, command)

    # La commande doit avoir été ackée
    assert ack_called["ok"], "La commande Slack n’a pas été ackée"

    # Un .pptx doit avoir été uploadé au moins une fois
    assert patch_slack.uploaded, "Le PPT n’a pas été uploadé sur Slack"

    # Et un message de confirmation doit avoir été renvoyé (via client.chat_postMessage)
    assert any(
        "rapport généré" in msg.lower() or "report" in msg.lower()
        for msg in patch_slack.messages
    ), "Pas de message de confirmation dans chat_postMessage"
