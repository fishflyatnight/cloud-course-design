# Course Design Bonus Work

This directory contains reproducible resources for the three optional tasks:

- `monitoring/`: Prometheus and Grafana on CCE.
- `cicd/`: GitHub Actions based build, SWR push, and CCE rollout.
- `distributed-ai/`: Kubernetes CPU experiment for single-process and
  two-worker PyTorch DistributedDataParallel training.

Runtime credentials are never stored here. Kubernetes pull secrets, Grafana
credentials, SWR tokens, and kubeconfig files must be supplied at runtime.

