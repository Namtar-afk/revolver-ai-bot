import os
import sys
import subprocess
import shutil
import pytest

def test_run_parser_cli():
    cmd = [sys.executable, "run_parser.py"]
    rc = subprocess.run(cmd, capture_output=True, text=True)
    assert rc.returncode == 0, rc.stderr
    assert '"title": "Brief extrait automatiquement"' in rc.stdout

def test_slack_simulator(capsys):
    from bot.slack_handler import simulate_slack_upload
    simulate_slack_upload()
    out, _ = capsys.readouterr()
    assert "Sections extraites" in out or "Résultat structuré" in out

def test_email_handler(tmp_path, capsys):
    inbox_dir = tmp_path / "inbox"
    inbox_dir.mkdir()
    sample = "tests/samples/brief_sample.pdf"
    dest = inbox_dir / "brief1.pdf"
    shutil.copy(sample, dest)

    import bot.email_handler as eh
    eh.INBOX_DIR = str(inbox_dir)

    eh.handle_inbox()
    out, _ = capsys.readouterr()
    assert "-- PROBLEM --" in out.upper()
    assert "-- KPIS --" in out.upper()
