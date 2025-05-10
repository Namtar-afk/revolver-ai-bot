import json
import os
from parser.pdf_parser import extract_text_from_pdf
from parser.nlp_utils import extract_brief_sections
from jsonschema import validate
from utils.logger import logger
from bot.monitoring import fetch_all_sources, save_to_csv

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
    schema_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "schema", "brief_schema.json")
    )
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    validate(instance=sections, schema=schema)
    logger.info("Brief valide ✅")

    return sections


def run_veille(output_path: str = "data/veille.csv") -> list[dict]:
    """
    Déclenche la veille média (RSS, Trends, social scrape) et sauve en CSV.
    """
    logger.info("[veille] Lancement de la veille média…")
    items = fetch_all_sources()
    save_to_csv(items, output_path)
    logger.info(f"[veille] Sauvegardé {len(items)} items dans {output_path}")
    return items


# Exemple d’usage dans main ou via un flag CLI
if __name__ == "__main__":
    # Par défaut, on lance les deux en séquence pour tester :
    from argparse import ArgumentParser

    parser = ArgumentParser(description="Orchestrateur Revolvr AI Bot")
    parser.add_argument("--brief", help="Chemin vers le PDF de brief")
    parser.add_argument("--veille", nargs="?", const="data/veille.csv",
                        help="Lance la veille et sauve en CSV (optionnel: chemin de sortie)")
    args = parser.parse_args()

    if args.brief:
        process_brief(args.brief)

    if args.veille:
        run_veille(args.veille)
