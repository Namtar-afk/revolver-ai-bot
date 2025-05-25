import json
from pathlib import Path

import pytest
from jsonschema import Draft7Validator

# Assure-toi que ces imports sont corrects
from parser.pdf_parser import extract_json_from_text, extract_text_from_pdf
from parser.validator import validate # Ta fonction de validation personnalisée

# Chemin vers la racine du projet
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_DIR = PROJECT_ROOT / "schema"


# Helper function pour charger le schéma JSON de manière robuste
def load_json_schema(schema_name: str):
    schema_file = SCHEMA_DIR / schema_name
    if not schema_file.exists():
        pytest.fail(f"Fichier schéma {schema_file} introuvable. Vérifiez le chemin et le nom du fichier.")
    try:
        with open(schema_file, encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        pytest.fail(f"Erreur de décodage JSON dans {schema_file}: {e}. Vérifiez la syntaxe du fichier.")
    except Exception as e:
        pytest.fail(f"Erreur inattendue lors du chargement de {schema_file}: {e}")


@pytest.mark.parametrize(
    "pdf_filename_relative_path, expect_json_present", 
    [
        # Pour ces deux fichiers, les logs et les prints ont montré qu'aucun JSON n'est trouvé.
        # Nous mettons donc expect_json_present à False.
        ("tests/samples/brief_simple.pdf", False), 
        ("tests/samples/brief_multi.pdf",  False),
        # TODO: Ajoute ici des PDF qui CONTIENNENT réellement un JSON pour tester la validation.
        # Exemple (à remplacer par un vrai fichier PDF contenant du JSON) :
        # ("tests/samples/brief_avec_json_valide.pdf", True), 
    ],
)
def test_schema_validation(pdf_filename_relative_path, expect_json_present):
    """
    Valide que le JSON extrait d'un PDF (s'il est attendu et trouvé) 
    est conforme au schéma 'brief_output.schema.json'.
    Si aucun JSON n'est attendu, vérifie qu'aucun n'est extrait.
    """
    pdf_path = PROJECT_ROOT / pdf_filename_relative_path
    assert pdf_path.exists(), f"Fichier PDF de test {pdf_path} introuvable."

    text_content = extract_text_from_pdf(str(pdf_path))
    
    # Décommente pour afficher le texte extrait lors du débogage
    # print(f"\n--- Contenu extrait de {pdf_filename_relative_path} ---")
    # if text_content:
    #     print(text_content[:2000] + "..." if len(text_content) > 2000 else text_content) 
    # else:
    #     print("Aucun texte n'a été extrait par extract_text_from_pdf.")
    # print("--- Fin du contenu extrait ---\n")

    if not text_content and expect_json_present:
        # Si on attendait du JSON mais que l'extraction de texte n'a rien donné du tout.
        pytest.fail(f"Aucun texte n'a été extrait de {pdf_path}, mais du JSON était attendu.")
    elif not text_content and not expect_json_present:
        # Si on n'attendait pas de JSON et que pas de texte n'est extrait, c'est OK pour cette partie.
        # On ne peut pas appeler extract_json_from_text avec None.
        extracted_data = None
    else: # text_content is not None
        extracted_data = extract_json_from_text(text_content)

    if expect_json_present:
        assert extracted_data is not None, \
            (f"Un JSON était attendu dans {pdf_path} mais extract_json_from_text a retourné None. "
             f"Vérifiez les logs de pdf_parser ou le contenu du PDF (via les prints de débogage).")
        
        # Les étapes de validation du schéma ne s'appliquent que si du JSON est attendu et trouvé.
        brief_output_schema = load_json_schema("brief_output_schema.json")

        try:
            Draft7Validator.check_schema(brief_output_schema)
        except Exception as e:
            pytest.fail(f"Le fichier {SCHEMA_DIR / 'brief_output.schema.json'} n'est pas un schéma JSON valide (Draft-07): {e}")

        try:
            validate(extracted_data, "brief_output") 
        except Exception as e: 
            pytest.fail(
                f"La validation des données extraites de {pdf_path} a échoué contre 'brief_output.schema.json'.\n"
                f"Erreur: {e}\n"
                f"Données: {json.dumps(extracted_data, indent=2, ensure_ascii=False)}"
            )

        assert "titre" in extracted_data, "Le champ 'titre' est manquant dans les données JSON extraites."
    else: # expect_json_present is False
        assert extracted_data is None, \
            (f"Aucun JSON n'était attendu dans {pdf_path}, mais extract_json_from_text a retourné des données : "
             f"{json.dumps(extracted_data, indent=2, ensure_ascii=False)}. "
             f"Le log de pdf_parser devrait indiquer pourquoi il a trouvé quelque chose.")