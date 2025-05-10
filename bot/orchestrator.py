import json
import os
from parser.pdf_parser import extract_text_from_pdf
from parser.nlp_utils import extract_brief_sections
from jsonschema import validate
from utils.logger import logger

def process_brief(file_path: str) -> dict:
    """
    Lit un PDF, en extrait le texte, segmente les sections, valide le schéma.
    """
    logger.info(f"Lecture du fichier : {file_path}")

    text = extract_text_from_pdf(file_path)
    if not text:
        logger.error("Échec de l'extraction du texte PDF.")
        raise RuntimeError("Extraction PDF échouée")

    logger.info("Extraction des sections sémantiques…")
    sections = extract_brief_sections(text)

    logger.info("Validation du schéma JSON…")
    # Chemin relatif vers le schéma
    schema_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "schema", "brief_schema.json")
    )
    with open(schema_path, "r") as f:
        schema = json.load(f)

    validate(instance=sections, schema=schema)
    logger.info("Brief valide ✅")

    return sections
