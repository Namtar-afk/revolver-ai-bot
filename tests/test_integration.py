import os
import shutil
import subprocess
import sys

import pytest


def test_run_parser_cli():
    """
    Vérifie que le script run_parser.py s'exécute correctement
    et extrait bien un titre depuis le brief PDF par défaut.
    """
    cmd = [sys.executable, "run_parser.py"]
    result = subprocess.run(cmd, capture_output=True, text=True)

    assert result.returncode == 0, f"Le CLI a planté : {result.stderr}"
    assert '"title": "Brief extrait automatiquement"' in result.stdout, (
        "Le titre attendu n’a pas été trouvé dans la sortie :\n" f"{result.stdout}"
    )


def test_slack_simulator(capsys):
    """
    Teste la commande simulate_upload depuis slack_handler.
    Vérifie que l'analyse PDF produit une sortie cohérente.
    """
    from bot.slack_handler import simulate_upload

    simulate_upload()
    out, _ = capsys.readouterr()

    assert "Brief extrait automatiquement" in out or "Résumé" in out, (
        "La simulation Slack n’a pas affiché le titre ni le résumé attendu :\n" f"{out}"
    )


def test_email_handler(tmp_path, capsys):
    """
    Simule un dépôt de fichier dans l'inbox email et déclenche le handler.
    Vérifie que des extraits attendus sont loggués ou affichés.
    """
    # Prépare un dossier inbox et y copie un sample PDF
    inbox_dir = tmp_path / "inbox"
    inbox_dir.mkdir()
    sample_pdf = "tests/samples/brief_sample.pdf"
    inbox_pdf = inbox_dir / "brief1.pdf"
    shutil.copy(sample_pdf, inbox_pdf)

    # Pointe l'INBOX_DIR de l'email handler vers notre dossier temporaire
    import bot.email_handler as email_handler

    email_handler.INBOX_DIR = str(inbox_dir)

    # Lance le traitement
    email_handler.handle_inbox()
    out, _ = capsys.readouterr()
    out_upper = out.upper()

    # Vérifie qu’on a bien extrait la section PROBLEM/OBJECTIF et les KPIS
    assert "-- KPIS --" in out_upper, "La section KPIS n’a pas été détectée"
    assert (
        "-- PROBLEM --" in out_upper or "-- OBJECTIF --" in out_upper
    ), "Ni PROBLEM ni OBJECTIF n’a été trouvé dans la sortie"
