#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="$ROOT_DIR/.env"

if [ ! -f "$ENV_FILE" ]; then
  echo "Missing .env. Run scripts/01_prepare_env.sh first." >&2
  exit 1
fi

set -a
# shellcheck disable=SC1091
source "$ENV_FILE"
set +a

require_real_value() {
  local name="$1"
  local value="${!name:-}"
  if [[ -z "$value" || "$value" == \[*\] ]]; then
    echo "Fill $name in .env before pushing." >&2
    exit 1
  fi
}

require_real_value REGION
require_real_value SWR_ORG
require_real_value SWR_AK
require_real_value SWR_IMAGE_BACKEND
require_real_value SWR_IMAGE_FRONTEND
require_real_value SWR_IMAGE_SPARK

login_password="${SWR_LOGIN_PASSWORD:-}"
if [[ -z "$login_password" || "$login_password" == \[*\] ]]; then
  login_password="${SWR_SK:-}"
fi
if [[ -z "$login_password" || "$login_password" == \[*\] ]]; then
  echo "Fill SWR_LOGIN_PASSWORD with the current SWR login token." >&2
  echo "Do not assume the IAM permanent SK is accepted as an SWR login password." >&2
  exit 1
fi

registry="swr.${REGION}.myhuaweicloud.com"
echo "Confirm that the SWR login password or temporary token is current before continuing."
echo "Logging in to $registry as ${REGION}@<AK hidden>."
printf '%s' "$login_password" |
  docker login --username "${REGION}@${SWR_AK}" --password-stdin "$registry"

docker tag cloud-course-backend:local "$SWR_IMAGE_BACKEND"
docker tag cloud-course-frontend:local "$SWR_IMAGE_FRONTEND"
docker tag cloud-course-spark:local "$SWR_IMAGE_SPARK"

docker push "$SWR_IMAGE_BACKEND"
docker push "$SWR_IMAGE_FRONTEND"
docker push "$SWR_IMAGE_SPARK"

echo "Push commands completed. Verify image names and tags in the SWR console."

