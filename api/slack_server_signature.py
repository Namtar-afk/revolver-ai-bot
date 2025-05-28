import hashlib
import hmac
import os
import time
from fastapi import Request
from utils.logger import logger

async def verify_slack_request(request: Request, raw_body: bytes = None) -> bool:
    slack_signing_secret_value = os.getenv("SLACK_SIGNING_SECRET") # Lire la variable ici

    if slack_signing_secret_value is None:
        logger.error("[Slack Signature] SLACK_SIGNING_SECRET non défini.")
        return False

    timestamp = request.headers.get("X-Slack-Request-Timestamp", "")
    slack_signature = request.headers.get("X-Slack-Signature", "")

    try:
        if abs(int(time.time()) - int(timestamp)) > 60 * 5:
            logger.warning(
                "[Slack Signature] Timestamp rejeté (replay attack ?)"
            )
            return False
    except ValueError:
        logger.warning("[Slack Signature] Timestamp invalide.")
        return False

    if raw_body is None:
        raw_body = await request.body()

    base_string = f"v0:{timestamp}:{raw_body.decode('utf-8')}"
    computed_signature = (
        "v0="
        + hmac.new(
            slack_signing_secret_value.encode(), # Utiliser la valeur lue ici
            base_string.encode(),
            hashlib.sha256,
        ).hexdigest()
    )
    is_valid = hmac.compare_digest(computed_signature, slack_signature)
    if not is_valid:
        logger.warning("[Slack Signature] Signature invalide.")
    return is_valid
