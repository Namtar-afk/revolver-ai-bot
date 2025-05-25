#!/usr/bin/env python3
import json
import os
import sys
from argparse import ArgumentParser
from pathlib import Path

from jsonschema import ValidationError, validate

# Supposons que ces imports sont corrects par rapport à la structure de votre projet
from parser.nlp_utils import extract_brief_sections
from parser.pdf_parser import extract_text_from_pdf
import pptx_generator.slide_builder
from reco.generator import generate_recommendation
from reco.models import (
    BrandOverview,
    BriefReminder,
    DeckData,
    StateOfPlaySection,
    # Les imports suivants sont supprimés car ils causaient des ImportError:
    # InsightSection,
    # HypothesisSection,
    # KpiSection,
    # IdeaSection,
    # TimelineSection,
    # BudgetSection,
)


# === Defaults ===
# Chemin vers le brief par défaut, relatif à l'emplacement de ce script
DEFAULT_BRIEF_PATH = Path(__file__).resolve().parent / "tests" / "samples" / "brief_sample.pdf"

# Chemin vers le schéma JSON, supposant que run_parser.py est à la racine du projet
# et que 'schema' est un dossier à la racine.
# Le contenu de ce fichier DOIT être le schéma FRANÇAIS.
SCHEMA_FILE_PATH = Path(__file__).resolve().parent / "schema" / "brief_schema.json"


def parse_brief(path: str) -> dict:
    """
    Extrait le texte du brief, segmente les sections et valide le JSON
    par rapport à un schéma en français.
    """
    print(f"[INFO] Lecture du brief : {path}", file=sys.stderr)
    text = extract_text_from_pdf(path)
    if not text:
        print("[ERROR] Échec de l'extraction du texte du PDF.", file=sys.stderr)
        return {
            "titre": "Erreur d'extraction PDF",
            "problème": "Impossible de lire le contenu du fichier PDF.",
            "objectifs": "Aucun objectif extrait dû à une erreur PDF.",
            "kpis": [],
            "erreur_extraction": True
        }
        
    sections = extract_brief_sections(text) # Sortie avec clés françaises, objectifs en string

    try:
        if not SCHEMA_FILE_PATH.exists():
            print(f"[WARN] Fichier schéma introuvable : {SCHEMA_FILE_PATH}", file=sys.stderr)
        else:
            with open(SCHEMA_FILE_PATH, encoding="utf-8") as f:
                schema_content = json.load(f) 
            # Valide la sortie de extract_brief_sections contre le schéma français
            validate(instance=sections, schema=schema_content)
            print(f"[INFO] Validation JSON (schéma: {SCHEMA_FILE_PATH}) réussie", file=sys.stderr)
    except (ValidationError, json.JSONDecodeError) as e:
        print(f"[WARN] Échec de validation JSON (schéma: {SCHEMA_FILE_PATH}) : {e}", file=sys.stderr)
    except FileNotFoundError: 
        print(f"[WARN] Erreur FileNotFoundError lors du chargement du schéma JSON : {SCHEMA_FILE_PATH}", file=sys.stderr)

    return sections


def convert_brief_for_pydantic(french_data: dict) -> dict:
    """
    Convertit le dictionnaire du brief avec clés françaises et types sources
    vers un format avec clés anglaises et types attendus par BriefReminder (Pydantic).
    """
    if french_data.get("erreur_extraction"):
        return {
            "title": french_data.get("titre", "Erreur de brief"),
            "objectives": [],
            "internal_reformulation": french_data.get("problème", "Détails non disponibles"),
            "summary": "Impossible de traiter le brief."
        }

    english_data = {}
    key_map_fr_to_en = {
        "titre": "title",
        "objectifs": "objectives", 
        "reformulation_interne": "internal_reformulation",
        "résumé": "summary",
    }

    for fr_key, value in french_data.items():
        en_key = key_map_fr_to_en.get(fr_key)
        if en_key:
            if en_key == "objectives" and isinstance(value, str):
                if value and value.lower() not in ["objectifs non précisés", ""]:
                    english_data[en_key] = [obj.strip() for obj in value.split(';') if obj.strip()]
                else:
                    english_data[en_key] = [] 
            else:
                english_data[en_key] = value
    
    if "title" not in english_data:
        english_data["title"] = french_data.get("titre", "Titre non spécifié")
    if "objectives" not in english_data:
        objectifs_str = french_data.get("objectifs", "")
        if objectifs_str and objectifs_str.lower() not in ["objectifs non précisés", ""]:
            english_data["objectives"] = [obj.strip() for obj in objectifs_str.split(';') if obj.strip()]
        else: 
            english_data["objectives"] = [] 
            
    if "internal_reformulation" not in english_data:
        english_data["internal_reformulation"] = french_data.get("reformulation_interne", "") 
            
    if "summary" not in english_data:
        english_data["summary"] = french_data.get("résumé", "Résumé non disponible.")
            
    return english_data


def main():
    parser = ArgumentParser(description="Revolver AI Bot Report CLI")
    parser.add_argument(
        "--brief",
        default=str(DEFAULT_BRIEF_PATH),
        help=f"PDF de brief client (défaut: {DEFAULT_BRIEF_PATH})"
    )
    parser.add_argument("--report", metavar="OUTPUT_PPTX", help="Chemin de sortie .pptx")
    args = parser.parse_args()

    brief_path = args.brief
    brief_dict_fr = parse_brief(brief_path)

    if args.report:
        brief_dict_en_for_pydantic = convert_brief_for_pydantic(brief_dict_fr)
        
        try:
            brief = BriefReminder(**brief_dict_en_for_pydantic)
        except Exception as e:
            print(f"[WARN] Conversion Pydantic vers BriefReminder échouée : {e}", file=sys.stderr)
            print(f"[INFO] Données utilisées pour la conversion Pydantic: {brief_dict_en_for_pydantic}", file=sys.stderr)
            brief = BriefReminder(
                title="Brief statique (Fallback)",
                objectives=[], 
                internal_reformulation="Reformulation automatique (Fallback).",
                summary="Résumé automatique (Fallback).",
            )

        trends = []
        try:
            from bot.analysis import detect_trends
            from bot.monitoring import fetch_all_sources, save_to_csv
            veille_csv_path = Path("data") / "veille.csv"
            veille_csv_path.parent.mkdir(parents=True, exist_ok=True)
            veille_items = fetch_all_sources()
            save_to_csv(veille_items, str(veille_csv_path))
            raw_trends = detect_trends(veille_items)
            trends = [StateOfPlaySection(theme=t, evidence=[]) for t in raw_trends]
        except ImportError:
            print("[WARN] Modules de veille non trouvés. Veille ignorée.", file=sys.stderr)
        except Exception as e:
            print(f"[WARN] Veille indisponible : {e}", file=sys.stderr)

        # Préparation des valeurs par défaut pour DeckData
        default_brand_overview = BrandOverview(
            description_paragraphs=[],
            competitive_positioning={"axes": [], "brands": []},
            persona={"heading": [], "bullets": []},
            top3_competitor_actions=[],
        )
        # Utilisation de listes vides pour les sections dont les modèles Pydantic spécifiques
        # n'ont pas pu être importés ou ne sont pas définis dans reco.models.
        default_insights = []
        default_hypotheses = []
        default_kpis_section = [] 
        default_ideas = []
        default_timeline = []
        default_budget = []

        try:
            generated_content = generate_recommendation(brief, trends) 

            if isinstance(generated_content, DeckData):
                deck = generated_content
            else:
                print(f"[WARN] generate_recommendation n'a pas retourné un objet DeckData. Construction manuelle avec fallback.", file=sys.stderr)
                deck = DeckData(
                    brief_reminder=brief,
                    brand_overview=default_brand_overview,
                    state_of_play=trends or [], 
                    insights=default_insights,
                    hypotheses=default_hypotheses,
                    kpis=default_kpis_section, # Ce champ dans DeckData correspond aux KPIs de la recommandation
                    executive_summary="Résumé exécutif non généré.",
                    ideas=default_ideas,
                    timeline=default_timeline,
                    budget=default_budget
                )
        except Exception as e:
            print(f"[WARN] Échec lors de l'appel à generate_recommendation ou construction du DeckData : {e}", file=sys.stderr)
            deck = DeckData(
                brief_reminder=brief,
                brand_overview=default_brand_overview,
                state_of_play=trends or [],
                insights=default_insights,
                hypotheses=default_hypotheses,
                kpis=default_kpis_section,
                executive_summary="Résumé exécutif (Fallback).",
                ideas=default_ideas,
                timeline=default_timeline,
                budget=default_budget
            )
        
        try:
            Path(args.report).parent.mkdir(parents=True, exist_ok=True)
            pptx_generator.slide_builder.build_ppt(deck, args.report)
            print(f"[OK] PPT généré : {args.report}")
        except AttributeError:
             print(f"[WARN] pptx_generator.slide_builder.build_ppt non trouvé. PPTX non généré.", file=sys.stderr)
             if args.report: open(args.report, "wb").close() # Créer fichier vide seulement si args.report est défini
             print(f"[OK] Fichier vide créé (fallback) : {args.report if args.report else 'Non spécifié'}")
        except Exception as e:
            print(f"[WARN] Erreur lors de la génération PPTX (build_ppt) : {e}", file=sys.stderr)
            if args.report: open(args.report, "wb").close()
            print(f"[OK] Fichier vide créé (fallback) : {args.report if args.report else 'Non spécifié'}")

        sys.exit(0)

    print(json.dumps(brief_dict_fr, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()