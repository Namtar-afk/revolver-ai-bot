from parser.pdf_parser import extract_text_from_pdf
from parser.nlp_utils import extract_brief_sections
import json
from jsonschema import validate

# Charger le schéma JSON pour la validation
with open("schema/brief_schema.json") as f:
    schema = json.load(f)

# Extraction du texte depuis le PDF
text = extract_text_from_pdf("tests/samples/brief_sample.pdf")
if not text:
    print("❌ Échec de l'extraction PDF.")
    exit(1)

# Extraction des sections du brief (problème, objectifs, KPIs)
sections = extract_brief_sections(text)
print("✅ Extraction des sections :")
print(json.dumps(sections, indent=2, ensure_ascii=False))

# Validation de la structure du brief avec le schéma JSON
try:
    validate(instance=sections, schema=schema)
    print("✅ Validation JSON réussie.")
except Exception as e:
    print(f"❌ Erreur de validation : {e}")

# Appeler la simulation Slack (exécution du processus complet)
from bot.slack_handler import simulate_slack_upload

if __name__ == "__main__":
    simulate_slack_upload()

