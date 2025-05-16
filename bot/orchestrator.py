#!/usr/bin/env python3
import json
import os
import sys
import csv
import pdfplumber
from argparse import ArgumentParser
from jsonschema import validate, ValidationError

from parser.pdf_parser import extract_text_from_pdf
from parser.nlp_utils    import extract_brief_sections
from utils.logger        import logger
from bot.monitoring      import fetch_all_sources, save_to_csv
from bot.analysis        import summarize_items, detect_trends

def process_brief(file_path: str) -> dict:
    """
    Lit et valide un PDF de brief.
    Retourne un dict brut.
    """
    logger.info(f"[orchestrator] Lecture du fichier : {file_path}")
    text = extract_text_from_pdf(file_path)
    if not text:
        logger.error("[orchestrator] Échec extraction PDF.")
        raise RuntimeError("Extraction PDF échouée")

    sections = extract_brief_sections(text)
    schema_path = os.path.join(os.path.dirname(__file__), "..", "schema", "brief_schema.json")
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    try:
        validate(instance=sections, schema=schema)
        logger.info("[orchestrator] Brief valide ✅")
    except ValidationError as e:
        logger.warning(f"[orchestrator] Validation JSON partielle : {e.message}")

    return sections

def run_veille(output_path: str = "data/veille.csv") -> list[dict]:
    """
    Récupère les items de veille et les sauvegarde en CSV.
    """
    logger.info("[veille] Lancement de la veille média…")
    items = fetch_all_sources()
    save_to_csv(items, output_path)
    logger.info(f"[veille] Sauvegardé {len(items)} items dans {output_path}")
    return items

def run_analyse(csv_path: str = None):
    """
    Charge un CSV de veille, synthétise et imprime la synthèse + tendances.
    """
    veille_path = csv_path or os.getenv("VEILLE_CSV_PATH", "data/veille.csv")
    logger.info(f"[analyse] Chargement des items depuis {veille_path}")

    if not os.path.exists(veille_path):
        logger.error(f"[analyse] Fichier introuvable : {veille_path}")
        raise FileNotFoundError(f"{veille_path} non trouvé")

    with open(veille_path, newline="", encoding="utf-8") as f:
        items = list(csv.DictReader(f))

    summary = summarize_items(items)
    trends  = detect_trends(items)

    print(summary)
    for t in trends:
        print(f"• {t}")

def main():
    parser = ArgumentParser(description="Orchestrateur Revolvr AI Bot")
    parser.add_argument("--brief",  help="Chemin vers le PDF de brief")
    parser.add_argument(
        "--veille",
        nargs="?",
        const="data/veille.csv",
        help="Lance la veille et sauve (optionnel: chemin)"
    )
    parser.add_argument(
        "--analyse",
        action="store_true",
        help="Lance l'analyse des items de veille"
    )
    parser.add_argument(
        "--report",
        metavar="OUTPUT",
        help="Génère un PPTX de recommandations"
    )
    args = parser.parse_args()

    if args.brief:
        try:
            process_brief(args.brief)
        except Exception as e:
            logger.error(f"[orchestrator] process_brief a échoué : {e}")
            sys.exit(1)

    if args.veille is not None:
        try:
            run_veille(args.veille)
        except Exception as e:
            logger.error(f"[orchestrator] run_veille a échoué : {e}")
            sys.exit(1)

    if args.analyse:
        try:
            run_analyse()
        except Exception as e:
            logger.error(f"[orchestrator] run_analyse a échoué : {e}")
            sys.exit(1)

    if args.report:
        # délègue au CLI principal
        os.execvp("python", [
            "python", "run_parser.py",
            "--brief", args.brief or "",
            "--report", args.report
        ])

if __name__ == "__main__":
    main()

def extract_text_from_pdf(file_path):
    try:
        with pdfplumber.open(file_path) as pdf:
            return "\n".join([page.extract_text() or "" for page in pdf.pages])
    except Exception as e:
        logger.error(f"[ERROR] Failed to extract PDF text: {e}")
        return ""
