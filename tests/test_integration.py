import os
import sys
import subprocess
import tempfile
import shutil
import pytest

from utils.logger import logger


def test_run_parser_cli():
    cmd = [sys.executable, "run_parser.py"]
    rc = subprocess.run(cmd, capture_output=True, text=True)
    assert rc.returncode == 0, rc.stderr
    assert "Validation JSON réussie" in rc.stdout


def test_slack_simulator(capsys):
    # appelle le simulateur Slack
    from bot.slack_handler import simulate_slack_upload
    simulate_slack_upload()
    out, _ = capsys.readouterr()
    assert "Sections extraites" in out or "Résultat structuré" in out


def test_email_handler(tmp_path, capsys):
    # prépare une inbox temporaire avec un PDF
    inbox_dir = tmp_path / "inbox"
    inbox_dir.mkdir()
    sample = "tests/samples/brief_sample.pdf"
    dest = inbox_dir / "brief1.pdf"
    shutil.copy(sample, dest)

    # on pointe notre stub vers ce dossier
    import bot.email_handler as eh
    eh.INBOX_DIR = str(inbox_dir)

    # exécute le handler
    eh.handle_inbox()

    out, _ = capsys.readouterr()
    # on doit voir les sections imprimées
    assert "-- PROBLEM --" in out.upper()
    assert "-- KPIS --" in out.upper()