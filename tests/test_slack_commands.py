import os
import pytest
from bot.slack_handler import handle_veille_command, handle_analyse_command


def test_handle_veille_command(tmp_path, monkeypatch):
    # Simuler un chemin de sortie temporaire pour le fichier CSV de veille
    fake_csv_path = tmp_path / "veille.csv"
    monkeypatch.setenv("VEILLE_OUTPUT_PATH", str(fake_csv_path))

    # Appeler la commande
    message = handle_veille_command()

    # Vérifications souples du format de retour
    assert message.startswith("✅")
    assert "items sauvegardés dans" in message


def test_handle_analyse_command(monkeypatch):
    # Empêcher l'exécution réelle de run_analyse
    import bot.slack_handler as sh
    monkeypatch.setattr(sh, "run_analyse", lambda: None)

    message = handle_analyse_command()

    assert message.startswith("✅ Analyse terminée.")
