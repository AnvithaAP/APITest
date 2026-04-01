# Enterprise API Testing Framework

A production-oriented quality platform with **tag intelligence**, **distributed execution**, **orchestration**, **aggregation/reporting**, **history/trends**, and a **FastAPI-backed dashboard**.

## Capability Map
- 🧪 **Test Layer**: Functional + Performance + Governance modules with structured tags (`scope`, `intent`, `concern`, `type`, `module`).
- 🧠 **Tag Intelligence**: Query parser, UI-selection mapping, inheritance rules, and query-string generation ready for AND/OR expansion.
- ⚙️ **Execution Layer**: Local execution plus distributed runner that emits Kubernetes Job specs and can submit pod-based jobs.
- ☸️ **Kubernetes Real Wiring**: `infra/k8s/k8s_runner.py` applies real Job manifests using `kubectl apply` for cluster-native parallel execution.
- 🌐 **Orchestration Layer**: Multi-repo GitLab trigger and central execution control.
- 🔗 **GitLab API (Authenticated)**: `orchestrator/gitlab_client.py` supports token-authenticated pipeline triggers and multi-repo remote execution.
- 📊 **Aggregation + Reporting**: Canonical JSON merger, HTML reports, dashboard-ready payloads.
- 🧾 **History + Trends**: SQLite persistence and trend timeline generation.
- 📈 **Live Dashboard Data Flow**: FastAPI backend endpoint `/metrics` + Chart.js frontend polling for real-time chart updates.
- 🔗 **Azure DevOps Full API Wiring**: PAT-authenticated test run creation, result push, and attachments via `integrations/ado/ado_api.py`.
- 🔐 **Secrets Wiring**: Env + AWS Secrets Manager + GCP Secret Manager + Vault.
- 🔐 **AWS IAM Secrets Integration**: `config/secrets/aws_iam.py` uses IAM role credentials (no hardcoded keys) for production-safe access.
- 🔁 **CI/CD**: Enterprise pipeline stages: `orchestrate -> deploy -> test -> report`.

## Framework Flow
1. Build tag query from structured UI fields.
2. Trigger relevant repos (GitLab/local).
3. Execute tests (local or distributed/Kubernetes-ready).
4. Aggregate canonical outputs.
5. Store history in SQLite.
6. Push run payload to Azure DevOps and link PBIs.
7. Serve dashboard frontend/backend with live metric refresh.

## Key Commands
```bash
# Local execution
python orchestrator/execution_router.py --runner pytest --query "scope=api AND intent=functional"

# Distributed execution (Kubernetes-ready, local fallback execution)
python runners/distributed_runner.py --execution-mode local --query "scope=api"
python runners/distributed_runner.py --execution-mode k8s --query "scope=api" --namespace qa

# Real Kubernetes job apply
python infra/k8s/k8s_runner.py --job-name api-tests-smoke --image python:3.11 --namespace qa --parallelism 3 --completions 3 --cmd pytest -q

# Enterprise orchestration
python orchestrator/enterprise_orchestrator.py --local-repos-file repos.json --query "scope=api"

# Dashboard frontend rendering
python dashboard/dashboard.py --aggregated artifacts/aggregated_canonical.json --out artifacts/dashboard.html

# Dashboard backend (live DB endpoints)
uvicorn dashboard.backend:app --host 0.0.0.0 --port 8080

# Build + push ADO submission
python integrations/ado_client.py --aggregated artifacts/aggregated_canonical.json --out artifacts/ado_submission.json
python integrations/ado_client.py --aggregated artifacts/aggregated_canonical.json --push --org-url <url> --project <project> --token <token>
```

## Deployment Wiring Checklist

### 1) Kubernetes cluster setup
- Create namespace(s) for execution (`qa`, `perf`, etc.).
- Ensure runner image pull permissions (service account + image pull secret if private registry).
- Grant RBAC for Jobs/Pods (`create`, `get`, `list`, `watch`, `delete`).
- Validate kube-context from CI and run `kubectl auth can-i create jobs -n qa`.

### 2) GitLab runner configuration
- Use a runner with network path to your Kubernetes API (or shell/docker runner with kubeconfig).
- Store `GITLAB_PRIVATE_TOKEN` as masked/protected CI variable.
- Configure per-repo/project IDs and branch refs for fan-out orchestration.

### 3) Azure DevOps PAT + project wiring
- Create PAT with `Test Management` + `Work Items` scopes.
- Set `ADO_ORG_URL`, `ADO_PROJECT`, and `ADO_PAT` as CI secrets.
- Validate API by creating a test run and pushing a sample result payload.

### 4) AWS IAM role assignment
- Attach IAM role to compute runtime (EC2/EKS task/pod role).
- Minimum policy: `secretsmanager:GetSecretValue` for scoped secret ARNs.
- Set `AWS_REGION` and reference only secret IDs/ARNs in config.

### 5) Domain hosting for dashboard
- Host frontend (`dashboard/frontend/index.html`) on static host (S3 + CloudFront / GitLab Pages / internal nginx).
- Publish backend (`uvicorn dashboard.backend:app`) behind API gateway/ingress.
- Set CORS allow-list to dashboard domain and pin HTTPS certificates.


## New Governance + Execution Additions

### Tag governance guardrails
- `tagging/tag_governance.py` enforces required tags and validates both pytest markers and BDD feature tags.
- Prevents unqueryable or malformed test additions before they scale into suites.

Run:
```bash
python tagging/tag_governance.py functional performance governance
```

### Execution engine (dry-run + parallel + atomic + portability)
- `orchestrator/execution_engine.py` adds a single command interface for:
  - dry-run collection
  - threaded parallel execution
  - atomic (single-test unit) execution
  - portability mode (`local`, `docker`, `k8s`, `gitlab`)

Run:
```bash
python orchestrator/execution_engine.py --query "scope=api AND intent=functional" --dry-run
python orchestrator/execution_engine.py --query "scope=api" --parallel 8 --atomic
python orchestrator/execution_engine.py --query "intent=performance" --runner gitlab --parallel 5
```

### BDD structure
Framework now includes:

```text
functional/
  features/
  steps/
  data/
performance/
  latency/
  capacity/
```

- add `.feature` files in `functional/features/`
- add step definitions in `functional/steps/`
- enforce cross-suite queryability through standard tags

### Infra setup playbooks
See `deployment/` for:
- Kubernetes setup
- GitLab runner setup
- Azure DevOps PAT/project wiring
- AWS IAM role assignment
- dashboard domain hosting
