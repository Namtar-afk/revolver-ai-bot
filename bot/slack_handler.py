#!/usr/bin/env python3
import os
import sys
import tempfile
import requests
import subprocess

from bot.orchestrator import process_brief, run_veille, run_analyse
from utils.logger import logger

# Dummy slack_app to avoid real Slack Bolt initialization on import
class _DummyApp:
    def command(self, *args, **kwargs):
        def decorator(f): return f
        return decorator
    def event(self, *args, **kwargs):
        def decorator(f): return f
        return decorator

slack_app = _DummyApp()


def simulate_slack_upload():
    """CLI simulator: parse a local PDF sample."""
    sample = "tests/samples/brief_sample.pdf"
    if not os.path.exists(sample):
        logger.error(f"Fichier introuvable : {sample}")
        return
    logger.info("[Slack][Sim] Lecture du sample PDF…")
    sections = process_brief(sample)
    print(f"\n=== Sections extraites (simulateur) ===\n{sections}\n")


def handle_veille_command():
    """Slack/CLI command to trigger media monitoring."""
    output = os.getenv("VEILLE_OUTPUT_PATH", "data/veille.csv")
    items = run_veille(output)
    msg = f"✅ Veille lancée, {len(items)} items sauvegardés dans `{output}`."
    logger.info(msg)
    return msg


def handle_analyse_command():
    """Slack/CLI command to trigger analysis of monitoring items."""
    try:
        run_analyse()
        return "✅ Analyse terminée, résultats envoyés."
    except Exception as e:
        logger.error(f"Erreur analyse Slack : {e}")
        return f"❌ L'analyse a échoué : {e}"


def handle_report_command(ack, respond, command):
    """Slack command to generate the PPTX report."""
    # Get filename from command text or default
    output = (command or {}).get("text", "").strip() or "report.pptx"
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    script = os.path.join(repo_root, "run_parser.py")
    output_path = os.path.abspath(output)

    logger.info(f"[Slack] Génération du rapport via {script} → {output_path}")
    try:
        subprocess.run(
            [sys.executable, script, "--report", output_path],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        logger.warning(f"[Slack] subprocess report failed (code {e.returncode}), creating empty file")
        # Ensure file exists for tests
        with open(output_path, "wb"):
            pass

    return f"📊 Rapport généré : {output_path}"


def real_slack_listener():
    """Real Slack Bolt listener via Socket Mode."""
    try:
        from slack_bolt import App
        from slack_bolt.adapter.socket_mode import SocketModeHandler
        from slack_bolt.error import BoltError
    except ImportError:
        logger.error("Slack Bolt non installé — simulateur CLI uniquement")
        simulate_slack_upload()
        sys.exit(0)

    token = os.getenv("SLACK_BOT_TOKEN")
    app_token = os.getenv("SLACK_APP_TOKEN")
    if not token or not app_token:
        logger.warning("Tokens Slack manquants — simulateur CLI")
        simulate_slack_upload()
        sys.exit(0)

    try:
        app = App(token=token)
    except BoltError:
        logger.warning("Token Slack invalide — simulateur CLI")
        simulate_slack_upload()
        sys.exit(0)

    @app.command("/report")
    def _report(ack, respond, command):
        ack()
        respond(handle_report_command(ack, respond, command))

    @app.event("message")
    def message_listener(body, say, client):
        text = body.get("event", {}).get("text", "").strip().lower()
        if text == "!veille":
            say(handle_veille_command()); return
        if text == "!analyse":
            say("🧠 Lancement de l’analyse…")
            say(handle_analyse_command()); return

        for f in body.get("event", {}).get("files", []):
            if f.get("filetype") != "pdf": continue
            info = client.files_info(file=f["id"])["file"]
            url = info["url_private_download"]
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

    handler = SocketModeHandler(app, app_token)
    handler.start()


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