import json  # Ceci doit être au tout début du fichier
from parser.pdf_parser import extract_text_from_pdf
from parser.nlp_utils import extract_brief_sections
from jsonschema import validate
from utils.logger import logger

def main():
    # Charger le schéma JSON pour la validation
    try:
        with open("schema/brief_schema.json") as f:
            schema = json.load(f)
    except Exception as e:
        logger.error(f"Erreur de chargement du schéma : {e}")
        exit(1)

    # Extraction du texte depuis le PDF
    text = extract_text_from_pdf("tests/samples/brief_sample.pdf")
    if not text:
        logger.error("❌ Échec de l'extraction PDF.")
        exit(1)

    # Extraction des sections du brief (problème, objectifs, KPIs)
    sections = extract_brief_sections(text)
    logger.info("✅ Extraction des sections :")
    logger.info(json.dumps(sections, indent=2, ensure_ascii=False))

    # Validation de la structure du brief avec le schéma JSON
    try:
        validate(instance=sections, schema=schema)
        logger.info("✅ Validation JSON réussie.")
    except Exception as e:
        logger.error(f"❌ Erreur de validation : {e}")
        exit(1)

if __name__ == "__main__":
    main()
