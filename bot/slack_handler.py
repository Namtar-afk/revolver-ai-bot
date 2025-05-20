#!/usr/bin/env python3
import os
import sys
import time
import tempfile
import subprocess
import argparse
import requests
import logging
from typing import Dict, Any, Optional, List

import aiohttp
from slack_sdk import WebClient

from utils.logger import logger
from bot.orchestrator import process_brief, run_veille, run_analyse

client = WebClient(token=os.getenv("SLACK_BOT_TOKEN", ""))
mock_handle_event: List[Dict[str, Any]] = []

time.sleep(0.5)  # Laisse Docker démarrer si nécessaire


# ------------------------------------------------------------------------------
# CLI Commands
# ------------------------------------------------------------------------------

def handle_veille_command() -> str:
    output = os.getenv("VEILLE_OUTPUT_PATH", "data/veille.csv")
    try:
        items = run_veille(output)
        logger.info(f"[CLI] Veille : {len(items)} items enregistrés dans {output}")
        return f"✅ {len(items)} items sauvegardés dans `{output}`."
    except Exception as e:
        logger.error(f"[CLI] Échec de la veille : {e}")
        return f"❌ Erreur veille : {e}"


def handle_analyse_command() -> str:
    try:
        run_analyse()
        return "✅ Analyse terminée."
    except Exception as e:
        logger.error(f"[CLI] Échec de l’analyse : {e}")
        return f"❌ Erreur analyse : {e}"


def simulate_upload() -> None:
    """Simulation CLI d’un upload PDF analysé par le bot."""
    pdf_path = "tests/samples/brief_sample.pdf"
    if not os.path.exists(pdf_path):
        logger.error(f"[CLI] Fichier introuvable : {pdf_path}")
        return
    logger.info("[CLI] Simulation d’un upload PDF Slack…")
    sections = process_brief(pdf_path)
    print("\n=== Résultat de l’analyse CLI ===\n")
    print(sections)


simulate_slack_upload = simulate_upload


# ------------------------------------------------------------------------------
# Slack HTTP Events (FastAPI usage)
# ------------------------------------------------------------------------------

async def handle_slack_event(event_payload: dict) -> dict:
    event = event_payload.get("event", {})
    text = event.get("text", "").strip().lower()

    if text == "!veille":
        logger.info("[Slack Event] Commande !veille reçue")
        return {"text": handle_veille_command()}

    if text == "!analyse":
        logger.info("[Slack Event] Commande !analyse reçue")
        return {"text": handle_analyse_command()}

    for f in event.get("files", []):
        if f.get("filetype") != "pdf":
            continue
        try:
            url = f["url_private_download"]
            headers = {"Authorization": f"Bearer {os.getenv('SLACK_BOT_TOKEN', '')}"}
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as resp:
                    content = await resp.read()
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                tmp.write(content)
                pdf_path = tmp.name
            sections = process_brief(pdf_path)
            logger.info(f"[Slack Event] PDF analysé : {sections}")
            return {"text": f"✅ Brief analysé :\n```{sections}```"}
        except Exception as e:
            logger.error(f"[Slack Event] Erreur analyse PDF : {e}")
            return {"text": f"❌ Erreur analyse PDF : {e}"}
        finally:
            if 'pdf_path' in locals() and os.path.exists(pdf_path):
                os.unlink(pdf_path)

    # Mode test : on garde une trace
    mock_handle_event.append(event)
    return {"ok": True}


# ------------------------------------------------------------------------------
# Slack Slash Commands & Socket Mode
# ------------------------------------------------------------------------------

def handle_report_command(ack, respond, command) -> str:
    ack()
    output = (getattr(command, "text", "") or "report.pptx").strip()
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    script_path = os.path.join(repo_root, "run_parser.py")
    output_path = os.path.abspath(output)

    logger.info(f"[Slack] Génération rapport : {script_path} → {output_path}")
    try:
        subprocess.run([sys.executable, script_path, "--report", output_path], check=True)
    except subprocess.CalledProcessError as e:
        logger.warning(f"[Slack] Erreur subprocess (code {e.returncode}) → fichier vide")
        open(output_path, "wb").close()

    try:
        client.files_upload(
            channels=getattr(command, "channel_id", "#general"),
            file=output_path,
            filename=os.path.basename(output_path),
        )
        client.chat_postMessage(
            channel=getattr(command, "channel_id", "#general"),
            text=f"📊 Rapport généré : {output_path}"
        )
    except Exception as e:
        logger.error(f"[Slack] Upload échoué : {e}")
        return f"❌ Échec de l’upload : {e}"

    return f"📊 Rapport généré : {output_path}"


def start_slack_listener():
    try:
        from slack_bolt import App
        from slack_bolt.adapter.socket_mode import SocketModeHandler
    except ImportError:
        logger.warning("[Slack] Slack Bolt manquant → fallback CLI")
        simulate_upload()
        sys.exit(0)

    app_token = os.getenv("SLACK_APP_TOKEN")
    bot_token = os.getenv("SLACK_BOT_TOKEN")

    if not app_token or not bot_token:
        logger.warning("[Slack] Tokens Slack manquants → fallback CLI")
        simulate_upload()
        sys.exit(0)

    app = App(token=bot_token)

    @app.command("/veille")
    def cmd_veille(ack, respond, command):
        ack()
        result = handle_veille_command()
        respond(result)

    @app.command("/analyse")
    def cmd_analyse(ack, respond, command):
        ack()
        respond("🧠 Lancement de l’analyse…")
        result = handle_analyse_command()
        respond(result)

    @app.event("message")
    async def message_handler(body, say):
        result = await handle_slack_event(body)
        if isinstance(result, dict) and "text" in result:
            await say(result["text"])

    logger.info("[Slack] Démarrage SocketModeHandler")
    SocketModeHandler(app, app_token).start()


# ------------------------------------------------------------------------------
# Mode CLI principal
# ------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Slack bot CLI")
    parser.add_argument("--simulate", action="store_true", help="Simule un upload PDF Slack")
    parser.add_argument("--veille", action="store_true", help="Lance la veille")
    parser.add_argument("--analyse", action="store_true", help="Lance l’analyse")
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

