from utils.logger import logger

def process_brief(file_path: str) -> dict:
    logger.info(f"Lecture du fichier : {file_path}")
    text = extract_text_from_pdf(file_path)
    if not text:
        logger.error("Échec de l'extraction du texte PDF.")
        raise ValueError("Échec de l'extraction du texte PDF.")

    logger.info("Extraction des sections sémantiques...")
    sections = extract_brief_sections(text)

    logger.info("Validation du schéma JSON...")
    try:
        with open("schema/brief_schema.json") as f:
            schema = json.load(f)

        validate(instance=sections, schema=schema)
        logger.info("Validation JSON réussie.")
    except Exception as e:
        logger.error(f"Erreur de validation : {e}")
        raise

    return sections

