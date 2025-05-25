#!/usr/bin/env python3
import argparse
import csv
import json
import os
import sys
from pathlib import Path

# Assure-toi que ces imports correspondent bien à ta structure et tes besoins
try:
    from jsonschema import ValidationError, validate
    from parser.nlp_utils import extract_brief_sections
    from parser.pdf_parser import extract_text_from_pdf
    from bot.analysis import detect_trends, summarize_items
    from bot.monitoring import fetch_all_sources, save_to_csv
    from utils.logger import logger
except ImportError as e:
    print(f"ERREUR CRITIQUE à l'import dans orchestrator.py: {e}. Vérifiez PYTHONPATH et la structure.", file=sys.stderr)
    sys.exit(1)


def load_brief_schema() -> dict:
    """
    Charge le schéma JSON du brief depuis le dossier schema/ à la racine du projet.
    """
    try:
        # Si orchestrator.py est dans PROJECT_ROOT/bot/orchestrator.py:
        # Path(__file__).resolve().parent est PROJECT_ROOT/bot/
        # Path(__file__).resolve().parents[0] est PROJECT_ROOT/bot/
        # Path(__file__).resolve().parents[1] est PROJECT_ROOT/
        project_root = Path(__file__).resolve().parents[1]
        schema_path = project_root / "schema" / "brief_schema.json"

        if not schema_path.exists():
            logger.error(f"[orchestrator] Schéma introuvable : {schema_path}")
            logger.error(f"[orchestrator] Répertoire de travail actuel (CWD): {Path.cwd()}")
            logger.error(f"[orchestrator] Chemin de l'orchestrateur: {Path(__file__).resolve()}")
            logger.error(f"[orchestrator] Racine du projet calculée: {project_root}")
            raise FileNotFoundError(f"Schéma non trouvé: {schema_path}")
        
        return json.loads(schema_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise
    except Exception as e:
        logger.error(f"[orchestrator] Erreur lors de la lecture ou du parsing du schéma JSON : {e} pour le fichier {schema_path if 'schema_path' in locals() else 'chemin_schema_non_defini'}")
        raise


def normalize_keys(sections: dict) -> dict:
    """
    Corrige les clés alias (par exemple, Anglais → Français) pour correspondre au schéma français.
    """
    key_map = {
        "title": "titre",
        "objectives": "objectifs",
        # Ajoute d'autres mappings si extract_brief_sections retourne d'autres clés anglaises
        # qui doivent être normalisées pour le schéma français interne.
        # "problem": "problème", 
        # "kpis": "kpis", # (si la clé brute était "KPIs" par exemple)
    }
    normalized_sections = sections.copy()
    for old_key, new_key in key_map.items():
        if old_key in normalized_sections and new_key not in normalized_sections:
            normalized_sections[new_key] = normalized_sections.pop(old_key)
    return normalized_sections


def process_brief(file_path: str) -> dict:
    """
    Extrait un brief depuis un PDF, normalise les clés vers le français,
    remplit les champs obligatoires pour le schéma français et valide.
    """
    logger.info(f"[orchestrator] Lecture du fichier : {file_path}")
    text = extract_text_from_pdf(file_path)
    if not text:
        logger.error("[orchestrator] Échec extraction PDF : aucun texte retourné.")
        raise RuntimeError("Extraction PDF échouée : le document est peut-être vide ou illisible.")

    sections_raw = extract_brief_sections(text)
    if not sections_raw:
        logger.warning("[orchestrator] extract_brief_sections n'a retourné aucune section.")
        sections_raw = {}

    sections = normalize_keys(sections_raw)

    # === Remplissage des champs obligatoires (clés françaises) ===
    sections.setdefault("titre", "Brief extrait automatiquement")
    
    if not sections.get("problème") or not isinstance(sections.get("problème"), str):
        sections["problème"] = "Problème non précisé"
        
    obj = sections.get("objectifs")
    if isinstance(obj, list): # Si extract_brief_sections + normalize_keys a produit une liste
        sections["objectifs"] = "; ".join(filter(None, obj)) if any(obj) else "Objectifs non précisés"
    elif not isinstance(obj, str) or not obj.strip():
        sections["objectifs"] = "Objectifs non précisés"
        
    kpis_value = sections.get("kpis")
    if isinstance(kpis_value, list) and all(isinstance(item, str) for item in kpis_value):
        if not any(kpis_value): 
            sections["kpis"] = ["KPI non identifié"]
    elif isinstance(kpis_value, str) and kpis_value.strip() and kpis_value.lower() != "kpi non identifié":
        sections["kpis"] = [k.strip() for k in kpis_value.split(';') if k.strip()]
        if not sections["kpis"]: sections["kpis"] = ["KPI non identifié"]
    else: 
        sections["kpis"] = ["KPI non identifié"]

    # === Point 6 du Plan d'Attaque (Optionnel mais recommandé) ===
    # Ajouter setdefault pour reformulation_interne et résumé s'ils sont requis par brief_schema.json
    # ou si on veut s'assurer de leur présence.
    # sections.setdefault("reformulation_interne", "Reformulation interne non précisée.")
    # sections.setdefault("résumé", "Résumé non précisé.")
    # Si tu les ajoutes, assure-toi qu'ils sont dans les 'properties' de schema/brief_schema.json
    # et ajoute-les à 'required' si nécessaire.

    try:
        schema = load_brief_schema() 
        validate(instance=sections, schema=schema)
        logger.info("[orchestrator] Brief conforme au schéma français ✅")
    except ValidationError as ve:
        logger.warning(f"[orchestrator] Validation JSON (schéma français) partielle : {ve.message} pour l'instance {sections}")
    except FileNotFoundError:
        logger.error("[orchestrator] Impossible de valider le brief car le fichier schéma est introuvable.")
    except Exception as e: # Pour les erreurs de parsing JSON du schéma lui-même
        logger.error(f"[orchestrator] Erreur lors du chargement/validation du schéma pour process_brief: {e}")


    return sections


def run_veille(output_path: str = "data/veille.csv") -> list[dict]:
    """
    Lance la veille et sauvegarde les résultats en CSV.
    """
    logger.info(f"[veille] Lancement de la veille média…")
    # S'assurer que le dossier de sortie existe
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    items = fetch_all_sources()
    save_to_csv(items, str(output_file))
    logger.info(f"[veille] Sauvegardé {len(items)} items dans '{output_file}'")
    return items


def run_analyse(csv_path: str = None) -> None:
    """
    Analyse les résultats de veille.
    """
    default_csv = Path("data") / "veille.csv"
    path_str = csv_path or os.getenv("VEILLE_CSV_PATH", str(default_csv))
    path_obj = Path(path_str)

    logger.info(f"[analyse] Chargement des items depuis {path_obj}")

    if not path_obj.exists():
        logger.error(f"[analyse] Fichier introuvable : {path_obj}")
        # Optionnel : retourner ou lever une erreur plus spécifique pour les appelants
        print(f"Erreur: Fichier de veille {path_obj} non trouvé.", file=sys.stderr)
        return # Ou raise FileNotFoundError

    items = []
    try:
        with open(path_obj, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            items = list(reader)
    except Exception as e:
        logger.error(f"[analyse] Erreur lors de la lecture du fichier CSV {path_obj}: {e}")
        print(f"Erreur lors de la lecture du fichier CSV: {e}", file=sys.stderr)
        return


    if not items:
        logger.warning(f"[analyse] Aucun item trouvé dans {path_obj}. Analyse annulée.")
        print("Aucun item à analyser.")
        return

    summary = summarize_items(items)
    trends = detect_trends(items)

    print(summary)
    # Correction de la SyntaxError: la chaîne doit être correctement terminée.
    print("\nTendances détectées :") 
    for t in trends:
        print(f"• {t}")


def delegate_to_report(brief_path: str, output_path: str) -> None:
    """
    Appelle run_parser.py pour générer un rapport PPTX.
    """
    run_parser_script_path = Path(__file__).resolve().parents[1] / "run_parser.py"
    if not run_parser_script_path.exists():
        logger.error(f"[report] Script run_parser.py introuvable à {run_parser_script_path}")
        # Gérer l'erreur, peut-être lever une exception ou retourner un code d'erreur
        return

    logger.info(f"[report] Génération du rapport via {run_parser_script_path}")
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    effective_brief_path = brief_path if brief_path else ""

    import subprocess
    command = [
        sys.executable, 
        str(run_parser_script_path),
        "--brief",
        effective_brief_path,
        "--report",
        output_path,
    ]
    try:
        logger.info(f"[report] Exécution de la commande: {' '.join(command)}")
        # Utiliser subprocess.run pour une meilleure gestion
        process = subprocess.run(command, capture_output=True, text=True, check=False, encoding='utf-8')
        if process.returncode == 0:
            logger.info(f"[report] run_parser.py a terminé avec succès. Sortie:\n{process.stdout}")
        else:
            logger.error(f"[report] run_parser.py a échoué avec le code {process.returncode}.\nSTDERR:\n{process.stderr}\nSTDOUT:\n{process.stdout}")
    except FileNotFoundError:
        logger.error(f"[report] Impossible d'exécuter run_parser.py. Vérifiez que Python et le script sont accessibles.")
    except Exception as e:
        logger.error(f"[report] Erreur inattendue lors de la délégation à run_parser.py: {e}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Orchestrateur Revolvr AI Bot")
    parser.add_argument("--brief", help="Chemin vers un PDF de brief à traiter")
    parser.add_argument(
        "--veille",
        nargs="?", # Accepte zéro ou un argument. Si présent sans argument, utilise 'const'.
        const=str(Path("data") / "veille.csv"), 
        default=None, # Valeur si l'option --veille n'est pas du tout fournie.
        help="Lancer la veille (chemin de sortie CSV optionnel, défaut: data/veille.csv)",
    )
    parser.add_argument(
        "--analyse", 
        action="store_true", 
        help="Analyser les données de veille (utilise le chemin de --veille ou data/veille.csv)"
    )
    parser.add_argument(
        "--report", 
        metavar="OUTPUT_PPTX", 
        help="Générer un PPTX à partir d’un brief (nécessite --brief pour spécifier le PDF source, sinon le défaut de run_parser.py sera utilisé)"
    )
    args = parser.parse_args()

    try:
        if args.veille is not None: # Sera True si --veille ou --veille chemin/fichier.csv
            run_veille(args.veille) # args.veille sera le const ou le chemin fourni.

        if args.analyse:
            veille_csv_pour_analyse = args.veille if args.veille is not None else str(Path("data") / "veille.csv")
            run_analyse(veille_csv_pour_analyse)

        processed_sections = None # Initialiser au cas où --brief n'est pas fourni mais --report l'est
        if args.brief:
            processed_sections = process_brief(args.brief)
            # Optionnel: logger un extrait du brief traité
            if processed_sections:
                 logger.info(f"[orchestrator] Brief traité: {json.dumps(processed_sections, indent=2, ensure_ascii=False)[:500]}...")


        if args.report:
            # Si args.brief n'a pas été fourni, delegate_to_report passera "" ou None,
            # et run_parser.py utilisera son propre brief par défaut.
            # C'est un comportement acceptable si run_parser.py est autonome.
            if not args.brief:
                 logger.info("[orchestrator] Option --report utilisée sans --brief explicite. run_parser.py utilisera son brief par défaut.")
            delegate_to_report(args.brief, args.report) # args.brief peut être None ici

        if not any([args.brief, args.veille is not None, args.analyse, args.report]):
            logger.info("[orchestrator] Aucune action spécifiée. Utiliser --help pour voir les options.")
            parser.print_help()

    except FileNotFoundError as e:
        logger.error(f"[orchestrator] Erreur de fichier non trouvé : {e}")
        sys.exit(1)
    except RuntimeError as e:
        logger.error(f"[orchestrator] Erreur d'exécution : {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"[orchestrator] Erreur critique inattendue : {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()