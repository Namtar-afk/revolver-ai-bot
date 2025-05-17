# bot/email_handler.py

#!/usr/bin/env python3
import os
import shutil
from pathlib import Path

from utils.logger import logger
from bot.orchestrator import process_brief

# Répertoire d’inbox (modifiable via variable d’environnement INBOX_DIR)
INBOX_DIR = os.getenv("INBOX_DIR", "inbox")

def handle_inbox():
    """
    Parcourt tous les PDFs dans INBOX_DIR, les traite via process_brief(),
    affiche les sections extraites et déplace chaque fichier en .processed.
    """
    inbox = Path(INBOX_DIR)
    if not inbox.exists() or not inbox.is_dir():
        logger.error(f"[Email] Inbox directory introuvable : {INBOX_DIR}")
        return

    for pdf_path in inbox.iterdir():
        if pdf_path.suffix.lower() != '.pdf':
            continue

        logger.info(f"[Email] Traitement du fichier : {pdf_path}")
        try:
            # Pass a Path directly so process_brief can check .is_file()
            sections = process_brief(pdf_path)
            print("-- PROBLEM --", sections.get("problem", ""))
            print("-- OBJECTIVES --", sections.get("objectives", []))
            print("-- KPIs --", sections.get("KPIs", ""))
        except Exception as e:
            logger.error(f"[Email] Erreur sur {pdf_path} : {e}")
        finally:
            processed = pdf_path.with_suffix(pdf_path.suffix + ".processed")
            shutil.move(str(pdf_path), str(processed))
            logger.info(f"[Email] Fichier déplacé en {processed}")

if __name__ == "__main__":
    handle_inbox()
