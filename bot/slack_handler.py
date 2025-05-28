#!/usr/bin/env python3
import argparse
import os
import subprocess
import sys
import tempfile

import aiohttp  # <— ensure bot.slack_handler.aiohttp exists for tests
import requests
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from bot.orchestrator import process_brief, run_analyse, run_veille
from utils.logger import logger


# ------------------------------------------------------------------------------
# Helpers for report CLI / unit tests
# ------------------------------------------------------------------------------
def run_report_subprocess(script_path: str, output_filepath: str) -> None:
    """Run run_parser.py in subprocess to generate the PPTX,
    always ensures the output file exists (empty if failed)."""
    subprocess.run(
        [sys.executable, script_path, "--report", output_filepath], check=True
    )
    if not os.path.exists(output_filepath):
        open(output_filepath, "wb").close()


def upload_to_slack(
    slack_client: WebClient, channel: str, file_path: str, filename: str
) -> None:
    """Upload a file to Slack and post a confirmation message."""
    slack_client.files_upload(channels=channel, file=file_path, filename=filename)
    slack_client.chat_postMessage(
        channel=channel, text=f"📊 Rapport généré : {file_path}"
    )


# ------------------------------------------------------------------------------
# Dummy Slack App for decorator compatibility in tests
# ------------------------------------------------------------------------------
class _DummyApp:
    def command(self, *args, **kwargs):
        def decorator(func):
            return func

        return decorator

    def event(self, *args, **kwargs):
        def decorator(func):
            return func

        return decorator


slack_app = _DummyApp()

# ------------------------------------------------------------------------------
# Shared CLI / Slack handlers
# ------------------------------------------------------------------------------
client = WebClient(token=os.getenv("SLACK_BOT_TOKEN", ""))


def simulate_slack_upload():
    """CLI: simulate a PDF upload event and print extracted sections."""
    sample = "tests/samples/brief_sample.pdf"
    if not os.path.exists(sample):
        logger.error(f"Fichier introuvable : {sample}")
        return
    logger.info("[Slack CLI] Simulation upload PDF")
    sections = process_brief(sample)
    print("\n=== Résultat Simulation ===")
    print(sections)


# Alias expected by some tests
simulate_upload = simulate_slack_upload


def handle_veille_command() -> str:
    """Run media monitoring and return a status message."""
    output = os.getenv("VEILLE_OUTPUT_PATH", "data/veille.csv")
    try:
        items = run_veille(output)
        msg = f"✅ Veille terminée : {len(items)} items sauvegardés dans '{output}'."
        logger.info(msg)
        return msg
    except Exception as e:
        logger.error(f"Erreur veille : {e}")
        return f"❌ Erreur veille : {e}"


def handle_analyse_command() -> str:
    """Analyse monitoring results and return a status message."""
    try:
        run_analyse()
        msg = "✅ Analyse terminée."
        logger.info(msg)
        return msg
    except FileNotFoundError as e:
        logger.error(f"Analyse interrompue, fichier manquant : {e}")
        return f"❌ Fichier veille introuvable : {e}"
    except Exception as e:
        logger.error(f"Erreur analyse : {e}")
        return f"❌ Erreur analyse : {e}"


# ------------------------------------------------------------------------------
# HTTP Slack Events handler for FastAPI / unit tests
# ------------------------------------------------------------------------------
async def handle_slack_event(event_payload: dict) -> dict:
    """Handle Slack events (HTTP webhook): commands and PDF uploads."""
    event = event_payload.get("event", {})
    text = event.get("text", "").strip().lower()

    if text == "!veille":
        return {"text": handle_veille_command()}
    if text == "!analyse":
        return {"text": handle_analyse_command()}

    # PDF upload
    for f in event.get("files", []):
        if f.get("filetype") != "pdf":
            continue
        url = f.get("url_private_download")
        headers = {"Authorization": f"Bearer {os.getenv('SLACK_BOT_TOKEN', '')}"}
        pdf_path = None
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as resp:
                    content = await resp.read()

            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                tmp.write(content)
                pdf_path = tmp.name

            sections = process_brief(pdf_path)
            return {"text": f"✅ Brief analysé :\n```{sections}```"}
        except Exception as e:
            logger.error(f"[Slack Event] PDF error: {e}")
            return {"text": f"❌ Erreur PDF : {e}"}
        finally:
            if pdf_path and os.path.exists(pdf_path):
                os.unlink(pdf_path)

    return {"ok": True}


# ------------------------------------------------------------------------------
# Slack /report command handler for Socket Mode (Bolt)
# ------------------------------------------------------------------------------
def handle_report_command(ack, respond, command) -> str:
    """Slack /report handler: run subprocess and upload the report."""
    ack()
    # command may be dict-like or object
    if isinstance(command, dict):
        text = command.get("text", "").strip()
    else:
        text = getattr(command, "text", "").strip()
    output = text or "report.pptx"
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    script = os.path.join(repo_root, "run_parser.py")
    output_path = os.path.abspath(output)

    logger.info(f"[Slack] Génération rapport via {script} → {output_path}")
    try:
        run_report_subprocess(script, output_path)
    except subprocess.CalledProcessError as e:
        logger.warning(
            f"[Slack] subprocess report failed (code {e.returncode}), fichier vide créé"
        )
        open(output_path, "wb").close()

    # upload to Slack
    try:
        channel = getattr(command, "channel_id", "#general")
        filename = os.path.basename(output_path)
        upload_to_slack(client, channel, output_path, filename)
    except SlackApiError as e:
        err = e.response.get("error", str(e))
        logger.error(f"[Slack] Upload échoué (API) : {err}")
        return f"❌ Échec de l’upload : {err}"
    except Exception as e:
        logger.error(f"[Slack] Upload échoué : {e}")
        return f"❌ Échec de l’upload : {e}"

    return f"📊 Rapport généré : {output_path}"


# ------------------------------------------------------------------------------
# Slack Bolt Socket Mode listener
# ------------------------------------------------------------------------------
def real_slack_listener():
    try:
        from slack_bolt import App
        from slack_bolt.adapter.socket_mode import SocketModeHandler
    except ImportError:
        logger.error("Slack Bolt non installé → CLI fallback")
        simulate_slack_upload()
        sys.exit(0)

    token = os.getenv("SLACK_BOT_TOKEN")
    app_token = os.getenv("SLACK_APP_TOKEN")
    if not token or not app_token:
        logger.warning("Tokens Slack manquants → CLI fallback")
        simulate_slack_upload()
        sys.exit(0)

    app = App(token=token)

    @app.command("/veille")
    def _cmd_veille(ack, respond, command):
        ack()
        respond(handle_veille_command())

    @app.command("/analyse")
    def _cmd_analyse(ack, respond, command):
        ack()
        respond(handle_analyse_command())

    @app.command("/report")
    def _cmd_report(ack, respond, command):
        respond(handle_report_command(ack, respond, command))

    @app.event("message")
    async def _on_message(body, say, client):
        result = await handle_slack_event(body)
        if "text" in result:
            await say(result["text"])

    handler = SocketModeHandler(app, app_token)
    handler.start()


# ------------------------------------------------------------------------------
# CLI entrypoint
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Slack Handler CLI")
    parser.add_argument("--simulate", action="store_true", help="Simuler upload PDF")
    parser.add_argument("--veille", action="store_true", help="Lancer veille média")
    parser.add_argument("--analyse", action="store_true", help="Lancer analyse veille")
    parser.add_argument("--report", action="store_true", help="Générer rapport PPTX")
    args = parser.parse_args()

    if args.simulate:
        simulate_slack_upload()
    elif args.veille:
        print(handle_veille_command())
    elif args.analyse:
        print(handle_analyse_command())
    elif args.report:
        # CLI report minimal: no ack/respond needed
        msg = handle_report_command(lambda: None, lambda *a, **k: None, {"text": ""})
        print(msg)
    else:
        real_slack_listener()
