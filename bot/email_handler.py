#!/usr/bin/env python3
import os
import shutil
from utils.logger import logger
from bot.orchestrator import process_brief

# Répertoire d’inbox (modifiable via variable d’environnement INBOX_DIR)
INBOX_DIR = os.getenv("INBOX_DIR", "inbox")

def handle_inbox():
    """
    Parcourt tous les PDFs dans INBOX_DIR, les traite via process_brief(),
    affiche les sections extraites et déplace chaque fichier en .processed.
    """
    for fname in os.listdir(INBOX_DIR):
        if not fname.lower().endswith(".pdf"):
            continue

        path = os.path.join(INBOX_DIR, fname)
        logger.info(f"[Email] Traitement du fichier : {path}")
        try:
            sections = process_brief(path)
            # Affichage CLI
            print("-- PROBLEM --", sections.get("problem", ""))
            print("-- OBJECTIVES --", sections.get("objectives", ""))
            print("-- KPIs --", sections.get("KPIs", ""))
        except Exception as e:
            logger.error(f"[Email] Erreur sur {path} : {e}")
        finally:
            # On renomme pour marquer comme traité
            processed = path + ".processed"
            shutil.move(path, processed)
            logger.info(f"[Email] Fichier déplacé en {processed}")

if __name__ == "__main__":
    handle_inbox()
