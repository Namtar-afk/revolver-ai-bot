import json
from parser.nlp_utils import extract_brief_sections
from parser.pdf_parser import extract_text_from_pdf

import pytest
from jsonschema import validate


def test_parser_on_dynamic_brief(generated_brief):
    text = extract_text_from_pdf(generated_brief)
    assert text, "❌ Échec de l’extraction PDF"
    assert "Problème" in text

    sections = extract_brief_sections(text)

    # Convertir en respectant types attendus par le schema
    sections_converted = {
        "titre": sections.get("title", ""),
        "problème": sections.get("internal_reformulation", ""),
        "objectifs": sections.get("objectives", ""),
        "kpis": [],
    }

    # objectifs doit être une string, on fait une concat si c'est une liste
    if isinstance(sections_converted["objectifs"], list):
        sections_converted["objectifs"] = " ".join(sections_converted["objectifs"])

    # kpis doit être une liste de chaînes, on essaye d'extraire depuis summary
    summary = sections.get("summary", "")
    if isinstance(summary, str):
        # Par exemple, séparer en lignes puis filtrer lignes vides
        sections_converted["kpis"] = [
            line.strip() for line in summary.split("\n") if line.strip()
        ]
    elif isinstance(summary, list):
        sections_converted["kpis"] = summary
    else:
        sections_converted["kpis"] = []

    with open("schema/brief_schema.json", encoding="utf-8") as f:
        schema = json.load(f)

    validate(instance=sections_converted, schema=schema)
    assert all(sections_converted.values()), f"Champs vides : {sections_converted}"
