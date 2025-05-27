# api/slack_server_signature.py

import hashlib
import hmac
import os
import time

from fastapi import Request

SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")


async def verify_slack_request(request: Request, raw_body: bytes = None) -> bool:
    """
    Vérifie la signature Slack d'une requête entrante.
    Voir : https://api.slack.com/authentication/verifying-requests-from-slack

    Args:
        request: objet `Request` FastAPI.
        raw_body: contenu brut du body, si déjà lu ailleurs.

    Returns:
        bool: True si signature valide, False sinon.
    """

    if SLACK_SIGNING_SECRET is None:
        # Signature impossible à vérifier sans secret
        print("[Slack Signature] SLACK_SIGNING_SECRET non défini.")
        return False

    timestamp = request.headers.get("X-Slack-Request-Timestamp", "")
    slack_signature = request.headers.get("X-Slack-Signature", "")

    # Protection anti-replay
    try:
        if abs(int(time.time()) - int(timestamp)) > 60 * 5:
            print("[Slack Signature] Timestamp rejeté (replay attack ?)")
            return False
    except ValueError:
        print("[Slack Signature] Timestamp invalide.")
        return False

    if raw_body is None:
        raw_body = await request.body()

    base_string = f"v0:{timestamp}:{raw_body.decode('utf-8')}"
    computed_signature = (
        "v0="
        + hmac.new(
            SLACK_SIGNING_SECRET.encode(),
            base_string.encode(),
            hashlib.sha256,
        ).hexdigest()
    )

    is_valid = hmac.compare_digest(computed_signature, slack_signature)

    if not is_valid:
        print("[Slack Signature] Signature invalide.")

    return is_valid
