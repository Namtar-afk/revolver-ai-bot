import os
import shutil
from pathlib import Path

import pytest

# Assure-toi que ces imports pointent correctement vers tes modules
from bot.slack_handler import (
    handle_analyse_command,
    handle_veille_command, # La fonction testée
    simulate_upload,
)
import bot.orchestrator # Importe le module orchestrator pour pouvoir mocker ses fonctions

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_simulate_upload(capsys):
    """
    Teste la fonction simulate_upload.
    Cette fonction appelle orchestrator.process_brief avec 'tests/samples/brief_sample.pdf'
    et est censée imprimer le dictionnaire résultant.
    Le dictionnaire retourné par process_brief a des clés françaises.
    """
    simulate_upload()
    captured_output = capsys.readouterr()
    out = captured_output.out # Sortie standard capturée

    expected_titre_substring = "'titre': 'STATIC'"

    assert expected_titre_substring in out, (
        f"La sortie de simulate_upload ne contient pas le titre attendu ('{expected_titre_substring}').\n"
        f"Sortie capturée (out):\n{out}"
    )


def test_handle_veille_command(tmp_path, monkeypatch):
    """
    Teste la commande de veille en mockant l'appel à orchestrator.run_veille.
    """
    fake_csv_output_path = str(tmp_path / "veille_test_slack_handler.csv")
    expected_items_count = 3
    # orchestrator.run_veille retourne une liste d'items.
    mocked_items_list = [{"id": str(i), "title": f"Mocked Item {i}"} for i in range(expected_items_count)]

    # (1) Mocker bot.orchestrator.run_veille
    def mock_orchestrator_run_veille(output_path=None): # Signature doit correspondre à la vraie fonction run_veille
        print(f"[Mock] bot.orchestrator.run_veille appelée avec output_path: {output_path}")
        # La vraie fonction run_veille utilise output_path (qui vient de VEILLE_OUTPUT_PATH ou défaut)
        # et sauvegarde le fichier. Notre mock doit vérifier que ce chemin est celui attendu.
        assert output_path == fake_csv_output_path, \
            f"orchestrator.run_veille attendait output_path='{fake_csv_output_path}', reçu='{output_path}'"
        # Simuler la création du fichier (la vraie fonction le fait via save_to_csv)
        Path(output_path).touch() 
        return mocked_items_list # Retourne la liste d'items mockés

    monkeypatch.setattr(bot.orchestrator, "run_veille", mock_orchestrator_run_veille)
    
    # (2) S'assurer que handle_veille_command utilise la variable d'environnement
    # pour déterminer le chemin qu'il passera à orchestrator.run_veille (ou que run_veille lira).
    monkeypatch.setenv("VEILLE_OUTPUT_PATH", fake_csv_output_path)

    # (3) Appeler la fonction testée
    # handle_veille_command devrait appeler orchestrator.run_veille et utiliser son retour.
    message = handle_veille_command()

    # (4) Vérifier les assertions sur le message retourné
    assert message.startswith("✅ Veille terminée"), f"Message inattendu: {message}"
    assert f"{expected_items_count} items sauvegardés dans" in message, \
        f"Détails de sauvegarde manquants ou nombre d'items incorrect: {message}"
    # Le message de handle_veille_command doit contenir le chemin fake_csv_output_path
    assert fake_csv_output_path in message, \
        f"Le chemin '{fake_csv_output_path}' n'est pas dans le message retourné: {message}"


def test_handle_analyse_command(monkeypatch):
    """
    Teste la commande d'analyse.
    Ce test neutralise run_analyse pour éviter les dépendances externes.
    """
    import bot.slack_handler as slack_handler_module

    def mock_run_analyse(csv_path=None):
        print(f"[Mock] mock_run_analyse appelée avec csv_path: {csv_path}")

    try:
        # Si run_analyse est une fonction dans slack_handler_module
        monkeypatch.setattr(slack_handler_module, "run_analyse", mock_run_analyse)
    except AttributeError:
        # Si run_analyse est importée dans slack_handler_module depuis, par exemple, bot.orchestrator
        try:
            monkeypatch.setattr(bot.orchestrator, "run_analyse", mock_run_analyse)
        except AttributeError:
             pytest.fail("Vérifie la cible du monkeypatch pour run_analyse. "
                         "Est-elle dans bot.slack_handler ou bot.orchestrator, ou ailleurs ?")

    msg = handle_analyse_command() 
    assert msg.startswith("✅ Analyse terminée."), f"Message inattendu: {msg}"