import json
import pytest
from parser.pdf_parser import extract_text_from_pdf
from parser.nlp_utils import extract_brief_sections
from jsonschema import validate

def test_brief_extraction():
    text = extract_text_from_pdf("tests/samples/brief_sample.pdf")
    assert text, "Échec de l’extraction PDF"

    data = extract_brief_sections(text)
    assert all(data.values()), f"Champs vides dans : {data}"

    with open("schema/brief_schema.json") as f:
        schema = json.load(f)

    validate(instance=data, schema=schema)
