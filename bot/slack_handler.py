import os
import sys
import argparse
import tempfile
from bot.orchestrator import process_brief
from utils.logger import logger

def simulate_slack_upload():
    """Simulateur CLI : parse un PDF local."""
    sample = "tests/samples/brief_sample.pdf"
    if not os.path.exists(sample):
        logger.error(f"Fichier introuvable : {sample}")
        return
    logger.info("[Slack][Sim] Lecture du sample")
    sections = process_brief(sample)
    print(f"\n=== Sections extraites (simulateur) ===\n{sections}")

def real_slack_listener():
    """Listener Slack réel via Slack Bolt + Socket Mode."""
    from slack_bolt import App
    from slack_bolt.adapter.socket_mode import SocketModeHandler
    import requests

    SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
    SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")
    if not SLACK_BOT_TOKEN or not SLACK_APP_TOKEN:
        logger.error("Tokens Slack manquants en env vars")
        sys.exit(1)

    app = App(token=SLACK_BOT_TOKEN)

    @app.event("message")
    def handle_file_shared(body, say, client):
        evt = body.get("event", {})
        for f in evt.get("files", []):
            if f.get("filetype") != "pdf":
                continue

            info = client.files_info(file=f["id"])["file"]
            url = info["url_private_download"]
            headers = {"Authorization": f"Bearer {SLACK_BOT_TOKEN}"}

            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                resp = requests.get(url, headers=headers)
                tmp.write(resp.content)
                tmp_path = tmp.name

            try:
                sections = process_brief(tmp_path)
                say(f"✅ Brief analysé :```{sections}```")
            except Exception as e:
                say(f"❌ Échec traitement : {e}")

    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--simulate", action="store_true",
        help="lancer le simulateur CLI (parse un sample local)"
    )
    args = parser.parse_args()
    if args.simulate:
        simulate_slack_upload()
    else:
        real_slack_listener()
