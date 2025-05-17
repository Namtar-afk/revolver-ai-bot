# Utilise une image Python 3.12 légère
FROM python:3.12-slim

# Empêche la génération de fichiers .pyc
ENV PYTHONDONTWRITEBYTECODE=1
# Affiche les logs Python en temps réel
ENV PYTHONUNBUFFERED=1

# Définit le répertoire de travail dans le conteneur
WORKDIR /app

# Installation des dépendances système nécessaires (poppler-utils pour pdf, build-essential, curl, git)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Copie des fichiers requirements en premier pour optimiser le cache Docker
COPY requirements.txt .
COPY requirements-dev.txt .

# Installation des dépendances Python
RUN pip install --upgrade pip && \
    pip uninstall -y -r requirements.txt && \
    pip uninstall -y -r requirements-dev.txt && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements-dev.txt

# Copie du code source dans le conteneur
COPY . .

# Installation en mode editable pour faciliter le dev
RUN pip install -e .

# Expose le port 8000 (celui utilisé par uvicorn)
EXPOSE 8000

# Commande par défaut pour lancer l'API FastAPI avec hot reload
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]