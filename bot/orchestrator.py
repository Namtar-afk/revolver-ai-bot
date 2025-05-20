import os
import sys
import json
import csv
import argparse
import pdfplumber
from jsonschema import validate, ValidationError

from parser.pdf_parser import extract_text_from_pdf
from parser.nlp_utils import extract_brief_sections
from utils.logger import logger
from bot.monitoring import fetch_all_sources, save_to_csv
from bot.analysis import summarize_items, detect_trends


def process_brief(file_path: str) -> dict:
    """
    Lit un PDF de brief, en extrait le texte, segmente les sections,
    valide selon le schéma JSON et renvoie le dictionnaire structuré.
    """
    logger.info(f"[orchestrator] Lecture du fichier : {file_path}")
    text = extract_text_from_pdf(file_path)
    if not text:
        logger.error("[orchestrator] Échec extraction PDF.")
        raise RuntimeError("Extraction PDF échouée")

    sections = extract_brief_sections(text)
    schema_path = os.path.join(os.path.dirname(__file__), "..", "schema", "brief_schema.json")
    with open(schema_path, encoding="utf-8") as f:
        schema = json.load(f)

    try:
        validate(instance=sections, schema=schema)
        logger.info("[orchestrator] Brief conforme au schéma ✅")
    except ValidationError as e:
        logger.warning(f"[orchestrator] Validation JSON partielle : {e.message}")

    return sections


def run_veille(output_path: str = "data/veille.csv") -> list[dict]:
    """
    Récupère les items de veille média, les enregistre en CSV et retourne la liste.
    """
    logger.info("[veille] Lancement de la veille média…")
    items = fetch_all_sources()
    save_to_csv(items, output_path)
    logger.info(f"[veille] Sauvegardé {len(items)} items dans {output_path}")
    return items


def run_analyse(csv_path: str = None) -> None:
    """
    Analyse les items de veille : synthèse et détection de tendances.
    Affiche le résumé et la liste des tendances.
    """
    veille_file = csv_path or os.getenv("VEILLE_CSV_PATH", "data/veille.csv")
    logger.info(f"[analyse] Chargement des items depuis {veille_file}")

    if not os.path.exists(veille_file):
        logger.error(f"[analyse] Fichier introuvable : {veille_file}")
        raise FileNotFoundError(f"{veille_file} non trouvé")

    with open(veille_file, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        items = list(reader)

    summary = summarize_items(items)
    trends = detect_trends(items)

    print(summary)
    for trend in trends:
        print(f"• {trend}")


def main():
    parser = argparse.ArgumentParser(description="Orchestrateur Revolvr AI Bot")
    parser.add_argument("--brief", help="Chemin vers le PDF de brief")
    parser.add_argument("--veille", nargs="?", const="data/veille.csv", help="Lance la veille et sauve (optionnel: chemin)")
    parser.add_argument("--analyse", action="store_true", help="Lance l'analyse des items de veille")
    parser.add_argument("--report", metavar="OUTPUT", help="Génère un PPTX de recommandations")
    args = parser.parse_args()

    if args.brief:
        try:
            process_brief(args.brief)
        except Exception as e:
            logger.error(f"[orchestrator] Échec process_brief : {e}")
            sys.exit(1)

    if args.veille is not None:
        try:
            run_veille(args.veille)
        except Exception as e:
            logger.error(f"[orchestrator] Échec run_veille : {e}")
            sys.exit(1)

    if args.analyse:
        try:
            run_analyse()
        except Exception as e:
            logger.error(f"[orchestrator] Échec run_analyse : {e}")
            sys.exit(1)

    if args.report:
        # Délègue la génération PPTX au CLI principal
        os.execvp(sys.executable, [sys.executable, "run_parser.py", "--brief", args.brief or "", "--report", args.report])


if __name__ == "__main__":
    main()
