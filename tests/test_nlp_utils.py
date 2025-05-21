from parser.nlp_utils import extract_brief_sections

import pytest


def test_extract_brief_sections_minimal():
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
    assert result["title"] == "Brief extrait automatiquement"
    assert isinstance(result["objectives"], list)
    assert len(result["objectives"]) >= 2
    assert result["internal_reformulation"].startswith(
        "Reformulation automatique du problème"
    )
    assert result["summary"].startswith("Résumé automatique des KPIs")


def test_extract_brief_sections_with_missing_titles():
    raw_text = "Texte sans structure claire"
    result = extract_brief_sections(raw_text)

    assert isinstance(result["objectives"], list)
    assert len(result["objectives"]) == 1
    assert "Reformulation automatique" in result["internal_reformulation"]
    assert "Résumé automatique" in result["summary"]
