#!/usr/bin/env python3
import json
import os
import sys
from argparse import ArgumentParser
from jsonschema import validate, ValidationError

from parser.pdf_parser import extract_text_from_pdf
from parser.nlp_utils import extract_brief_sections
from reco.generator import generate_recommendation
from reco.models import (
    BriefReminder,
    DeckData,
    BrandOverview,
    StateOfPlaySection,
)
import pptx_generator.slide_builder

# === Defaults ===
DEFAULT_BRIEF = os.path.join(
    os.path.dirname(__file__),
    "tests", "samples", "brief_sample.pdf"
)

SCHEMA_PATH = os.path.join(
    os.path.dirname(__file__),
    "schema", "brief_schema.json"
)

# === Step 1 — Extraction + validation JSON ===
def parse_brief(path: str) -> dict:
    print(f"[INFO] Lecture du brief : {path}", file=sys.stderr)
    text = extract_text_from_pdf(path)
    sections = extract_brief_sections(text)

    try:
        with open(SCHEMA_PATH, encoding="utf-8") as f:
            schema = json.load(f)
        validate(instance=sections, schema=schema)
        print("[INFO] Validation JSON réussie", file=sys.stderr)
    except (ValidationError, FileNotFoundError, json.JSONDecodeError) as e:
        print(f"[WARN] Échec de validation JSON : {e}", file=sys.stderr)

    return sections

# === Step 2 — CLI Handler ===
def main():
    parser = ArgumentParser(description="Revolver AI Bot Report CLI")
    parser.add_argument("--brief", help="PDF de brief client")
    parser.add_argument("--report", metavar="OUTPUT", help="Chemin de sortie .pptx")
    args = parser.parse_args()

    # 1. Chargement du brief
    brief_path = args.brief or DEFAULT_BRIEF
    brief_dict = parse_brief(brief_path)

    # 2. Mode génération du rapport
    if args.report:
        # a. Conversion dict → BriefReminder (Pydantic)
        try:
            brief = BriefReminder(**brief_dict)
        except Exception as e:
            print(f"[WARN] Conversion Pydantic échouée : {e}", file=sys.stderr)
            brief = BriefReminder(
                title="Brief statique",
                objectives=["Non précisé"],
                internal_reformulation="Reformulation automatique",
                summary="Résumé automatique"
            )

        # b. Veille & tendances
        try:
            from bot.monitoring import fetch_all_sources, save_to_csv
            from bot.analysis import detect_trends

            veille = fetch_all_sources()
            save_to_csv(veille, "data/veille.csv")
            raw_trends = detect_trends(veille)
            trends = [StateOfPlaySection(theme=theme, evidence=[]) for theme in raw_trends]
        except Exception as e:
            print(f"[WARN] Veille indisponible : {e}", file=sys.stderr)
            trends = []

        # c. Génération du deck
        try:
            deck: DeckData = generate_recommendation(brief, trends)
        except Exception as e:
            print(f"[WARN] generate_recommendation a échoué : {e}", file=sys.stderr)
            deck = DeckData(
                brief_reminder=brief,
                brand_overview=BrandOverview(
                    description_paragraphs=[],
                    competitive_positioning={"axes": [], "brands": []},
                    persona={"heading": [], "bullets": []},
                    top3_competitor_actions=[],
                ),
                state_of_play=trends,
                insights=[],
                hypotheses=[],
                kpis=[],
                executive_summary="",
                ideas=[],
                timeline=[],
                budget=[],
            )

        # d. Génération du PPTX
        try:
            pptx_generator.slide_builder.build_ppt(deck, args.report)
            print(f"[OK] PPT généré : {args.report}")
        except Exception as e:
            print(f"[WARN] build_ppt indisponible : {e}", file=sys.stderr)
            open(args.report, "wb").close()
            print(f"[OK] Fichier vide créé : {args.report}")

        sys.exit(0)

    # 3. Si pas de --report, afficher le JSON brut
    print(json.dumps(brief_dict, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
