import os
import tempfile
from pathlib import Path
from typing import Any

from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.errors import SlackApiError

from utils.logger import logger
import bot.orchestrator

try:
    slack_client = AsyncWebClient(token=os.environ["SLACK_BOT_TOKEN"])
except KeyError:
    logger.error(
        "SLACK_BOT_TOKEN non défini. Client Slack non initialisé."
    )
    slack_client = None

async def download_slack_file_simplified(
    file_info: dict, download_dir: Path
) -> Path | None:
    file_id = file_info.get("id")
    file_name = file_info.get("name", "downloaded_brief.pdf")
    download_url = file_info.get("url_private_download")

    if not all([file_id, download_url, slack_client]):
        logger.error(
            f"Infos fichier manquantes ou client Slack non initialisé "
            f"pour file_id: {file_id}"
        )
        return None
    try:
        logger.info(
            f"Tentative de téléchargement (simulé) du fichier Slack : "
            f"{file_name} (ID: {file_id})"
        )
        temp_file_path = download_dir / f"{file_id}_{file_name}"
        with open(temp_file_path, "w") as f:
            f.write(f"Contenu simulé pour {file_name} depuis {download_url}")
        logger.info(
            f"Téléchargement simulé du fichier {file_name} vers {temp_file_path}"
        )
        return temp_file_path
    except SlackApiError as e:
        logger.error(
            f"Erreur API Slack téléchargement fichier {file_id}: "
            f"{e.response['error']}"
        )
        return None
    except Exception as e:
        logger.error(
            f"Erreur inattendue téléchargement fichier {file_id}: {e}"
        )
        return None

async def send_slack_message(
    channel_id: str, text: str, thread_ts: str = None
):
    if not slack_client:
        logger.error("Client Slack non initialisé. Envoi message impossible.")
        return
    try:
        await slack_client.chat_postMessage(
            channel=channel_id, text=text, thread_ts=thread_ts
        )
        logger.info(f"Message envoyé au canal {channel_id}")
    except SlackApiError as e:
        logger.error(
            f"Erreur API Slack envoi message à {channel_id}: "
            f"{e.response['error']}"
        )
    except Exception as e:
        logger.error(
            f"Erreur inattendue envoi message à {channel_id}: {e}"
        )

async def handle_event(event_data: dict[str, Any]) -> None:
    event_type = event_data.get("type")
    logger.info(f"[handle_event] Événement Slack reçu : {event_type}")
    if event_type == "message":
        files = event_data.get("files")
        channel_id = event_data.get("channel")
        user_id = event_data.get("user")
        thread_ts = event_data.get("ts")
        if files and channel_id and user_id:
            for file_info in files:
                filetype = file_info.get("filetype", "").lower()
                mimetype = file_info.get("mimetype", "").lower()
                if filetype == "pdf" or "application/pdf" in mimetype:
                    f_name = file_info.get('name')
                    log_msg = (
                        f"Fichier PDF détecté : {f_name} "
                        f"dans {channel_id} par {user_id}."
                    )
                    logger.info(log_msg)
                    ack_msg = (
                        f"Merci <@{user_id}> ! Brief PDF '{f_name}' reçu. "
                        "Analyse en cours..."
                    )
                    await send_slack_message(
                        channel_id, ack_msg, thread_ts=thread_ts
                    )
                    temp_dir = Path(tempfile.gettempdir()) / "slack_briefs"
                    temp_dir.mkdir(parents=True, exist_ok=True)
                    local_file_path = await download_slack_file_simplified(
                        file_info, temp_dir
                    )
                    if local_file_path and local_file_path.exists():
                        try:
                            logger.info(
                                "Lancement workflow stratégique pour "
                                f"{local_file_path}"
                            )
                            await bot.orchestrator.generate_full_strategic_deck(
                                str(local_file_path),
                                channel_id,
                                user_id,
                                thread_ts,
                            )
                            logger.info(
                                "Workflow stratégique terminé pour "
                                f"{local_file_path}."
                            )
                        except Exception as e:
                            err_msg = (
                                "Erreur exécution workflow stratégique pour "
                                f"{local_file_path}: {e}"
                            )
                            logger.error(err_msg, exc_info=True)
                            await send_slack_message(
                                channel_id,
                                "Désolé, erreur traitement de votre brief.",
                                thread_ts=thread_ts,
                            )
                        finally:
                            if local_file_path.exists():
                                try:
                                    os.remove(local_file_path)
                                    logger.info(
                                        f"Fichier temp {local_file_path} supprimé."
                                    )
                                except OSError as e_rm:
                                    logger.error(
                                        f"Erreur suppression fichier temp "
                                        f"{local_file_path}: {e_rm}"
                                    )
                    else:
                        f_name_err = file_info.get('name')
                        logger.error(
                            "Échec téléchargement ou fichier non trouvé "
                            f"pour {f_name_err}."
                        )
                        await send_slack_message(
                            channel_id,
                            "Désolé, impossible de récupérer le PDF.",
                            thread_ts=thread_ts
                        )
                    break
    else:
        logger.info(f"Événement type '{event_type}' non traité par handle_event.")
