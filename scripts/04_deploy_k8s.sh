#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [ -f "$ROOT_DIR/.env" ]; then
  set -a
  # shellcheck disable=SC1091
  source "$ROOT_DIR/.env"
  set +a
fi

if [[ -n "${KUBECONFIG_PATH:-}" && "${KUBECONFIG_PATH}" != \[*\] ]]; then
  export KUBECONFIG="$KUBECONFIG_PATH"
fi

if grep -R -E '\[SWR_IMAGE_(BACKEND|FRONTEND)\]' "$ROOT_DIR/k8s" >/dev/null 2>&1; then
  echo "Kubernetes YAML still contains SWR image placeholders." >&2
  echo "Replace them with real image addresses before deployment." >&2
  exit 1
fi

echo "This script does not create a CCE cluster. It deploys to the current kubectl context."
kubectl config current-context

for manifest in "$ROOT_DIR"/k8s/*.yaml; do
  echo "Applying $(basename "$manifest")"
  kubectl apply -f "$manifest"
done

echo "Kubernetes manifests were submitted. Run scripts/05_verify_k8s.sh next."
