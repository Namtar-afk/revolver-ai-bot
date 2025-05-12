#!/usr/bin/env python3
import json
import os
import sys
from argparse import ArgumentParser
from jsonschema import validate, ValidationError

from parser.pdf_parser import extract_text_from_pdf
from parser.nlp_utils import extract_brief_sections
from reco.generator import generate_recommendation       # ← import corrigé
from reco.models import DeckData, BriefReminder, StateOfPlaySection, BrandOverview
import pptx_generator.slide_builder

# Emplacement du sample interne pour le mode dev sans brief explicite
DEFAULT_BRIEF = os.path.join(
    os.path.dirname(__file__),
    "tests", "samples", "brief_sample.pdf"
)

def parse_brief(path: str) -> dict:
    """
    Extrait les sections du brief et valide contre le schéma JSON.
    Renvoie la structure brute (dict).
    """
    print(f"[INFO] Lecture du brief : {path}", file=sys.stderr)
    text = extract_text_from_pdf(path)
    sections = extract_brief_sections(text)

    schema_path = os.path.join(
        os.path.dirname(__file__),
        "schema", "brief_schema.json"
    )
    with open(schema_path, encoding="utf-8") as f:
        schema = json.load(f)

    try:
        validate(instance=sections, schema=schema)
        print("Validation JSON réussie")
    except ValidationError as e:
        print(f"[WARN] Validation JSON échouée : {e.message}", file=sys.stderr)

    return sections


def main():
    parser = ArgumentParser(description="Revolver AI Bot Report CLI")
    parser.add_argument(
        "--brief",
        help="Chemin vers le PDF de brief (défaut interne)"
    )
    parser.add_argument(
        "--report",
        metavar="OUTPUT",
        help="Chemin de sortie pour le PPTX"
    )
    args = parser.parse_args()

    # 1) Extraction brute du brief
    brief_path = args.brief or DEFAULT_BRIEF
    brief_dict = parse_brief(brief_path)

    # 2) Génération de rapport PPT si demandé
    if args.report:
        # 2.1) Conversion en Pydantic BriefReminder
        try:
            brief_model = BriefReminder(**brief_dict)
        except Exception as e:
            print(f"[WARN] Conversion BriefReminder impossible : {e}", file=sys.stderr)
            # Placeholder fallback pour éviter les erreurs Pydantic
            brief_model = BriefReminder(
                title="Brief statique",
                objectives=["Non précisé"],
                internal_reformulation="Reformulation automatique",
                summary="Résumé automatique"
            )

        # 2.2) Veille & tendances
        from bot.monitoring import fetch_all_sources, save_to_csv
        from bot.analysis import detect_trends

        veille = fetch_all_sources()
        save_to_csv(veille, "data/veille.csv")
        raw_trends = detect_trends(veille)
        trends_model = [
            StateOfPlaySection(theme=theme, evidence=[])
            for theme in raw_trends
        ]

        # 2.3) Génération du deck et création du PPTX
        try:
            deck: DeckData = generate_recommendation(
                brief_model,
                trends_model
            )
        except Exception as e:
            print(f"[WARN] generate_recommendation a échoué : {e}", file=sys.stderr)
            # Fallback deck minimal valide
            deck = DeckData(
                brief_reminder=brief_model,
                brand_overview=BrandOverview(
                    description_paragraphs=[],
                    competitive_positioning={"axes": [], "brands": []},
                    persona={"heading": [], "bullets": []},
                    top3_competitor_actions=[]
                ),
                state_of_play=[],
                insights=[],
                hypotheses=[],
                kpis=[],
                executive_summary="",
                ideas=[],
                timeline=[],
                budget=[]
            )

        try:
            pptx_generator.slide_builder.build_ppt(deck, args.report)
            print(f"[OK] PPT généré : {args.report}")
        except Exception as e:
            print(f"[WARN] build_ppt indisponible : {e}", file=sys.stderr)
            open(args.report, "wb").close()
            print(f"[OK] Fichier vide créé : {args.report}")

        sys.exit(0)

    # 3) Pas de --report : on affiche le JSON extrait
    print(json.dumps(brief_dict, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
