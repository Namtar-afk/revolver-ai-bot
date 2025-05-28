import pytest
from pathlib import Path
import json # Ajouté pour JSON_SAMPLE_TEXT_WITH_JSON

# Assure-toi que ces imports sont corrects et pointent vers tes modules
from parser.pdf_parser import (
    _clean_semantic,
    extract_text_from_pdf,
    extract_json_from_text,
)
# from utils.logger import logger # Commenté si logger.caplog n'est pas utilisé et que le logger standard est suffisant
# Importer le module parser.validator pour pouvoir le patcher
import parser.validator 


# Fixture pour créer un fichier PDF vide (ou invalide) temporaire
@pytest.fixture
def empty_pdf_file(tmp_path):
    file_path = tmp_path / "empty.pdf"
    # Un contenu qui n'est pas un PDF valide pour que pdfplumber lève une exception
    file_path.write_text("Ceci n'est pas une structure PDF valide.") 
    return str(file_path)

# Fixture pour créer un chemin vers un fichier PDF non existant
@pytest.fixture
def nonexistent_pdf_file(tmp_path):
    return str(tmp_path / "fichier_qui_n_existe_pas.pdf")


def test_clean_semantic_merges_hyphens_and_collapses_spaces():
    text = "un mot cou-\npé et   plusieurs  espaces."
    cleaned = _clean_semantic(text)
    assert cleaned == "un mot coupé et plusieurs espaces."

def test_extract_text_single_page(generated_brief): # Utilise ta fixture 'generated_brief'
    # Supposant que 'generated_brief' est un objet Path ou une str vers un PDF valide
    pdf_path_str = str(generated_brief) 
    
    text = extract_text_from_pdf(pdf_path_str)
    assert text is not None, f"Aucun texte n'a été extrait de {pdf_path_str}"
    
    # Adapte cette assertion au contenu réel attendu de ton 'generated_brief'
    # Si le titre "TITRE D'EXEMPLE" est attendu :
    assert "TITRE D'EXEMPLE" in text, \
        f"Le mot-clé 'TITRE D'EXEMPLE' n'a pas été trouvé dans le texte extrait : {text[:200]}..."
    # Ou si seulement "TITRE" (générique) est attendu et que sa casse peut varier :
    # assert "titre" in text.lower(), \
    #     f"Le mot-clé 'titre' (insensible à la casse) n'a pas été trouvé dans le texte : {text[:200]}..."


def test_extract_text_from_pdf_nonexistent(nonexistent_pdf_file, caplog):
    result = extract_text_from_pdf(nonexistent_pdf_file)
    assert result is None
    assert f"Fichier non trouvé : {nonexistent_pdf_file}" in caplog.text

def test_extract_text_from_pdf_empty(empty_pdf_file, caplog):
    result = extract_text_from_pdf(empty_pdf_file)
    assert result is None
    # Vérifie une partie du message d'erreur attendu de pdfplumber ou de ta gestion d'erreur
    assert "Erreur lors de l'extraction du texte du PDF" in caplog.text 
    # Tu peux ajouter une vérification plus spécifique de l'exception si pdfplumber en loggue une typique
    assert "Is this really a PDF?" in caplog.text # Partie du message d'erreur de pdfplumber


# Exemples de textes pour les tests de extract_json_from_text
JSON_SAMPLE_TEXT_WITH_JSON = """
Quelque texte avant le JSON.
{
  "title": "Un Titre JSON",
  "problem": "Un Problème à résoudre",
  "objectives": "Objectif JSON 1; Objectif JSON 2", 
  "kpis": "KPI Alpha; KPI Beta",
  "summary": "Résumé du JSON.",
  "internal_reformulation": "Reformulation interne du JSON."
}
Et du texte après le JSON, qui devrait être ignoré.
"""
JSON_SAMPLE_TEXT_NO_JSON = "Ceci est un texte simple sans aucune structure JSON."
JSON_SAMPLE_TEXT_INVALID_JSON = "Du texte puis {propriete_sans_quotes: valeur} du JSON invalide."


@pytest.fixture
def mock_validator_validate(monkeypatch):
    """Mock parser.validator.validate pour isoler les tests de extract_json_from_text."""
    def mock_validate_func(instance, schema_name):
        print(f"[MockValidator] Validation appelée pour '{schema_name}' avec instance: {instance}")
        if schema_name == "brief_output":
            assert isinstance(instance, dict), "MockValidator: L'instance doit être un dictionnaire."
            # Vérifie la présence des clés françaises attendues après normalisation
            required_french_keys = ["titre", "objectifs", "reformulation_interne", "résumé"] 
            for key in required_french_keys:
                assert key in instance, f"MockValidator: Clé française requise '{key}' manquante dans l'instance pour brief_output."
            # Simule une validation réussie
            return
        raise ValueError(f"MockValidator: Schéma inconnu '{schema_name}' dans le mock.")

    # Correction de la cible du monkeypatch :
    # Patcher la fonction 'validate' dans le module 'parser.validator'
    # C'est là que `extract_json_from_text` l'importe avec `from parser.validator import validate as _validate`
    monkeypatch.setattr(parser.validator, "validate", mock_validate_func)


def test_extract_json_from_text_success(mock_validator_validate): 
    result = extract_json_from_text(JSON_SAMPLE_TEXT_WITH_JSON)
    assert result is not None, "extract_json_from_text ne devrait pas retourner None pour un JSON valide."
    
    # Vérifie les clés françaises et les conversions de type attendues par le schéma 'brief_output'
    assert result.get("titre") == "Un Titre JSON"
    assert result.get("problème") == "Un Problème à résoudre" # Normalisé depuis "problem"
    assert isinstance(result.get("objectifs"), list), "'objectifs' devrait être une liste"
    assert result.get("objectifs") == ["Objectif JSON 1", "Objectif JSON 2"]
    assert isinstance(result.get("kpis"), list), "'kpis' devrait être une liste"
    assert result.get("kpis") == ["KPI Alpha", "KPI Beta"]
    assert result.get("résumé") == "Résumé du JSON." # Normalisé depuis "summary"
    assert result.get("reformulation_interne") == "Reformulation interne du JSON." # Normalisé depuis "internal_reformulation"


def test_extract_json_from_text_no_json(caplog):
    result = extract_json_from_text(JSON_SAMPLE_TEXT_NO_JSON)
    assert result is None
    assert "Aucune accolade ouvrante '{' trouvée dans le texte." in caplog.text


def test_extract_json_from_text_invalid_json(caplog):
    result = extract_json_from_text(JSON_SAMPLE_TEXT_INVALID_JSON)
    assert result is None
    assert "Échec du parsing JSON (JSONDecodeError)" in caplog.text
    # Vérifie une partie du message d'erreur spécifique au JSON invalide
    assert "Expecting property name enclosed in double quotes" in caplog.text