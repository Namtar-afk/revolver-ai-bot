#!/usr/bin/env python3
import os
import sys
import tempfile
import requests
import subprocess

from bot.orchestrator import process_brief, run_veille, run_analyse
from utils.logger import logger

# dummy slack_app pour import/tests, strictement NO BOLT ici
class _DummyApp:
    def command(self, *args, **kwargs):
        def deco(f): return f
        return deco
    def event(self, *args, **kwargs):
        def deco(f): return f
        return deco

slack_app = _DummyApp()


def simulate_slack_upload():
    """Simulateur CLI : parse un PDF local."""
    sample = "tests/samples/brief_sample.pdf"
    if not os.path.exists(sample):
        logger.error(f"Fichier introuvable : {sample}")
        return
    logger.info("[Slack][Sim] Lecture du sample PDF…")
    sections = process_brief(sample)
    print(f"=== Simulé ===\n{sections}")


def handle_veille_command():
    """Commande CLI/Slack pour déclencher la veille média."""
    output = os.getenv("VEILLE_OUTPUT_PATH", "data/veille.csv")
    items = run_veille(output)
    return f"✅ {len(items)} items sauvegardés dans `{output}`."


def handle_analyse_command():
    """Commande CLI/Slack pour déclencher l'analyse des items de veille."""
    try:
        run_analyse()
        return "✅ Analyse terminée, résultats envoyés."
    except Exception as e:
        logger.error(f"Erreur analyse Slack : {e}")
        return f"❌ L'analyse a échoué : {e}"


def handle_report_command(ack, respond, command):
    """Commande Slack pour générer le rapport PPT."""
    ack()
    output = "report.pptx"
    subprocess.run(
        ["python", "-m", "bot.orchestrator", "--report", output],
        check=True
    )
    respond(f"📊 Rapport généré : {output}")


def real_slack_listener():
    """Listener Slack réel via Slack Bolt + Socket Mode."""
    # ⚠️ Import de Bolt **uniquement ici**
    try:
        from slack_bolt import App
        from slack_bolt.adapter.socket_mode import SocketModeHandler
        from slack_bolt.error import BoltError
    except ImportError:
        logger.error("Slack Bolt non installé — impossible de lancer le listener réel")
        sys.exit(1)

    token     = os.getenv("SLACK_BOT_TOKEN")
    app_token = os.getenv("SLACK_APP_TOKEN")
    if not token or not app_token:
        logger.warning("Tokens Slack manquants — lancement du simulateur")
        simulate_slack_upload()
        return

    try:
        app = App(token=token)
    except BoltError:
        logger.warning("Token Slack invalide — simulateur")
        simulate_slack_upload()
        return

    @app.command("/report")
    def _report(ack, respond, command):
        handle_report_command(ack, respond, command)

    @app.event("message")
    def _evt(body, say, client):
        text = body.get("event", {}).get("text", "").strip().lower()
        if text == "!veille":
            say(handle_veille_command())
        elif text == "!analyse":
            say(handle_analyse_command())
        else:
            # gestion d'upload PDF
            for f in body.get("event", {}).get("files", []):
                if f.get("filetype") != "pdf": 
                    continue
                info = client.files_info(file=f["id"])["file"]
                url = info.get("url_private_download")
                headers = {"Authorization": f"Bearer {token}"}
                with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                    tmp.write(requests.get(url, headers=headers).content)
                    path = tmp.name
                try:
                    sections = process_brief(path)
                    say(f"✅ Brief analysé :\n```{sections}```")
                except Exception as e:
                    logger.error(f"Erreur traitement PDF : {e}")
                    say(f"❌ Échec du traitement : {e}")

    SocketModeHandler(app, app_token).start()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Slack handler CLI / listener")
    parser.add_argument("--simulate", action="store_true",
                        help="Lancer le simulateur CLI (parse sample local)")
    parser.add_argument("--veille", action="store_true",
                        help="Déclencher la veille média")
    parser.add_argument("--analyse", action="store_true",
                        help="Déclencher l'analyse des items de veille")
    args = parser.parse_args()

    if args.simulate:
        simulate_slack_upload()
    elif args.veille:
        print(handle_veille_command())
    elif args.analyse:
        print(handle_analyse_command())
    else:
        real_slack_listener()
