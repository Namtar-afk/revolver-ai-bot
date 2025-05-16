import os
import sys
import subprocess
import shutil
import pytest


def test_run_parser_cli():
    """
    Vérifie que le script run_parser.py s'exécute correctement
    et extrait bien un titre depuis le brief PDF par défaut.
    """
    cmd = [sys.executable, "run_parser.py"]
    result = subprocess.run(cmd, capture_output=True, text=True)

    assert result.returncode == 0, result.stderr
    assert '"title": "Brief extrait automatiquement"' in result.stdout


def test_slack_simulator(capsys):
    """
    Teste la commande simulate_upload depuis slack_handler.
    Vérifie que l'analyse PDF produit une sortie partielle cohérente.
    """
    from bot.slack_handler import simulate_upload
    simulate_upload()
    out, _ = capsys.readouterr()

    assert "Brief extrait automatiquement" in out or "Résumé" in out


def test_email_handler(tmp_path, capsys):
    """
    Simule un dépôt de fichier dans l'inbox email et déclenche le handler.
    Vérifie que des extraits attendus sont loggués ou affichés.
    """
    inbox_dir = tmp_path / "inbox"
    inbox_dir.mkdir()
    sample_pdf = "tests/samples/brief_sample.pdf"
    inbox_pdf = inbox_dir / "brief1.pdf"
    shutil.copy(sample_pdf, inbox_pdf)

    import bot.email_handler as email_handler
    email_handler.INBOX_DIR = str(inbox_dir)

    email_handler.handle_inbox()
    out, _ = capsys.readouterr()

    out_upper = out.upper()
    assert "-- PROBLEM --" in out_upper or "-- OBJECTIF --" in out_upper
    assert "-- KPIS --" in out_upper
