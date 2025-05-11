import json
import pytest
from parser.pdf_parser import extract_text_from_pdf
from parser.nlp_utils import extract_brief_sections
from jsonschema import validate

def test_parser_on_dynamic_brief(generated_brief):
    text = extract_text_from_pdf(generated_brief)
    assert text, "❌ Échec de l’extraction PDF"
    assert "Problème" in text

    sections = extract_brief_sections(text)
    with open("schema/brief_schema.json", encoding="utf-8") as f:
        schema = json.load(f)
    validate(instance=sections, schema=schema)
    assert all(sections.values()), f"Champs vides : {sections}"
