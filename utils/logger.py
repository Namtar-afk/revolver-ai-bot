import logging
import sys

# create module‐level logger
logger = logging.getLogger("revolver_ai_bot")
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)
handler.setFormatter(formatter)

# Avoid adding multiple handlers if module gets re-imported
if not logger.handlers:
    logger.addHandler(handler)
