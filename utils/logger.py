import logging
import sys

# Configure the root logger for the application
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    stream=sys.stdout
)

# Create a named logger for the Revolver AI Bot
logger = logging.getLogger("revolver_ai_bot")
