#!/usr/bin/env python3
import argparse
import csv
import json
import os
import sys
from parser.nlp_utils import extract_brief_sections
from parser.pdf_parser import extract_text_from_pdf

from jsonschema import ValidationError, validate

from bot.analysis import detect_trends, summarize_items
from bot.monitoring import fetch_all_sources, save_to_csv
from utils.logger import logger


def load_brief_schema() -> dict:
    schema_path = os.path.join(
        os.path.dirname(__file__), "..", "schema", "brief_schema.json"
    )
    with open(schema_path, encoding="utf-8") as f:
        return json.load(f)


def normalize_keys(sections: dict) -> dict:
    """
    Corrige les clés alias (US → FR) pour valider le JSON.
    """
    key_map = {
        "title": "titre",
        "objectives": "objectifs",
    }
    for old, new in key_map.items():
        if old in sections and new not in sections:
            sections[new] = sections.pop(old)
    return sections


def process_brief(file_path: str) -> dict:
    """
    Extrait un brief depuis un PDF, corrige les clés, remplit
    les champs obligatoires et valide le schéma.
    """
    logger.info(f"[orchestrator] Lecture du fichier : {file_path}")
    text = extract_text_from_pdf(file_path)
    if not text:
        logger.error("[orchestrator] Échec extraction PDF.")
        raise RuntimeError("Extraction PDF échouée")

    # Extraction et normalisation initiale
    sections = extract_brief_sections(text)
    sections = normalize_keys(sections)

    # === Remplissage des champs obligatoires ===
    # Titre
    sections.setdefault("titre", "Brief extrait automatiquement")
    # Problème
    if not sections.get("problème") or not isinstance(sections.get("problème"), str):
        sections["problème"] = "Problème non précisé"
    # Objectifs : convertit liste (issue de nlp_utils) en texte
    obj_val = sections.get("objectifs")
    if isinstance(obj_val, list):
        sections["objectifs"] = (
            "; ".join(obj_val) if obj_val else "Objectifs non précisés"
        )
    elif not obj_val:
        sections["objectifs"] = "Objectifs non précisés"
    # KPIs : doit être une liste non vide
    kpi_val = sections.get("kpis")
    if not isinstance(kpi_val, list) or not kpi_val:
        sections["kpis"] = ["KPI non identifié"]

    # === Validation JSON ===
    schema = load_brief_schema()
    try:
        validate(instance=sections, schema=schema)
        logger.info("[orchestrator] Brief conforme au schéma ✅")
    except ValidationError as e:
        logger.warning(f"[orchestrator] Validation JSON partielle : {e.message}")

    return sections


def run_veille(output_path: str = "data/veille.csv") -> list[dict]:
    """
    Lance la veille et sauvegarde les résultats en CSV.
    """
    logger.info("[veille] Lancement de la veille média…")
    items = fetch_all_sources()
    save_to_csv(items, output_path)
    logger.info(f"[veille] Sauvegardé {len(items)} items dans {output_path}")
    return items


def run_analyse(csv_path: str = None) -> None:
    """
    Analyse les résultats de veille.
    """
    path = csv_path or os.getenv("VEILLE_CSV_PATH", "data/veille.csv")
    logger.info(f"[analyse] Chargement des items depuis {path}")

    if not os.path.exists(path):
        logger.error(f"[analyse] Fichier introuvable : {path}")
        raise FileNotFoundError(f"{path} non trouvé")

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        items = list(reader)

    summary = summarize_items(items)
    trends = detect_trends(items)

    print(summary)
    print("\nTendances détectées :")
    for trend in trends:
        print(f"• {trend}")


def delegate_to_report(brief_path: str, output_path: str) -> None:
    """
    Appelle run_parser.py pour générer un rapport PPTX.
    """
    logger.info("[report] Génération du rapport via run_parser.py")
    os.execvp(
        sys.executable,
        [
            sys.executable,
            "run_parser.py",
            "--brief",
            brief_path or "",
            "--report",
            output_path,
        ],
    )


def main():
    parser = argparse.ArgumentParser(description="Orchestrateur Revolvr AI Bot")
    parser.add_argument("--brief", help="Chemin vers un PDF de brief à traiter")
    parser.add_argument(
        "--veille",
        nargs="?",
        const="data/veille.csv",
        help="Lancer la veille (chemin optionnel)",
    )
    parser.add_argument(
        "--analyse", action="store_true", help="Analyser les données de veille"
    )
    parser.add_argument(
        "--report", metavar="OUTPUT", help="Générer un PPTX à partir d’un brief"
    )
    args = parser.parse_args()

    try:
        if args.brief:
            process_brief(args.brief)

        if args.veille is not None:
            run_veille(args.veille)

        if args.analyse:
            run_analyse(args.veille or "data/veille.csv")

        if args.report:
            delegate_to_report(args.brief, args.report)

    except Exception as e:
        logger.error(f"[orchestrator] Erreur critique : {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
