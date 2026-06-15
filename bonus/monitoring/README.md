# Bonus 1: Prometheus and Grafana

The deployment uses the teacher-provided
`kube-prometheus-stack-83.7.0.tgz` chart. Images are mirrored to the
`cn-north-4` SWR organization so CCE does not depend on foreign registries.

Secrets are created directly in Kubernetes:

```powershell
$env:KUBECONFIG = "D:\path\to\kubeconfig.yaml"
kubectl create namespace monitoring
kubectl create secret generic monitoring-grafana-admin -n monitoring `
  --from-literal=admin-user=admin `
  --from-literal=admin-password="<GENERATED_PASSWORD>"
```

The existing `swr-pull-secret` is copied into the monitoring namespace without
printing its contents. Install the chart with:

```powershell
helm upgrade --install monitoring <CHART_PATH> `
  -n monitoring --create-namespace `
  -f bonus/monitoring/values-cce.yaml
```

Do not commit the generated Grafana password or the rendered Secret.

