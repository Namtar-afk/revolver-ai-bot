#!/usr/bin/env python3
import argparse
import csv
import json
import os
import sys
from pathlib import Path

try:
    from jsonschema import ValidationError, validate
    from parser.nlp_utils import extract_brief_sections
    from parser.pdf_parser import extract_text_from_pdf
    from bot.analysis import detect_trends, summarize_items
    from bot.monitoring import fetch_all_sources, save_to_csv
    from utils.logger import logger
except ImportError as e:
    error_message = (
        f"ERREUR CRITIQUE à l'import dans orchestrator.py: {e}. "
        "Vérifiez PYTHONPATH et la structure."
    )
    print(error_message, file=sys.stderr)
    sys.exit(1)


def load_brief_schema() -> dict:
    try:
        project_root = Path(__file__).resolve().parents[1]
        schema_path = project_root / "schema" / "brief_schema.json"
        if not schema_path.exists():
            logger.error(f"[orchestrator] Schéma introuvable : {schema_path}")
            logger.error(f"[orchestrator] CWD: {Path.cwd()}")
            logger.error(
                f"[orchestrator] Path orchestrateur: "
                f"{Path(__file__).resolve()}"
            )
            logger.error(f"[orchestrator] Racine projet: {project_root}")
            raise FileNotFoundError(f"Schéma non trouvé: {schema_path}")
        return json.loads(schema_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise
    except Exception as e:
        schema_f = schema_path if "schema_path" in locals() else "non défini"
        log_msg = (
            "[orchestrator] Erreur lecture/parsing schéma JSON : "
            f"{e} pour {schema_f}"
        )
        logger.error(log_msg)
        raise


def normalize_keys(sections: dict) -> dict:
    if not isinstance(sections, dict):
        raise RuntimeError("normalize_keys: sections doit être un dictionnaire")
    key_map = {"title": "titre", "objectives": "objectifs"}
    normalized_sections = sections.copy()
    for old_key, new_key in key_map.items():
        if old_key in normalized_sections and new_key not in normalized_sections:
            normalized_sections[new_key] = normalized_sections.pop(old_key)
    return normalized_sections


def process_brief(file_path: str) -> dict:
    logger.info(f"[orchestrator] Lecture du fichier : {file_path}")
    text = extract_text_from_pdf(file_path)
    if not text:
        logger.error("[orchestrator] Échec extraction PDF : aucun texte.")
        msg = "Extraction PDF échouée : document vide ou illisible."
        raise RuntimeError(msg)
    sections_raw = extract_brief_sections(text)
    if not sections_raw:
        msg = (
            "[orchestrator] extract_brief_sections n'a retourné aucune "
            "section."
        )
        logger.warning(msg)
        sections_raw = {}
    sections = normalize_keys(sections_raw)
    sections.setdefault("titre", "Brief extrait automatiquement")
    if not sections.get("problème") or not isinstance(
        sections.get("problème"), str
    ):
        sections["problème"] = "Problème non précisé"
    obj = sections.get("objectifs")
    if isinstance(obj, list):
        obj_text = "; ".join(filter(None, obj))
        sections["objectifs"] = (
            obj_text if any(obj) else "Objectifs non précisés"
        )
    elif not isinstance(obj, str) or not obj.strip():
        sections["objectifs"] = "Objectifs non précisés"
    kpis_value = sections.get("kpis")
    if isinstance(kpis_value, list) and all(
        isinstance(item, str) for item in kpis_value
    ):
        if not any(kpis_value):
            sections["kpis"] = ["KPI non identifié"]
    elif (
        isinstance(kpis_value, str)
        and kpis_value.strip()
        and kpis_value.lower() != "kpi non identifié"
    ):
        kpi_list = [k.strip() for k in kpis_value.split(";") if k.strip()]
        sections["kpis"] = kpi_list if kpi_list else ["KPI non identifié"]
    else:
        sections["kpis"] = ["KPI non identifié"]
    try:
        schema = load_brief_schema()
        validate(instance=sections, schema=schema)
        logger.info("[orchestrator] Brief conforme au schéma français ✅")
    except ValidationError as ve:
        instance_str = str(sections)[:150]
        val_err_msg = (
            f"[orchestrator] Validation JSON (fr) partielle : {ve.message} "
            f"pour instance {instance_str}..."
        )
        logger.warning(val_err_msg)
    except FileNotFoundError:
        err_fnf = "[orchestrator] Val. impossible: fichier schéma introuvable."
        logger.error(err_fnf)
    except Exception as e:
        err_load = ("[orchestrator] Err. chargement/val. "
                    f"schéma process_brief: {e}")
        logger.error(err_load)
    return sections


def run_veille(output_path: str = "data/veille.csv") -> list[dict]:
    logger.info("[veille] Lancement de la veille média…")
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    items = fetch_all_sources()
    save_to_csv(items, str(output_file))
    log_msg = f"[veille] Sauvegardé {len(items)} items dans '{output_file}'"
    logger.info(log_msg)
    return items


def run_analyse(csv_path: str = None) -> None:
    default_csv = Path("data") / "veille.csv"
    path_str = csv_path or os.getenv("VEILLE_CSV_PATH", str(default_csv))
    path_obj = Path(path_str)
    logger.info(f"[analyse] Chargement des items depuis {path_obj}")
    if not path_obj.exists():
        logger.error(f"[analyse] Fichier introuvable : {path_obj}")
        print(
            f"Erreur: Fichier veille {path_obj} non trouvé.", file=sys.stderr
        )
        return
    items = []
    try:
        with open(path_obj, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            items = list(reader)
    except Exception as e:
        logger.error(f"[analyse] Erreur lecture CSV {path_obj}: {e}")
        print(f"Erreur lecture CSV: {e}", file=sys.stderr)
        return
    if not items:
        warn_msg = f"[analyse] Aucun item {path_obj}. Analyse annulée."
        logger.warning(warn_msg)
        print("Aucun item à analyser.")
        return
    summary = summarize_items(items)
    trends = detect_trends(items)
    print(summary)
    print("\nTendances détectées :")
    for t in trends:
        print(f"• {t}")


def delegate_to_report(brief_path: str, output_path: str) -> None:
    project_root = Path(__file__).resolve().parents[1]
    run_parser_script = project_root / "run_parser.py"
    if not run_parser_script.exists():
        err_msg = (
            f"[report] Script run_parser.py introuvable: {run_parser_script}"
        )
        logger.error(err_msg)
        return
    logger.info(f"[report] Génération rapport via {run_parser_script}")
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    eff_brief_path = brief_path if brief_path else ""
    import subprocess
    command = [
        sys.executable,
        str(run_parser_script),
        "--brief",
        eff_brief_path,
        "--report",
        output_path,
    ]
    try:
        cmd_str = " ".join(f"'{c}'" if " " in c else c for c in command)
        logger.info(f"[report] Exécution: {cmd_str}")
        process = subprocess.run(
            command, capture_output=True, text=True, check=False,
            encoding="utf-8"
        )
        if process.returncode == 0:
            log_stdout = process.stdout
            log_msg_stdout = (
                log_stdout[:400] + "..." if len(log_stdout) > 400
                else log_stdout
            )
            log_msg_parts = [
                "[report] run_parser.py succès. Sortie:\n", log_msg_stdout
            ]
            logger.info("".join(log_msg_parts))
        else:
            err_log_parts = [
                f"[report] run_parser.py échec code {process.returncode}.\n",
                f"STDERR:\n{process.stderr}\nSTDOUT:\n{process.stdout}",
            ]
            logger.error("".join(err_log_parts))
    except FileNotFoundError:
        err_fnf_delegate = (
            "[report] Exécution run_parser.py impossible. "
            "Python/script accessible?"
        )
        logger.error(err_fnf_delegate)
    except Exception as e:
        logger.error(f"[report] Erreur délégation run_parser.py: {e}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Orchestrateur Revolvr AI Bot")
    parser.add_argument(
        "--brief", help="Chemin vers un PDF de brief à traiter")
    default_veille_path = str(Path("data") / "veille.csv")
    help_veille = (
        f"Lancer veille (sortie CSV optionnelle, "
        f"défaut: {default_veille_path})"
    )
    parser.add_argument(
        "--veille",
        nargs="?",
        const=default_veille_path,
        default=None,
        help=help_veille,
    )
    help_analyse = (
        "Analyser données veille (utilise chemin --veille ou data/veille.csv)"
    )
    parser.add_argument("--analyse", action="store_true", help=help_analyse)
    help_report = (
        "Générer PPTX (nécessite --brief, sinon défaut de run_parser.py)"
    )
    parser.add_argument(
        "--report", metavar="OUTPUT_PPTX", help=help_report
    )
    args = parser.parse_args()
    try:
        if args.veille is not None:
            run_veille(args.veille)
        if args.analyse:
            veille_csv = args.veille or default_veille_path
            run_analyse(veille_csv)
        processed_sections = None
        if args.brief:
            processed_sections = process_brief(args.brief)
            if processed_sections:
                log_brief_json = json.dumps(
                    processed_sections, indent=2, ensure_ascii=False
                )
                log_msg_parts = [
                    "[orchestrator] Brief traité: ",
                    log_brief_json[:350] + "...",
                ]
                logger.info("".join(log_msg_parts))
        if args.report:
            if not args.brief:
                msg = (
                    "[orchestrator] --report sans --brief. "
                    "run_parser.py utilisera son brief par défaut."
                )
                logger.info(msg)
            delegate_to_report(args.brief, args.report)
        if not any(
            [args.brief, args.veille is not None, args.analyse, args.report]
        ):
            log_msg_no_action = (
                "[orchestrator] Aucune action. Utiliser --help pour options."
            )
            logger.info(log_msg_no_action)
            parser.print_help()
    except FileNotFoundError as e:
        logger.error(f"[orchestrator] Fichier non trouvé : {e}")
        sys.exit(1)
    except RuntimeError as e:
        logger.error(f"[orchestrator] Erreur d'exécution : {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"[orchestrator] Erreur critique : {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
