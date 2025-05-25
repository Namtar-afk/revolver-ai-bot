import json
from pathlib import Path

import pytest
from jsonschema import validate

# Assure-toi que ces imports pointent correctement vers tes modules
from parser.nlp_utils import extract_brief_sections
from parser.pdf_parser import extract_text_from_pdf

# Chemin vers la racine du projet pour aider à localiser les fichiers de manière fiable
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_parser_on_dynamic_brief(generated_brief): # Utilisation du nom de fixture correct 'generated_brief'
    """
    Teste l'extraction et la validation d'un brief généré dynamiquement (PDF).
    1. Extrait le texte du PDF.
    2. Extrait les sections structurées (clés françaises) du texte.
    3. Valide ces sections par rapport au schéma français 'brief_schema.json'.
    """ # Assure-toi que cette ligne de fermeture est bien présente et correcte.
    
    # Vérifie si generated_brief est un objet Path ou une chaîne et agit en conséquence
    pdf_path_to_test = None
    if isinstance(generated_brief, Path):
        pdf_path_to_test = generated_brief
    elif isinstance(generated_brief, str):
        pdf_path_to_test = Path(generated_brief)
    else:
        pytest.fail(f"La fixture 'generated_brief' a retourné un type inattendu: {type(generated_brief)}")

    assert pdf_path_to_test.exists(), f"Le fichier PDF généré {pdf_path_to_test} n'existe pas."

    text = extract_text_from_pdf(str(pdf_path_to_test)) # extract_text_from_pdf attend une chaîne
    assert text, f"❌ Échec de l’extraction de texte du PDF: {pdf_path_to_test}"
    
    # Optionnel: Vérifier un mot-clé attendu si le contenu du PDF généré est connu.
    # assert "Problème" in text, "Le mot-clé 'Problème' n'a pas été trouvé dans le texte extrait du PDF."

    # `extract_brief_sections` retourne un dict avec des clés françaises.
    sections = extract_brief_sections(text)
    assert isinstance(sections, dict), "extract_brief_sections doit retourner un dictionnaire."

    # Charger le schéma FRANÇAIS 'brief_schema.json'
    # Ce chemin suppose que pytest est lancé depuis la racine du projet où se trouve 'schema/'
    schema_file_path = PROJECT_ROOT / "schema" / "brief_schema.json"
    
    assert schema_file_path.exists(), (
        f"Le fichier schéma {schema_file_path} est introuvable. "
        "Assurez-vous que 'schema/brief_schema.json' existe à la racine du projet et contient le schéma FRANÇAIS."
    )

    try:
        with open(schema_file_path, encoding="utf-8") as f:
            french_brief_schema = json.load(f)
    except json.JSONDecodeError as e:
        pytest.fail(f"Erreur de décodage JSON dans {schema_file_path}: {e}. Vérifiez le contenu du fichier.")
    except Exception as e:
        pytest.fail(f"Erreur lors du chargement de {schema_file_path}: {e}")

    # Valider l'instance 'sections' (directement issue de extract_brief_sections)
    # contre le schéma français.
    # L'ÉCHEC ACTUEL DE CE TEST SE PRODUIT ICI SI french_brief_schema N'EST PAS LE BON (FRANÇAIS).
    try:
        validate(instance=sections, schema=french_brief_schema)
    except Exception as e: # Attrape jsonschema.exceptions.ValidationError ou autres erreurs
        # Imprimer le schéma utilisé peut aider à diagnostiquer si c'est le bon
        schema_title_for_debug = french_brief_schema.get('title', 'Titre de schéma non trouvé')
        pytest.fail(
            f"La validation de l'instance 'sections' a échoué contre '{schema_file_path}' (titre du schéma chargé: '{schema_title_for_debug}').\n"
            f"Erreur: {e}\n"
            f"Instance: {json.dumps(sections, indent=2, ensure_ascii=False)}"
        )

    # Vérifier que les champs principaux (ceux définis comme 'required' dans le schéma français)
    # ont bien des valeurs. `extract_brief_sections` fournit des valeurs par défaut.
    assert sections.get("titre"), f"Le champ 'titre' est vide ou manquant dans les sections extraites: {sections}"
    assert sections.get("problème"), f"Le champ 'problème' est vide ou manquant: {sections}"
    assert sections.get("objectifs"), f"Le champ 'objectifs' est vide ou manquant: {sections}"
    assert sections.get("kpis") is not None, f"Le champ 'kpis' est manquant (devrait être une liste): {sections}"
    assert isinstance(sections.get("kpis"), list), f"Le champ 'kpis' devrait être une liste: {sections}"
    
    # `extract_brief_sections` met ["KPI non identifié"] par défaut si aucun KPI n'est trouvé.
    assert len(sections["kpis"]) > 0, f"La liste 'kpis' ne devrait pas être vide (au moins un placeholder): {sections}"