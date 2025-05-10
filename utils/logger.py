import logging

def setup_logger():
    # Création d'un logger
    logger = logging.getLogger(__name__)
    # Création d'un handler pour afficher les logs dans le terminal
    handler = logging.StreamHandler()
    # Format des messages loggés
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    # Ajouter le handler au logger
    logger.addHandler(handler)
    # Définir le niveau de log (INFO pour afficher tous les logs)
    logger.setLevel(logging.INFO)
    return logger

# Initialisation du logger
logger = setup_logger()

# Exemple d’utilisation :
# logger.info("This is an info message")

