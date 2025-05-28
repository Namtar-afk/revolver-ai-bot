#!/usr/bin/env python3
import argparse
import os
import subprocess
import sys
import tempfile
import time

import requests
from slack_sdk import WebClient

from bot.orchestrator import process_brief, run_analyse, run_veille
from utils.logger import logger

# ----------------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------------
# Initialize Slack client for file uploads and messages
client = WebClient(token=os.getenv("SLACK_BOT_TOKEN", ""))


# ----------------------------------------------------------------------------
# CLI Functions (exportable and testable)
# ----------------------------------------------------------------------------
def handle_veille_command() -> str:
    """
    Lance une veille média et retourne un message de confirmation.
    """
    output = os.getenv("VEILLE_OUTPUT_PATH", "data/veille.csv")
    try:
        items = run_veille(output)
        msg = f"✅ {len(items)} items sauvegardés dans `{output}`."
        logger.info(f"[CLI] Veille : {len(items)} items enregistrés dans {output}")
        return msg
    except Exception as e:
        logger.error(f"[CLI] Échec de la veille : {e}")
        return f"❌ Erreur veille : {e}"


def handle_analyse_command() -> str:
    """
    Lance l'analyse des items de veille et retourne un message de confirmation.
    """
    try:
        run_analyse()
        msg = "✅ Analyse terminée."
        logger.info("[CLI] Analyse terminée.")
        return msg
    except Exception as e:
        logger.error(f"[CLI] Échec de l’analyse : {e}")
        return f"❌ Erreur analyse : {e}"


def simulate_upload() -> None:
    """
    Simule l'upload d'un PDF Slack pour tester le process de brief.
    Affiche le résultat de l'analyse en CLI.
    """
    pdf_path = "tests/samples/brief_sample.pdf"
    if not os.path.exists(pdf_path):
        logger.error(f"[CLI] Fichier introuvable : {pdf_path}")
        return
    logger.info("[CLI] Simulation d'un upload PDF Slack...")
    sections = process_brief(pdf_path)
    print("\n=== Résultat de l’analyse CLI ===\n")
    print(sections)


# Alias for backward compatibility in tests
simulate_slack_upload = simulate_upload


# ----------------------------------------------------------------------------
# HTTP Slack Events Handler (FastAPI integration)
# ----------------------------------------------------------------------------
def handle_slack_event(payload: dict) -> dict:
    """
    Point d'entrée pour les événements Slack HTTP.
    - Gère l'URL Verification
    - Gère les commandes simples et l'upload de PDF
    - Retourne un dict JSON prêt à être renvoyé par FastAPI
    """
    # URL verification challenge
    if payload.get("type") == "url_verification":
        return {"challenge": payload.get("challenge")}
    # Event callback
    if payload.get("type") == "event_callback":
        event = payload.get("event", {})
        text = event.get("text", "").strip().lower()
        # Commande veille
        if text == "!veille":
            return {"text": handle_veille_command()}
        # Commande analyse
        if text == "!analyse":
            return {"text": handle_analyse_command()}
        # Fichiers PDF reçus
        for f in event.get("files", []):
            if f.get("filetype") != "pdf":
                continue
            try:
                url = f.get("url_private_download")
                headers = {
                    "Authorization": f"Bearer {os.getenv('SLACK_BOT_TOKEN', '')}"
                }
                with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                    tmp.write(requests.get(url, headers=headers).content)
                    pdf_path = tmp.name
                sections = process_brief(pdf_path)
                return {"text": f"✅ Brief analysé :\n```{sections}```"}
            except Exception as e:
                logger.error(f"[Slack] Erreur analyse PDF : {e}")
                return {"text": f"❌ Erreur analyse PDF : {e}"}
    # Accusé de réception par défaut
    return {"status": "ok"}


# ----------------------------------------------------------------------------
# Slack Bot Socket Mode (réel ou fallback CLI)
# ----------------------------------------------------------------------------
def handle_report_command(ack, respond, command) -> str:
    """
    Génère un rapport PPTX et l'envoie sur Slack.
    """
    ack()
    output = (getattr(command, "text", "") or "report.pptx").strip()
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    script_path = os.path.join(repo_root, "run_parser.py")
    output_path = os.path.abspath(output)
    logger.info(f"[Slack] Génération rapport : {script_path} → {output_path}")
    try:
        subprocess.run(
            [sys.executable, script_path, "--report", output_path], check=True
        )
    except subprocess.CalledProcessError as e:
        logger.warning(
            f"[Slack] Erreur subprocess (code {e.returncode}) → fichier vide créé"
        )
        open(output_path, "wb").close()
    try:
        client.files_upload(
            channels=getattr(command, "channel_id", "#general"),
            file=output_path,
            filename=os.path.basename(output_path),
        )
        client.chat_postMessage(
            channel=getattr(command, "channel_id", "#general"),
            text=f"📊 Rapport généré : {output_path}",
        )
    except Exception as e:
        logger.error(f"[Slack] Upload échoué : {e}")
        return f"❌ Échec de l’upload : {e}"
    return f"📊 Rapport généré : {output_path}"


def start_slack_listener():
    """
    Démarre l'écoute en Socket Mode avec Slack Bolt ou bascule en CLI.
    """
    try:
        from slack_bolt import App
        from slack_bolt.adapter.socket_mode import SocketModeHandler
    except ImportError:
        logger.error("[Slack] Slack Bolt non installé → fallback CLI")
        simulate_upload()
        sys.exit(0)
    app_token = os.getenv("SLACK_APP_TOKEN")
    bot_token = os.getenv("SLACK_BOT_TOKEN")
    if not app_token or not bot_token:
        logger.warning("[Slack] Tokens manquants → fallback CLI")
        simulate_upload()
        sys.exit(0)
    app = App(token=bot_token)

    @app.command("/report")
    def report_handler(ack, respond, command):
        respond(handle_report_command(ack, respond, command))

    @app.event("message")
    def message_handler(body, say):
        result = handle_slack_event(body)
        # Slack Bolt : renvoi direct via say si 'text' présent
        if isinstance(result, dict) and "text" in result:
            say(result["text"])

    logger.info("[Slack] SocketModeHandler démarré.")
    SocketModeHandler(app, app_token).start()


# ----------------------------------------------------------------------------
# Mode CLI principal
# ----------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Slack bot CLI")
    parser.add_argument(
        "--simulate", action="store_true", help="Simule un upload PDF Slack en CLI"
    )
    parser.add_argument("--veille", action="store_true", help="Lance la veille en CLI")
    parser.add_argument("--analyse", action="store_true", help="Lance l’analyse en CLI")
    args = parser.parse_args()

    if args.simulate:
        simulate_upload()
    elif args.veille:
        print(handle_veille_command())
    elif args.analyse:
        print(handle_analyse_command())
    else:
        start_slack_listener()


if __name__ == "__main__":
    main()
