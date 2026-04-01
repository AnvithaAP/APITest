# GitLab Runner Setup (Shell / Docker / Kubernetes)

The framework is runner-portable by design.

## Supported executor types

- shell ✅
- docker ✅
- kubernetes ✅

## Required CI Variables

- `ADO_ORG_URL`
- `ADO_PROJECT`
- `ADO_PAT`
- `GITLAB_PRIVATE_TOKEN` (for multi-repo orchestrator)
- `AWS_REGION`

## Minimal job pattern

```yaml
api_tests:
  stage: test
  script:
    - pip install -r requirements.txt
    - python orchestrator/execution_engine.py --query "scope=api AND intent=functional" --parallel 4
```

## Portability notes

- shell: host python + toolchain required
- docker: use pinned image with dependencies baked in
- kubernetes: provide service account + kubeconfig/in-cluster auth
