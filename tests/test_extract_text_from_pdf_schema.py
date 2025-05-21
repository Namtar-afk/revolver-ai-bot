import json
from parser.nlp_utils import extract_brief_sections
from parser.pdf_parser import extract_text_from_pdf

import pytest
from jsonschema import validate


@pytest.mark.parametrize("fixture", ["brief_simple.pdf", "brief_multi.pdf"])
def test_schema_validation(fixture):
    pdf = f"tests/samples/{fixture}"
    text = extract_text_from_pdf(pdf)
    assert (
        text is not None and text.strip() != ""
    ), f"Extraction PDF vide ou invalide pour {pdf}"
    data = extract_brief_sections(text)
    with open("schema/brief_output.schema.json", encoding="utf-8") as f:
        schema = json.load(f)
    validate(instance=data, schema=schema)
