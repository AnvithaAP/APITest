# Kubernetes Cluster Setup Guide

## 1) Namespace + RBAC

```bash
kubectl create namespace qa
kubectl create namespace perf
kubectl auth can-i create jobs -n qa
```

Grant permissions for Jobs/Pods (`create`, `get`, `list`, `watch`, `delete`) to the service account used by runners.

## 2) Runtime image

- Build and push the image containing framework dependencies.
- Configure image pull secret for private registries.

## 3) Verify runner wiring

```bash
python infra/k8s/k8s_runner.py \
  --job-name api-tests-smoke \
  --image your-registry/api-tests:latest \
  --namespace qa \
  --parallelism 2 \
  --completions 2 \
  --cmd pytest -q
```

## 4) Distributed orchestration

`runners/distributed_runner.py` can generate and submit node-specific job specs for parallel scaling.
