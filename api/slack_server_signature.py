import hashlib
import hmac
import os
import time

from fastapi import Request

SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET", "")


async def verify_slack_request(request: Request, raw_body: bytes) -> bool:
    timestamp = request.headers.get("X-Slack-Request-Timestamp", "")
    slack_sig = request.headers.get("X-Slack-Signature", "")

    # Prevent replay attacks
    try:
        req_ts = float(timestamp)
    except ValueError:
        return False
    if abs(time.time() - req_ts) > 60 * 5:
        return False

    # Recompute signature based on exact raw body
    basestring = f"v0:{timestamp}:{raw_body.decode('utf-8')}"
    my_sig = (
        "v0="
        + hmac.new(
            SLACK_SIGNING_SECRET.encode(),
            basestring.encode(),
            hashlib.sha256
        ).hexdigest()
    )

    return hmac.compare_digest(my_sig, slack_sig)
