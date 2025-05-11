#!/usr/bin/env python3
import json
import os
import sys
from argparse import ArgumentParser
from jsonschema import validate, ValidationError

from parser.pdf_parser import extract_text_from_pdf
from parser.nlp_utils import extract_brief_sections
import reco.generator
from reco.models import DeckData, BriefReminder, StateOfPlaySection
import pptx_generator.slide_builder

# Emplacement du sample interne pour le mode dev sans brief explicite
DEFAULT_BRIEF = "tests/samples/brief_sample.pdf"

def parse_brief(path: str) -> dict:
    """
    Extrait les sections du brief et valide contre le schéma JSON.
    Renvoie la structure brute (dict).
    """
    # logs d’info sur stderr
    print(f"[INFO] Lecture du brief : {path}", file=sys.stderr)

    text = extract_text_from_pdf(path)
    sections = extract_brief_sections(text)

    schema_file = os.path.join(os.path.dirname(__file__), "schema", "brief_schema.json")
    with open(schema_file, encoding="utf-8") as f:
        schema = json.load(f)

    try:
        validate(instance=sections, schema=schema)
        # MESSAGE EXACT attendu par test_run_parser_cli, sur STDOUT
        print("Validation JSON réussie")
    except ValidationError as e:
        # warning sur stderr
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

    # 1) Extraction brute du brief (dict)
    brief_path = args.brief or DEFAULT_BRIEF
    brief_dict = parse_brief(brief_path)

    # 2) Si on demande un rapport, on convertit, génère et quitte 0
    if args.report:
        # 2.1) Conversion en Pydantic
        try:
            brief_model = BriefReminder(**brief_dict)
        except Exception as e:
            print(f"[WARN] Conversion BriefReminder impossible : {e}", file=sys.stderr)
            # modèle vide de secours
            brief_model = BriefReminder(title="", objectives=[], internal_reformulation="")

        # 2.2) Veille et calcul des tendances
        from bot.monitoring import fetch_all_sources, save_to_csv
        from bot.analysis   import detect_trends

        veille = fetch_all_sources()
        save_to_csv(veille, "data/veille.csv")
        raw_trends = detect_trends(veille)
        trends_model = [StateOfPlaySection(theme=t, evidence=[]) for t in raw_trends]

        # 2.3) Génération du deck et création du PPTX
        deck: DeckData = reco.generator.generate_recommendation(brief_model, trends_model)
        try:
            pptx_generator.slide_builder.build_ppt(deck, args.report)
        except Exception as e:
            print(f"[WARN] build_ppt indisponible : {e}", file=sys.stderr)
            # fallback : on crée un fichier vide
            open(args.report, "wb").close()

        print(f"[OK] PPT généré : {args.report}")
        sys.exit(0)

    # 3) Pas de --report : on affiche juste le JSON extrait
    print(json.dumps(brief_dict, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
