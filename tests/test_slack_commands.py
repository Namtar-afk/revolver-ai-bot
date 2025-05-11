# tests/test_slack_commands.py

import os
from bot.slack_handler import handle_veille_command, handle_analyse_command

def test_handle_veille_command(tmp_path, monkeypatch):
    # Préparer un CSV factice
    csv = tmp_path / "veille.csv"
    csv.write_text("title,url,date\nA,b,2025-05-01\n", encoding="utf-8")
    monkeypatch.setenv("VEILLE_OUTPUT_PATH", str(csv))

    msg = handle_veille_command()

    # Vérifier que le message commence correctement
    assert msg.startswith("✅ Veille lancée")
    # Vérifier la présence de la partie statique du message
    assert "items sauvegardés dans" in msg

def test_handle_analyse_command(monkeypatch):
    # Stub run_analyse pour ne pas lire de CSV et capturer le print
    import bot.slack_handler as sh
    monkeypatch.setattr(sh, "run_analyse", lambda: print("Test analyse"))

    resp = handle_analyse_command()
    assert resp.startswith("✅")
