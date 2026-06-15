#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-preview}"
NAMESPACE="cloud-course"

show_commands() {
  cat <<'EOF'
# Step 1: find the Redis Pod.
REDIS_POD=$(kubectl get pod -n cloud-course -l app=redis -o jsonpath='{.items[0].metadata.name}')

# Step 2: write testkey. Screenshot this result later.
kubectl exec -n cloud-course "$REDIS_POD" -- sh -c \
  'redis-cli -a "$REDIS_PASSWORD" SET testkey hello'

# Step 3: delete the Pod. Screenshot the deletion/recreation later.
kubectl delete pod -n cloud-course "$REDIS_POD"
kubectl wait --for=condition=Ready pod -n cloud-course -l app=redis --timeout=180s

# Step 4: read testkey from the replacement Pod. Screenshot this result later.
NEW_REDIS_POD=$(kubectl get pod -n cloud-course -l app=redis -o jsonpath='{.items[0].metadata.name}')
kubectl exec -n cloud-course "$NEW_REDIS_POD" -- sh -c \
  'redis-cli -a "$REDIS_PASSWORD" GET testkey'
EOF
}

if [ "$MODE" != "--execute" ]; then
  echo "Preview mode only. Run with --execute when PVC is Bound and screenshots are ready."
  echo
  show_commands
  exit 0
fi

REDIS_POD="$(kubectl get pod -n "$NAMESPACE" -l app=redis -o jsonpath='{.items[0].metadata.name}')"
echo "Step 1/3: writing testkey to $REDIS_POD."
kubectl exec -n "$NAMESPACE" "$REDIS_POD" -- sh -c \
  'redis-cli -a "$REDIS_PASSWORD" SET testkey hello'
read -r -p "Screenshot point: SET result. Press Enter to delete the Redis Pod..."

kubectl delete pod -n "$NAMESPACE" "$REDIS_POD"
echo "Screenshot point: Pod deletion and recreation."
kubectl wait --for=condition=Ready pod -n "$NAMESPACE" -l app=redis --timeout=180s
read -r -p "Redis replacement Pod is Ready. Press Enter to read testkey..."

NEW_REDIS_POD="$(kubectl get pod -n "$NAMESPACE" -l app=redis -o jsonpath='{.items[0].metadata.name}')"
kubectl exec -n "$NAMESPACE" "$NEW_REDIS_POD" -- sh -c \
  'redis-cli -a "$REDIS_PASSWORD" GET testkey'
echo "Screenshot point: GET result. Treat only the actual command output as evidence."

