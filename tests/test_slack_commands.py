import os
import pytest

from bot.slack_handler import handle_veille_command, handle_analyse_command


def test_handle_veille_command(tmp_path, monkeypatch):
    # Préparer un fichier CSV simulé pour la veille
    fake_csv = tmp_path / "veille.csv"
    fake_csv.write_text("title,url,date\nA,b,2025-05-01\n", encoding="utf-8")
    monkeypatch.setenv("VEILLE_OUTPUT_PATH", str(fake_csv))

    message = handle_veille_command()

    # Test tolérant : on vérifie la bonne structure du retour
    assert message.startswith("✅")
    assert "items sauvegardés dans" in message


def test_handle_analyse_command(monkeypatch):
    # Stub de run_analyse pour éviter les effets de bord
    import bot.slack_handler as sh
    monkeypatch.setattr(sh, "run_analyse", lambda: None)

    message = handle_analyse_command()
    assert message.startswith("✅")
    assert "Analyse" in message
