#!/bin/bash

set -euo pipefail

USER="namtar-afk"
REPO="revolver-ai-bot"
VERSION=${1:-"v0.2.4"}
IMAGE_NAME="ghcr.io/${USER}/${REPO}:${VERSION}"

if [[ -z "${GHCR_PAT:-}" ]]; then
  echo "❌ GHCR_PAT non défini. Abandon."
  exit 1
fi

echo "🔐 Connexion à GHCR en tant que $USER..."
echo "$GHCR_PAT" | docker login ghcr.io -u "$USER" --password-stdin

echo "📦 Pousser l’image Docker : $IMAGE_NAME"
docker push "$IMAGE_NAME"

echo "✅ Publication terminée."