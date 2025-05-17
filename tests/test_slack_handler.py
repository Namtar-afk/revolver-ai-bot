import os
import shutil
import pytest

from utils.logger import logger
from bot.slack_handler import handle_veille_command, handle_analyse_command, simulate_upload


def test_simulate_upload(capsys):
    simulate_upload()
    out, _ = capsys.readouterr()
    assert "Brief extrait automatiquement" in out or "Résumé" in out


def test_handle_veille_command(tmp_path, monkeypatch):
    # Préparation d’un fichier CSV factice
    fake_csv = tmp_path / "veille.csv"
    monkeypatch.setenv("VEILLE_OUTPUT_PATH", str(fake_csv))

    message = handle_veille_command()

    assert message.startswith("✅")
    assert "items sauvegardés dans" in message


def test_handle_analyse_command(monkeypatch):
    # Patch pour neutraliser run_analyse
    import bot.slack_handler as sh
    monkeypatch.setattr(sh, "run_analyse", lambda: None)

    msg = handle_analyse_command()
    assert msg.startswith("✅ Analyse terminée.")
