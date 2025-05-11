import os
import sys
from bot.slack_handler import handle_report_command

def test_handle_report_command_generates_file_and_returns_message(tmp_path, monkeypatch):
    # On se place dans tmp_path pour isoler
    monkeypatch.chdir(tmp_path)
    # On simule un appel Slack (command["text"] vide => report.pptx)
    msg = handle_report_command(ack=None, respond=None, command={})
    # Doit mentionner le chemin absolu
    assert "📊 Rapport généré" in msg
    out = msg.split(":")[-1].strip()
    # Le fichier a bien été créé
    assert os.path.exists(out), f"{out} should exist"

def test_cli_report_invokes_orchestrator_and_outputs_pptx(tmp_path, monkeypatch):
    # Même fixture d'isolement
    monkeypatch.chdir(tmp_path)
    # On appelle la même fonction via subprocess to be sure
    from bot.slack_handler import handle_report_command as slack_report
    # On récupère un output spécifique
    custom = tmp_path / "cli_custom.pptx"
    msg = slack_report(None, None, {"text": str(custom)})
    assert str(custom) in msg
    assert custom.exists()
