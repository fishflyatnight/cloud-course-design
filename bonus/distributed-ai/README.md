# Bonus 3, C-1: PyTorch DDP on Kubernetes

This experiment compares a single-process MNIST CNN run with a two-worker
PyTorch DistributedDataParallel run on Huawei Cloud CCE.

The image contains the MNIST dataset so the CCE Jobs do not depend on runtime
internet access. DDP uses the CPU `gloo` backend. Rank 0 is discovered through
the `mnist-ddp-master` Service, and required pod anti-affinity places the two
rank Pods on different Worker nodes.

Build and push:

```powershell
docker build --provenance=false -f bonus/distributed-ai/Dockerfile `
  -t swr.cn-north-4.myhuaweicloud.com/cloud_course/distributed-ai:v1 `
  bonus/distributed-ai
docker push swr.cn-north-4.myhuaweicloud.com/cloud_course/distributed-ai:v1
```

Run the baseline first, then the DDP jobs:

```powershell
kubectl apply -f bonus/distributed-ai/00-namespace.yaml
kubectl apply -f bonus/distributed-ai/01-single-job.yaml
kubectl wait --for=condition=complete job/mnist-single -n ai-bonus --timeout=15m
kubectl apply -f bonus/distributed-ai/02-ddp-jobs.yaml
kubectl wait --for=condition=complete job/mnist-ddp-rank0 -n ai-bonus --timeout=15m
kubectl wait --for=condition=complete job/mnist-ddp-rank1 -n ai-bonus --timeout=15m
```

