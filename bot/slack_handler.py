#!/usr/bin/env python3
import os
import sys
import tempfile
import subprocess
import argparse
import requests
import time

from slack_sdk import WebClient
from bot.utils.logger import logger
from bot.orchestrator import process_brief, run_veille, run_analyse

time.sleep(0.5)

client = WebClient(token=os.getenv("SLACK_BOT_TOKEN", ""))

# ------------------------------------------------------------------------------
# Fonctions CLI exportables (utilisables aussi dans les tests)
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
    pdf_path = "tests/samples/brief_sample.pdf"
    if not os.path.exists(pdf_path):
        logger.error(f"[CLI] Fichier introuvable : {pdf_path}")
        return
    logger.info("[CLI] Simulation d'un upload PDF Slack...")
    sections = process_brief(pdf_path)
    print("\n=== Résultat de l’analyse CLI ===\n")
    print(sections)

# ------------------------------------------------------------------------------
# Slack Handlers
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
        logger.warning(f"[Slack] Erreur subprocess (code {e.returncode}) → fichier vide créé")
        with open(output_path, "wb"):
            pass

    try:
        client.files_upload(
            channels=command.channel_id if hasattr(command, "channel_id") else "#general",
            file=output_path,
            filename=os.path.basename(output_path)
        )
        client.chat_postMessage(
            channel=command.channel_id if hasattr(command, "channel_id") else "#general",
            text=f"📊 Rapport généré : {output_path}"
        )
    except Exception as e:
        logger.error(f"[Slack] Upload échoué : {e}")
        return f"❌ Échec de l’upload : {e}"

    return f"📊 Rapport généré : {output_path}"

# ------------------------------------------------------------------------------
# Slack Socket Mode
# ------------------------------------------------------------------------------

def start_slack_listener():
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
        event = body.get("event", {})
        text = event.get("text", "").strip().lower()

        if text == "!veille":
            say(handle_veille_command())
        elif text == "!analyse":
            say("🧠 Lancement de l’analyse...")
            say(handle_analyse_command())
        else:
            for f in event.get("files", []):
                if f.get("filetype") != "pdf":
                    continue
                try:
                    url = f.get("url_private_download")
                    headers = {"Authorization": f"Bearer {bot_token}"}
                    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                        tmp.write(requests.get(url, headers=headers).content)
                        pdf_path = tmp.name
                    sections = process_brief(pdf_path)
                    say(f"✅ Brief analysé :\n```{sections}```")
                except Exception as e:
                    logger.error(f"[Slack] Erreur PDF : {e}")
                    say(f"❌ Erreur analyse PDF : {e}")

    logger.info("[Slack] SocketModeHandler démarré.")
    SocketModeHandler(app, app_token).start()

# ------------------------------------------------------------------------------
# Mode CLI
# ------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--simulate", action="store_true")
    parser.add_argument("--veille", action="store_true")
    parser.add_argument("--analyse", action="store_true")
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
