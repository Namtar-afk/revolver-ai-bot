#!/bin/bash
set -e  # Stoppe en cas d’erreur

echo "Lancement des tests pytest avec coverage sur bot/ ..."

pytest --cov=bot/ "$@"

