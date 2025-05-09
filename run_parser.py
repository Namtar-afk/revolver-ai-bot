from parser.pdf_parser import extract_text_from_pdf
from parser.nlp_utils import extract_brief_sections
import json
from jsonschema import validate

with open("schema/brief_schema.json") as f:
    schema = json.load(f)

text = extract_text_from_pdf("tests/samples/brief_sample.pdf")
if not text:
    print("❌ Échec de l'extraction PDF.")
    exit(1)

sections = extract_brief_sections(text)
print("✅ Extraction des sections :")
print(json.dumps(sections, indent=2, ensure_ascii=False))

try:
    validate(instance=sections, schema=schema)
    print("✅ Validation JSON réussie.")
except Exception as e:
    print(f"❌ Erreur de validation : {e}")
