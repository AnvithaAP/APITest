# Enterprise API Testing Framework

A production-oriented quality platform with **tag intelligence**, **distributed execution**, **orchestration**, **aggregation/reporting**, **history/trends**, and a **FastAPI-backed dashboard**.

## Capability Map
- 🧪 **Test Layer**: Functional + Performance + Governance modules with structured tags (`scope`, `intent`, `concern`, `type`, `module`).
- 🧠 **Tag Intelligence**: Query parser, UI-selection mapping, inheritance rules, and query-string generation ready for AND/OR expansion.
- ⚙️ **Execution Layer**: Local execution plus distributed runner that emits Kubernetes Job specs and can submit pod-based jobs.
- 🌐 **Orchestration Layer**: Multi-repo GitLab trigger and central execution control.
- 📊 **Aggregation + Reporting**: Canonical JSON merger, HTML reports, dashboard-ready payloads.
- 🧾 **History + Trends**: SQLite persistence and trend timeline generation.
- 📊 **Dashboard (Upgraded)**: Chart-ready frontend + live FastAPI backend endpoints.
- 🔐 **Secrets Wiring**: Env + AWS Secrets Manager + GCP Secret Manager + Vault.
- 🔁 **CI/CD**: Enterprise pipeline stages: `orchestrate -> deploy -> test -> report`.

## Framework Flow
1. Build tag query from structured UI fields.
2. Trigger relevant repos (GitLab/local).
3. Execute tests (local or distributed/Kubernetes-ready).
4. Aggregate canonical outputs.
5. Store history in SQLite.
6. Push run payload to Azure DevOps and link PBIs.
7. Serve dashboard frontend/backend.

## Key Commands
```bash
# Local execution
python orchestrator/execution_router.py --runner pytest --query "scope=api AND intent=functional"

# Distributed execution (Kubernetes-ready, local fallback execution)
python runners/distributed_runner.py --execution-mode local --query "scope=api"
python runners/distributed_runner.py --execution-mode k8s --query "scope=api" --namespace qa

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
