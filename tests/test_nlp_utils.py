import pytest
from parser.nlp_utils import extract_brief_sections


def test_extract_brief_sections_minimal():
    """
    Cas nominal avec des titres bien identifiés et des puces standard.
    """
    raw_text = """
    Problème : Le marché des soins naturels est saturé.
    Objectifs :
    - Accroître la notoriété de la marque
    - Générer de l'engagement sur Instagram

    KPIs :
    * +20% de reach organique
    * +10k abonnés en 1 mois
    """

    result = extract_brief_sections(raw_text)

    assert isinstance(result, dict)
    assert set(result.keys()) == {
        "title", "objectives", "internal_reformulation", "summary"
    }

    assert result["title"] == "Brief extrait automatiquement"
    assert isinstance(result["objectives"], list)
    assert len(result["objectives"]) >= 2
    assert result["objectives"][0].lower().startswith("accroître")
    assert "Reformulation automatique" in result["internal_reformulation"]
    assert "Résumé automatique" in result["summary"]


def test_extract_brief_sections_with_missing_titles():
    """
    Cas dégradé : aucun titre reconnu → fallback automatique.
    """
    raw_text = "Texte sans structure claire"
    result = extract_brief_sections(raw_text)

    assert isinstance(result, dict)
    assert set(result.keys()) == {
        "title", "objectives", "internal_reformulation", "summary"
    }

    assert isinstance(result["objectives"], list)
    assert len(result["objectives"]) == 1
    assert "Objectifs non identifiés" in result["objectives"][0]
    assert "Reformulation automatique" in result["internal_reformulation"]
    assert "Résumé automatique" in result["summary"]
