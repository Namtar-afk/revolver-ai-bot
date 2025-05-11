import os
import sys
import argparse
import tempfile

from bot.orchestrator import process_brief, run_veille, run_analyse
from utils.logger import logger

def simulate_slack_upload():
    """Simulateur CLI : parse un PDF local."""
    sample = "tests/samples/brief_sample.pdf"
    if not os.path.exists(sample):
        logger.error(f"Fichier introuvable : {sample}")
        return
    logger.info("[Slack][Sim] Lecture du sample PDF...")
    sections = process_brief(sample)
    print(f"\n=== Sections extraites (simulateur) ===\n{sections}\n")

def handle_veille_command():
    """Commande CLI/Slack pour déclencher la veille média."""
    output = os.getenv("VEILLE_OUTPUT_PATH", "data/veille.csv")
    items = run_veille(output)
    msg = f"✅ Veille lancée, {len(items)} items sauvegardés dans `{output}`."
    logger.info(msg)
    return msg

def handle_analyse_command():
    """Commande CLI/Slack pour déclencher l'analyse des items de veille."""
    try:
        run_analyse()
        return "✅ Analyse terminée, résultats envoyés."
    except Exception as e:
        logger.error(f"Erreur analyse Slack : {e}")
        return f"❌ L'analyse a échoué : {e}"

def real_slack_listener():
    """Listener Slack réel via Slack Bolt + Socket Mode."""
    try:
        from slack_bolt import App
        from slack_bolt.adapter.socket_mode import SocketModeHandler
        import requests
    except ImportError as e:
        logger.error(f"Slack Bolt non installé: {e}")
        sys.exit(1)

    SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
    SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")
    if not SLACK_BOT_TOKEN or not SLACK_APP_TOKEN:
        logger.warning("Tokens Slack manquants — passage en simulateur.")
        simulate_slack_upload()
        sys.exit(0)

    app = App(token=SLACK_BOT_TOKEN)

    @app.event("message")
    def handle_message_events(body, say, client):
        evt = body.get("event", {})
        text = evt.get("text", "").strip().lower()

        # Commande veille
        if text == "!veille":
            say(handle_veille_command())
            return

        # Commande analyse
        if text == "!analyse":
            say("🧠 Lancement de l’analyse, ça arrive…")
            say(handle_analyse_command())
            return

        # Fichier upload PDF
        for f in evt.get("files", []):
            if f.get("filetype") != "pdf":
                continue

            info = client.files_info(file=f["id"])["file"]
            url = info.get("url_private_download")
            headers = {"Authorization": f"Bearer {SLACK_BOT_TOKEN}"}

            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                resp = requests.get(url, headers=headers)
                tmp.write(resp.content)
                tmp_path = tmp.name

            try:
                sections = process_brief(tmp_path)
                say(f"✅ Brief analysé :```{sections}```")
            except Exception as e:
                logger.error(f"Erreur traitement PDF: {e}")
                say(f"❌ Échec traitement du brief : {e}")

    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Slack handler CLI / real listener")
    parser.add_argument(
        "--simulate", action="store_true",
        help="Lancer le simulateur CLI (parse un sample local)"
    )
    parser.add_argument(
        "--veille", action="store_true",
        help="Déclencher la veille média"
    )
    parser.add_argument(
        "--analyse", action="store_true",
        help="Déclencher l'analyse des items de veille"
    )
    args = parser.parse_args()

    if args.simulate:
        simulate_slack_upload()
    elif args.veille:
        print(handle_veille_command())
    elif args.analyse:
        print(handle_analyse_command())
    else:
        real_slack_listener()
