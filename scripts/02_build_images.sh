#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [ -f "$ROOT_DIR/.env" ]; then
  set -a
  # shellcheck disable=SC1091
  source "$ROOT_DIR/.env"
  set +a
fi

SPARK_BASE_IMAGE="${SPARK_BASE_IMAGE:-apache/spark-py:v3.4.0}"

echo "Building with --provenance=false for Huawei Cloud SWR manifest compatibility."
docker build --provenance=false \
  -f "$ROOT_DIR/backend/Dockerfile.backend" \
  -t cloud-course-backend:local \
  "$ROOT_DIR/backend"

docker build --provenance=false \
  -f "$ROOT_DIR/frontend/Dockerfile.frontend" \
  -t cloud-course-frontend:local \
  "$ROOT_DIR/frontend"

docker build --provenance=false \
  --build-arg "SPARK_BASE_IMAGE=$SPARK_BASE_IMAGE" \
  -f "$ROOT_DIR/spark/Dockerfile.spark" \
  -t cloud-course-spark:local \
  "$ROOT_DIR"

tag_if_ready() {
  local local_image="$1"
  local target_image="${2:-}"
  if [[ -n "$target_image" && "$target_image" != \[*\] ]]; then
    docker tag "$local_image" "$target_image"
    echo "Tagged $local_image as $target_image"
  else
    echo "Skipped remote tag for $local_image because its .env placeholder is not filled."
  fi
}

tag_if_ready cloud-course-backend:local "${SWR_IMAGE_BACKEND:-}"
tag_if_ready cloud-course-frontend:local "${SWR_IMAGE_FRONTEND:-}"
tag_if_ready cloud-course-spark:local "${SWR_IMAGE_SPARK:-}"

echo "Image build commands completed. This does not prove SWR push or CCE deployment."

