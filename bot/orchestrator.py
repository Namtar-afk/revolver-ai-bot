#!/usr/bin/env python3
import argparse
import csv
import json
import os
import subprocess
import sys
from pathlib import Path

from jsonschema import ValidationError, validate
from parser.nlp_utils import extract_brief_sections
from parser.pdf_parser import extract_text_from_pdf
from bot.analysis import detect_trends, summarize_items
from bot.monitoring import fetch_all_sources, save_to_csv
from utils.logger import logger


def load_brief_schema() -> dict:
    """Charge le schéma JSON des briefs."""
    project_root = Path(__file__).resolve().parents[1]
    schema_path = project_root / "schema" / "brief_schema.json"
    if not schema_path.exists():
        logger.error(f"[orchestrator] Schéma introuvable : {schema_path}")
        raise FileNotFoundError(f"Schéma non trouvé: {schema_path}")
    try:
        return json.loads(schema_path.read_text(encoding="utf-8"))
    except Exception as e:
        logger.error(f"[orchestrator] Erreur lecture schéma JSON : {e}")
        raise


def normalize_keys(sections: dict) -> dict:
    """Normalise les noms de clés extraites d’un brief."""
    if not isinstance(sections, dict):
        raise RuntimeError("normalize_keys: sections doit être un dictionnaire")
    key_map = {"title": "titre", "objectives": "objectifs"}
    normalized = sections.copy()
    for old, new in key_map.items():
        if old in normalized and new not in normalized:
            normalized[new] = normalized.pop(old)
    return normalized


def process_brief(file_path: str) -> dict:
    """Traite un fichier PDF de brief et renvoie les sections normalisées."""
    logger.info(f"[orchestrator] Lecture du fichier : {file_path}")
    text = extract_text_from_pdf(file_path)
    if not text:
        raise RuntimeError("Extraction PDF échouée : document vide ou illisible.")

    sections = normalize_keys(extract_brief_sections(text) or {})
    sections.setdefault("titre", "Brief extrait automatiquement")
    sections["problème"] = sections.get("problème") or "Problème non précisé"

    obj = sections.get("objectifs")
    if isinstance(obj, list):
        sections["objectifs"] = "; ".join(filter(None, obj)) or "Objectifs non précisés"
    elif not isinstance(obj, str) or not obj.strip():
        sections["objectifs"] = "Objectifs non précisés"

    kpi = sections.get("kpis")
    if isinstance(kpi, list) and any(kpi):
        sections["kpis"] = kpi
    elif isinstance(kpi, str) and kpi.strip():
        sections["kpis"] = [k.strip() for k in kpi.split(";") if k.strip()]
    else:
        sections["kpis"] = ["KPI non identifié"]

    try:
        schema = load_brief_schema()
        validate(instance=sections, schema=schema)
        logger.info("[orchestrator] Brief conforme au schéma ✅")
    except ValidationError as ve:
        logger.warning(f"[orchestrator] Validation partielle : {ve.message}")
    return sections


def run_veille(output_path: str = "data/veille.csv") -> list[dict]:
    """Lance la veille média et enregistre les résultats en CSV."""
    logger.info("[veille] Lancement veille média...")
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    items = fetch_all_sources()
    save_to_csv(items, output_path)
    logger.info(f"[veille] Sauvegarde de {len(items)} items dans '{output_path}'")
    return items


def run_analyse(csv_path: str = "data/veille.csv") -> None:
    """Analyse les données de veille depuis un fichier CSV."""
    path = Path(csv_path)
    if not path.exists():
        logger.error(f"[analyse] Fichier introuvable : {path}")
        print(f"Erreur : fichier veille {path} non trouvé.", file=sys.stderr)
        return

    try:
        with open(path, newline="", encoding="utf-8") as f:
            items = list(csv.DictReader(f))
    except Exception as e:
        logger.error(f"[analyse] Erreur lecture CSV : {e}")
        print(f"Erreur lecture CSV : {e}", file=sys.stderr)
        return

    if not items:
        logger.warning("[analyse] Aucun item à analyser.")
        print("Aucun item à analyser.")
        return

    print(summarize_items(items))
    print("\nTendances détectées :")
    for trend in detect_trends(items):
        print(f"• {trend}")


def delegate_to_report(brief_path: str, output_path: str) -> None:
    """Délègue la génération d’un rapport à run_parser.py."""
    run_parser = Path(__file__).resolve().parents[1] / "run_parser.py"
    if not run_parser.exists():
        logger.error(f"[report] Script introuvable : {run_parser}")
        return

    logger.info(f"[report] Génération via {run_parser}")
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    command = [
        sys.executable,
        str(run_parser),
        "--brief", brief_path or "",
        "--report", output_path,
    ]

    try:
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode == 0:
            logger.info("[report] Rapport généré avec succès.")
            logger.debug(result.stdout)
        else:
            logger.error(f"[report] Erreur génération :\n{result.stderr}")
    except Exception as e:
        logger.error(f"[report] Échec exécution run_parser.py : {e}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Orchestrateur Revolvr AI Bot")
    parser.add_argument("--brief", help="Chemin vers un PDF de brief à traiter")
    parser.add_argument("--veille", nargs="?", const="data/veille.csv", help="Lancer la veille (CSV)")
    parser.add_argument("--analyse", action="store_true", help="Analyser la veille")
    parser.add_argument("--report", metavar="OUTPUT_PPTX", help="Générer le rapport PPTX")

    args = parser.parse_args()

    try:
        if args.veille is not None:
            run_veille(args.veille)
        if args.analyse:
            run_analyse(args.veille or "data/veille.csv")
        if args.brief:
            brief_data = process_brief(args.brief)
            logger.info(f"[orchestrator] Brief traité :\n{json.dumps(brief_data, indent=2, ensure_ascii=False)}")
        if args.report:
            delegate_to_report(args.brief, args.report)
        if not any([args.brief, args.veille is not None, args.analyse, args.report]):
            parser.print_help()

    except Exception as e:
        logger.error(f"[orchestrator] Exception : {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
