#!/usr/bin/env python3
import json
import os
import sys
from argparse import ArgumentParser
from parser.nlp_utils import extract_brief_sections
from parser.pdf_parser import extract_text_from_pdf

from jsonschema import ValidationError, validate

import pptx_generator.slide_builder
from reco.generator import generate_recommendation
from reco.models import (BrandOverview, BriefReminder, DeckData,
                         StateOfPlaySection)

# === Defaults ===
DEFAULT_BRIEF = os.path.join(
    os.path.dirname(__file__), "tests", "samples", "brief_sample.pdf"
)

SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema", "brief_schema.json")


def parse_brief(path: str) -> dict:
    """
    Extrait le texte du brief, segmente les sections et valide le JSON.
    """
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


def main():
    parser = ArgumentParser(description="Revolver AI Bot Report CLI")
    parser.add_argument("--brief", help="PDF de brief client")
    parser.add_argument("--report", metavar="OUTPUT", help="Chemin de sortie .pptx")
    args = parser.parse_args()

    # 1. Chargement du brief
    brief_path = args.brief or DEFAULT_BRIEF
    brief_dict = parse_brief(brief_path)

    # 2. Mode rapport
    if args.report:
        # a. Conversion dict → BriefReminder (Pydantic)
        try:
            brief = BriefReminder(**brief_dict)
        except Exception as e:
            print(f"[WARN] Conversion Pydantic échouée : {e}", file=sys.stderr)
            brief = BriefReminder(
                title="Brief statique",
                objectives=["Objectif générique"],
                internal_reformulation="Reformulation automatique du problème.",
                summary="Résumé automatique de la situation.",
            )

        # b. Veille
        try:
            from bot.analysis import detect_trends
            from bot.monitoring import fetch_all_sources, save_to_csv

            veille = fetch_all_sources()
            save_to_csv(veille, "data/veille.csv")
            raw_trends = detect_trends(veille)
            trends = [StateOfPlaySection(theme=t, evidence=[]) for t in raw_trends]
        except Exception as e:
            print(f"[WARN] Veille indisponible : {e}", file=sys.stderr)
            trends = []

        # c. Génération Deck
        try:
            deck: DeckData = generate_recommendation(brief, trends)
        except Exception as e:
            print(f"[WARN] Échec de génération du deck : {e}", file=sys.stderr)
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

        # d. Export PPTX
        try:
            pptx_generator.slide_builder.build_ppt(deck, args.report)
            print(f"[OK] PPT généré : {args.report}")
        except Exception as e:
            print(f"[WARN] build_ppt indisponible : {e}", file=sys.stderr)
            open(args.report, "wb").close()
            print(f"[OK] Fichier vide créé : {args.report}")

        sys.exit(0)

    # 3. Si pas de --report, affichage du JSON brut
    print(json.dumps(brief_dict, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
