#!/usr/bin/env bash
set -u

missing=0

check_command() {
  local command_name="$1"
  local install_hint="$2"
  shift 2

  if command -v "$command_name" >/dev/null 2>&1 && "$@" >/dev/null 2>&1; then
    printf '[OK] %-12s %s\n' "$command_name" "$(command -v "$command_name")"
  else
    printf '[MISSING] %-7s Tomorrow install: %s\n' "$command_name" "$install_hint"
    missing=1
  fi
}

echo "Checking local prerequisites only; this script installs nothing."
check_command docker "Docker Desktop or Docker Engine" docker --version
check_command kubectl "kubectl compatible with the CCE Kubernetes version" kubectl version --client
check_command helm "Helm client; see docs/02_environment_setup.md" helm version
check_command git "Git" git --version

if command -v docker >/dev/null 2>&1; then
  if docker compose version >/dev/null 2>&1; then
    echo "[OK] docker compose"
  else
    echo "[MISSING] Docker Compose v2 plugin"
    missing=1
  fi
fi

if command -v python3 >/dev/null 2>&1 && python3 --version >/dev/null 2>&1; then
  echo "[OK] python3      $(command -v python3)"
elif command -v python >/dev/null 2>&1 && python --version >/dev/null 2>&1; then
  echo "[OK] python       $(command -v python) (use python on this Windows environment)"
else
  echo "[MISSING] Python 3"
  missing=1
fi

echo
if [ "$missing" -eq 0 ]; then
  echo "Prerequisite command check passed. Cloud credentials and connectivity are not verified."
else
  echo "One or more tools are missing. Read docs/02_environment_setup.md tomorrow."
fi

exit "$missing"
