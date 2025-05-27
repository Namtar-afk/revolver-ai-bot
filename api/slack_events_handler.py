# api/slack_events_handler.py

import logging
from typing import Any

logger = logging.getLogger(__name__)


async def handle_event(event: dict[str, Any]) -> None:
    """
    Gère un événement Slack.
    Cette fonction est appelée par slack_routes lors d’un message de type "message".
    """
    logger.info(f"[handle_event] Événement Slack reçu : {event}")
    # Logique métier à implémenter ici
