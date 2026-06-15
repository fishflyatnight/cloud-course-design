#!/usr/bin/env bash
set -euo pipefail

if [ "${1:-}" != "--yes" ]; then
  cat <<'EOF'
Cleanup preview:
  kubectl delete sparkapplications --all -n default
  kubectl delete namespace cloud-course

Run scripts/99_cleanup.sh --yes only after saving required real evidence.
This script does not delete CCE clusters, worker ECS nodes, ELB, OBS, SWR, or EVS.
EOF
  exit 0
fi

echo "Deleting SparkApplication resources in default namespace, if the CRD exists."
kubectl delete sparkapplications --all -n default --ignore-not-found || true

echo "Deleting namespace cloud-course and its namespaced resources."
kubectl delete namespace cloud-course --ignore-not-found

cat <<'EOF'

Kubernetes cleanup command completed.
Manually inspect and release billable Huawei Cloud resources:
  ELB, CCE worker nodes/ECS, EVS disks/PVs, OBS objects/buckets, and unused SWR images.
Do not assume namespace deletion releases every cloud resource immediately.
EOF

