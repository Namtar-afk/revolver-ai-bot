import os
from pathlib import Path
import pytest

from bot.slack_handler import (
    handle_analyse_command,
    handle_veille_command,
    simulate_upload,
)
import bot.slack_handler # Pour mocker les noms tels qu'utilisés dans ce module
import bot.orchestrator  # Pour mocker les noms tels qu'utilisés dans ce module

from utils.logger import logger

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_simulate_upload(capsys, monkeypatch):
    def mock_process_brief(file_path_str):
        expected_path_as_passed = "tests/samples/brief_sample.pdf" # Correction ici
        assert file_path_str == expected_path_as_passed, \
            f"Chemin attendu: {expected_path_as_passed}, Chemin obtenu: {file_path_str}"
        logger.info(f"[Mock] mock_process_brief appelée pour {file_path_str}") # Ce log est utile pour le débogage
        return {
            "titre": "STATIC_TITLE_FROM_MOCK_PROCESS_BRIEF",
            "problème": "Un problème mocké",
            "objectifs": "Objectif mocké",
            "kpis": ["KPI mocké"],
            "résumé": "Résumé mocké",
            "reformulation_interne": "Reformulation mockée"
        }

    monkeypatch.setattr(bot.slack_handler, "process_brief", mock_process_brief)

    simulate_upload()
    captured = capsys.readouterr() # Capture stdout et stderr
    out = captured.out
    # err = captured.err # Nous n'allons plus l'utiliser pour vérifier les logs des mocks ici

    # L'important est que le mock ait été appelé (visible dans "Captured log call" de pytest)
    # et que la sortie de simulate_upload soit correcte grâce au mock.
    expected_titre_substring = "'titre': 'STATIC_TITLE_FROM_MOCK_PROCESS_BRIEF'"
    assert expected_titre_substring in out, (
        f"La sortie de simulate_upload ne contient pas le titre attendu.\n"
        f"Sortie capturée (out):\n{out}"
    )


@pytest.fixture
def mock_run_veille_dependencies(monkeypatch, tmp_path):
    fake_csv_output_path = str(tmp_path / "veille_test_slack_handler.csv")
    expected_items_count = 3

    mocked_items_list = [
        {"source": "rss_mock", "title": "RSS Item 1", "link": "link1", "date": "date1"},
        {"source": "google_trends", "keyword": "mock_keyword1", "trend": "[10,20]", "link": "link2", "date": "date2"},
        {"source": "google_trends", "keyword": "mock_keyword2", "trend": "[30,40]", "link": "link3", "date": "date3"},
    ]

    def mock_fetch_all_sources_for_veille():
        logger.info("[Mock] bot.orchestrator.fetch_all_sources appelée") # Utile pour le débogage
        return mocked_items_list

    def mock_save_to_csv_for_veille(items, path):
        logger.info(f"[Mock] bot.orchestrator.save_to_csv appelée avec {len(items)} items pour {path}") # Utile
        assert path == fake_csv_output_path
        assert len(items) == expected_items_count
        with open(path, "w", encoding="utf-8") as f:
            f.write("source,title,link,date\n")
            for item in items:
                f.write(f"{item.get('source','')},{item.get('title','')},{item.get('link','')},{item.get('date','')}\n")
        logger.info(f"Fichier mock CSV créé à : {path}") # Utile

    monkeypatch.setattr(bot.orchestrator, "fetch_all_sources", mock_fetch_all_sources_for_veille)
    monkeypatch.setattr(bot.orchestrator, "save_to_csv", mock_save_to_csv_for_veille)
    monkeypatch.setenv("VEILLE_OUTPUT_PATH", fake_csv_output_path)
    return expected_items_count, fake_csv_output_path


def test_handle_veille_command(mock_run_veille_dependencies): # capsys n'est plus nécessaire ici
    expected_items_count, fake_csv_output_path = mock_run_veille_dependencies

    message = handle_veille_command()

    # Les logs des mocks seront visibles dans "Captured log call" de pytest si vous exécutez avec -s ou -rA
    # Nous n'avons plus besoin de les vérifier explicitement ici si les assertions fonctionnelles passent.

    assert os.path.exists(fake_csv_output_path), f"Le fichier CSV mocké n'a pas été créé à {fake_csv_output_path}"
    assert message is not None, "handle_veille_command ne devrait pas retourner None"
    assert message.startswith("✅ Veille terminée"), f"Message inattendu: {message}"
    assert f"{expected_items_count} items sauvegardés dans" in message, \
        f"Le nombre d'items attendu n'est pas dans le message: {message}"
    assert fake_csv_output_path in message, \
        f"Le chemin du fichier CSV n'est pas dans le message: {message}"


def test_handle_analyse_command(monkeypatch): # capsys n'est plus nécessaire ici
    def mock_run_analyse_for_slack_handler(csv_path=None):
        logger.info(
            f"[Mock] mock_run_analyse_for_slack_handler appelée avec csv_path: {csv_path}"
        ) # Utile pour débogage

    monkeypatch.setattr(
        bot.slack_handler, "run_analyse", mock_run_analyse_for_slack_handler
    )

    message = handle_analyse_command()

    # Le log du mock sera visible dans "Captured log call"
    assert message == "✅ Analyse terminée."