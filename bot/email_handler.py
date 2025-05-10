import os
import glob
from bot.orchestrator import process_brief
from utils.logger import logger

INBOX_DIR = "inbox"

def handle_inbox():
    """
    Parcourt tous les PDFs du dossier inbox/ et les traite.
    """
    pdf_paths = glob.glob(os.path.join(INBOX_DIR, "*.pdf"))
    if not pdf_paths:
        logger.warning(f"Aucun PDF trouvé dans '{INBOX_DIR}/'")
        return

    for path in pdf_paths:
        try:
            logger.info(f"[Email] Traitement du fichier : {path}")
            sections = process_brief(path)
            # Affichage minimal pour la CLI
            print(f"\n=== Résultat pour {os.path.basename(path)} ===")
            for k, v in sections.items():
                print(f"\n-- {k.upper()} --\n{v}")
        except Exception as e:
            logger.error(f"[Email] Erreur sur {path} : {e}")

if __name__ == "__main__":
    handle_inbox()
