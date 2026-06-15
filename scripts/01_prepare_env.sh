#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="$ROOT_DIR/.env"
EXAMPLE_FILE="$ROOT_DIR/.env.example"

if [ ! -f "$ENV_FILE" ]; then
  cp "$EXAMPLE_FILE" "$ENV_FILE"
  echo "Created $ENV_FILE from .env.example."
else
  echo "$ENV_FILE already exists; it was not overwritten."
fi

cat <<'EOF'

Tomorrow, replace the placeholders in .env, especially:
  STUDENT_ID, STUDENT_NAME, REGION, SWR_ORG
  SWR_IMAGE_BACKEND, SWR_IMAGE_FRONTEND, SWR_IMAGE_SPARK
  REDIS_PASSWORD

Only fill SWR_AK/SWR_SK/SWR_LOGIN_PASSWORD when a command actually needs them.
Never commit .env, credentials, login tokens, or kubeconfig files.
EOF

