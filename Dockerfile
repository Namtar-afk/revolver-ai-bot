# Étape 1 : image de base légère avec Python 3.12
FROM python:3.12-slim

# Étape 2 : installation des dépendances système nécessaires
RUN apt-get update && apt-get install -y --no-install-recommends \
    poppler-utils \
    tesseract-ocr \
    libreoffice \
    curl \
    build-essential \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Étape 3 : création du dossier de travail
WORKDIR /app

# Étape 4 : copie du code source
COPY . .

# Étape 5 : installation des dépendances Python du projet
RUN pip install --upgrade pip && pip install .

# Étape 6 : définition de l’entrée du conteneur
ENTRYPOINT ["python", "run_parser.py"]
