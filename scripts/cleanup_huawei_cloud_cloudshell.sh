#!/usr/bin/env bash
set -euo pipefail

echo "== Cloud course cleanup on Huawei Cloud CCE =="
echo "This script deletes course Kubernetes resources only."
echo "Run it in Huawei Cloud CloudShell or any terminal whose kubectl can access cloud-course-cce."
echo

echo "Current cluster:"
kubectl config current-context || true
kubectl get nodes -o wide
echo

echo "Deleting SparkApplication resources if the CRD still exists..."
if kubectl get crd sparkapplications.sparkoperator.k8s.io >/dev/null 2>&1; then
  kubectl delete sparkapplication --all -A --ignore-not-found=true
fi
echo

echo "Deleting course namespaces..."
for ns in cloud-course monitoring ai-bonus spark-operator; do
  if kubectl get namespace "$ns" >/dev/null 2>&1; then
    echo "Deleting namespace: $ns"
    kubectl delete namespace "$ns" --wait=false
  else
    echo "Namespace already absent: $ns"
  fi
done
echo

echo "Waiting for namespaces to terminate..."
for ns in cloud-course monitoring ai-bonus spark-operator; do
  kubectl wait --for=delete "namespace/$ns" --timeout=10m 2>/dev/null || true
done
echo

echo "Remaining course-related resources:"
kubectl get ns | grep -E 'cloud-course|monitoring|ai-bonus|spark-operator' || true
kubectl get pods -A | grep -E 'cloud-course|monitoring|ai-bonus|spark|mnist|grafana|prometheus|redis|backend|frontend' || true
kubectl get svc -A | grep -E 'LoadBalancer|cloud-course|monitoring|ai-bonus|spark|grafana|prometheus|backend|frontend|redis' || true
kubectl get pvc -A || true
echo

echo "Kubernetes cleanup command finished."
echo "Important: still delete the CCE cluster/nodes, ELB, EVS disks, OBS buckets, and unused SWR images in Huawei Cloud Console to stop billing."
