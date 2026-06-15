#!/usr/bin/env bash
set -u

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

run_check() {
  echo
  echo "\$ $*"
  "$@" || echo "[WARN] Command failed; use docs/troubleshooting.md to investigate."
}

run_check kubectl get nodes -o wide
run_check kubectl get pods -n cloud-course
run_check kubectl get svc -n cloud-course
run_check kubectl get pvc -n cloud-course
run_check kubectl get hpa -n cloud-course
run_check kubectl top nodes

