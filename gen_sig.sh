#!/usr/bin/env bash
# gen_sig.sh — génère TS, SIG et BODY pour tester l’endpoint /slack/events

# 1) Récupère le timestamp actuel (secondes depuis l’Époque)
TS=$(date +%s)

# 2) Définir le payload JSON à tester.
#    Par défaut : URL verification (challenge)
BODY='{"type":"url_verification","challenge":"mon_challenge"}'

#    Pour tester un événement file_shared, décommentez la ligne suivante :
# BODY='{"type":"event_callback","event":{"type":"file_shared","file_id":"F12345678","user":"U12345678"}}'

#    Pour tester un événement message, décommentez plutôt :
# BODY='{"type":"event_callback","event":{"type":"message","text":"Hello world","user":"U12345678"}}'

# 3) Construit la base string pour la signature Slack
BASE="v0:${TS}:${BODY}"

# 4) Calcule la signature HMAC-SHA256 avec votre SLACK_SIGNING_SECRET
SIG="v0=$(printf '%s' "$BASE" \
     | openssl dgst -sha256 -hmac "${SLACK_SIGNING_SECRET}" \
     | sed 's/^.* //')"

# 5) Exporte les variables et affiche la commande curl d’exemple
export TS SIG BODY

cat <<EOF

✅ Variables générées :
  TS  = \$TS
  SIG = \$SIG
  BODY= \$BODY

Utilisez-les ainsi :

curl -X POST http://localhost:8000/slack/events \\
  -H "Content-Type: application/json" \\
  -H "X-Slack-Request-Timestamp: \$TS" \\
  -H "X-Slack-Signature: \$SIG" \\
  -d "\$BODY"

EOF

