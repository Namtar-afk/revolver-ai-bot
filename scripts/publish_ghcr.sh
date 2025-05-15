# publish_ghcr.sh

#!/bin/bash
set -euo pipefail

USER="namtar-afk"
REPO="revolver-ai-bot"
VERSION=${1:-"v0.2.4"}

IMAGE_NAME="ghcr.io/${USER}/${REPO}:${VERSION}"
ARCHIVE_NAME="${REPO}-${VERSION}.tar.gz"

if [[ -z "${GHCR_PAT:-}" ]]; then
  read -s -p "🔑 Enter your GHCR_PAT: " GHCR_PAT
  echo
fi

echo "🔐 Logging in to GHCR as $USER..."
echo "$GHCR_PAT" | docker login ghcr.io -u "$USER" --password-stdin
