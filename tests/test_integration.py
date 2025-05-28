import os
import shutil
import subprocess
import sys
from pathlib import Path # Ajout de l'import Path pour une meilleure gestion des chemins

import pytest

# Chemin vers la racine du projet pour construire les chemins vers les scripts/fichiers de test
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_run_parser_cli(capsys): # capsys peut être utile si on veut vérifier stderr aussi
    """
    Vérifie que le script run_parser.py s'exécute correctement
    et extrait bien un titre depuis le brief PDF par défaut.
    Le brief par défaut est tests/samples/brief_sample.pdf.
    """
    run_parser_script = str(PROJECT_ROOT / "run_parser.py")
    cmd = [sys.executable, run_parser_script] # run_parser.py est appelé sans argument, il utilise son DEFAULT_BRIEF_PATH

    result = subprocess.run(cmd, capture_output=True, text=True, check=False)

    # Afficher stderr si le test échoue peut aider au débogage
    if result.returncode != 0:
        print(f"run_parser.py STDERR:\n{result.stderr}", file=sys.stderr)
        print(f"run_parser.py STDOUT:\n{result.stdout}", file=sys.stderr)

    assert result.returncode == 0, f"Le CLI run_parser.py a planté : {result.stderr}"
    
    # run_parser.py sans --report affiche le JSON brut de parse_brief (clés françaises)
    # On suppose que brief_sample.pdf donne "titre": "STATIC"
    # Si le comportement par défaut pour un brief vide/minimal est "Brief extrait automatiquement",
    # et que brief_sample.pdf est vide/minimal, alors cette assertion serait correcte.
    # Mais les logs précédents montraient "titre": "STATIC".
    
    # Vérifions la sortie JSON pour la clé "titre" et sa valeur attendue.
    # La sortie de `extract_brief_sections` pour `brief_sample.pdf` semble être `{"titre": "STATIC", ...}`
    expected_json_substring = '"titre": "STATIC"' # Clé française
    
    # Si un titre par défaut différent est attendu pour le cas où le PDF ne contient pas de titre explicite
    # et que `brief_sample.pdf` est ce cas-là :
    # expected_json_substring = '"titre": "Brief extrait automatiquement"'

    assert expected_json_substring in result.stdout, (
        f"Le contenu attendu ('{expected_json_substring}') n’a pas été trouvé dans la sortie JSON de run_parser.py:\n"
        f"STDOUT:\n{result.stdout}\n"
        f"STDERR:\n{result.stderr}"
    )


def test_slack_simulator(capsys):
    """
    Teste la commande simulate_upload depuis slack_handler.
    Vérifie que l'analyse PDF (via orchestrator.process_brief) produit une sortie cohérente.
    `simulate_upload` utilise `tests/samples/brief_sample.pdf`.
    """
    # Assurer que les modules nécessaires sont importables et configurés
    # (ex: si slack_handler dépend de variables d'env pour les chemins de schémas, etc.)
    try:
        from bot.slack_handler import simulate_upload
    except ImportError as e:
        pytest.skip(f"Impossible d'importer bot.slack_handler: {e}")

    simulate_upload() # Cette fonction doit printer le dict résultant de process_brief
    captured = capsys.readouterr()
    out = captured.out # Sortie standard capturée

    # orchestrator.process_brief retourne un dict avec des clés françaises.
    # `simulate_upload` imprime ce dict.
    # La sortie de process_brief pour `brief_sample.pdf` semble être `{'titre': 'STATIC', ...}`
    # On vérifie si la représentation str du dict contient la clé et la valeur attendues.
    
    # Log de pytest précédent :
    # out: '\n=== Résultat Simulation ===\n{\'titre\': \'STATIC\', \'problème\': "Brief statique pour les tests d\'intégration.", \'objectifs\': \'Test statique.\', \'kpis\': [\'TEST1\']}\n'
    
    # Attentes basées sur la sortie de `process_brief` pour `brief_sample.pdf`
    expected_titre_repr = "'titre': 'STATIC'" 
    # Si un résumé est attendu (par exemple, un résumé par défaut si non extrait)
    # expected_resume_repr = "'résumé': 'Valeur attendue pour le résumé'"

    # Vérifie la présence de la représentation du titre
    assert expected_titre_repr in out, (
        f"La simulation Slack n’a pas affiché le titre attendu ('{expected_titre_repr}') dans la sortie :\n"
        f"Sortie capturée (out):\n{out}"
    )
    
    # Optionnellement, vérifier d'autres champs si nécessaire.
    # Par exemple, si un résumé par défaut est toujours ajouté par process_brief :
    # assert "'résumé':" in out, (
    #     "La simulation Slack n'a pas affiché de clé 'résumé'.\n"
    #     f"Sortie capturée (out):\n{out}"
    # )


def test_email_handler(tmp_path, capsys):
    """
    Simule un dépôt de fichier dans l'inbox email et déclenche le handler.
    Vérifie que des extraits attendus sont loggués ou affichés.
    Ce test passait dans la dernière exécution.
    """
    inbox_dir = tmp_path / "inbox"
    inbox_dir.mkdir()
    
    # Utiliser un chemin absolu ou relatif au test pour le sample_pdf
    sample_pdf_path = PROJECT_ROOT / "tests" / "samples" / "brief_sample.pdf"
    if not sample_pdf_path.exists():
        pytest.fail(f"Fichier test {sample_pdf_path} introuvable.")
        
    inbox_pdf = inbox_dir / "brief1.pdf"
    shutil.copy(sample_pdf_path, inbox_pdf)

    try:
        import bot.email_handler as email_handler
    except ImportError as e:
        pytest.skip(f"Impossible d'importer bot.email_handler: {e}")

    # Sauvegarder l'ancienne valeur et la restaurer après le test si nécessaire
    original_inbox_dir = getattr(email_handler, "INBOX_DIR", None)
    email_handler.INBOX_DIR = str(inbox_dir)

    try:
        email_handler.handle_inbox() # Cette fonction doit printer les sections formatées
    finally:
        # Restaurer la valeur originale de INBOX_DIR pour ne pas affecter d'autres tests
        if original_inbox_dir is not None:
            email_handler.INBOX_DIR = original_inbox_dir
        elif hasattr(email_handler, "INBOX_DIR"): # Si elle a été settée par le test et n'existait pas
            del email_handler.INBOX_DIR


    captured = capsys.readouterr()
    out_upper = captured.out.upper() # La sortie est convertie en majuscules pour la comparaison

    # Les assertions restent les mêmes car elles vérifient des marqueurs de section
    # qui sont supposés être produits par email_handler.py
    assert "-- KPIS --" in out_upper, (
        "La section KPIS n’a pas été détectée dans la sortie de email_handler.\n"
        f"Sortie capturée (out.upper()):\n{out_upper}"
    )
    assert (
        "-- PROBLEM --" in out_upper or # Ancien format attendu
        "-- PROBLÈME --" in out_upper or # Nouveau format si la clé "problème" est utilisée
        "-- OBJECTIF --" in out_upper or # Ancien format attendu
        "-- OBJECTIFS --" in out_upper   # Nouveau format si la clé "objectifs" est utilisée
    ), (
        "Ni PROBLEM/PROBLÈME ni OBJECTIF/OBJECTIFS n’a été trouvé dans la sortie de email_handler.\n"
        f"Sortie capturée (out.upper()):\n{out_upper}"
    )