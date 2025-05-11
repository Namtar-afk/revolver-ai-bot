#!/usr/bin/env python3
"""
CLI principal : parse un brief_sample.pdf et affiche les sections,
même si la validation JSON échoue.
"""
import json
import os
import sys
from jsonschema import validate, ValidationError
from parser.pdf_parser import extract_text_from_pdf
from parser.nlp_utils import extract_brief_sections

def main():
    pdf = "tests/samples/brief_sample.pdf"
    text = extract_text_from_pdf(pdf)
    sections = extract_brief_sections(text)

    schema_path = os.path.join("schema", "brief_schema.json")
    with open(schema_path, encoding="utf-8") as f:
        schema = json.load(f)

    # 1) On affiche toujours les sections
    print(json.dumps(sections, ensure_ascii=False, indent=2))

    # 2) Puis on valide et on affiche le résultat
    try:
        validate(instance=sections, schema=schema)
        # print sans file= pour aller sur stdout
        print("Validation JSON réussie")
    except ValidationError as e:
        # garde stderr pour le message d'erreur
        print(f"Validation JSON échouée : {e.message}", file=sys.stderr)

if __name__ == "__main__":
    main()
