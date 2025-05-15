# Utilise une image Python 3.12 légère
FROM python:3.12-slim

# Définit le répertoire de travail dans le conteneur
WORKDIR /app

# Copie des fichiers requirements en premier pour profiter du cache Docker
COPY requirements.txt .
COPY requirements-dev.txt .

# Installation des dépendances
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements-dev.txt

# Copie du reste du code source dans le conteneur
COPY . .

# Port d’exposition (modifiable selon usage serveur)
EXPOSE 8080

# Commande par défaut (modifiable si API ou Streamlit par exemple)
CMD ["python", "run_parser.py", "--help"]
