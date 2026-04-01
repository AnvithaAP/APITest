# Enterprise API Testing Framework

A production-grade API quality framework designed for **maximum defect detection** with explicit coverage across contract, behavior, data correctness, auth, headers, errors, availability, and performance.

## API Coverage-First Test Structure

```text
functional/
  contract/      # schema + structure checks
  data/          # response content correctness
  behavior/      # business rule validation
  error/         # error payload + status handling
  auth/          # authentication + authorization
  availability/  # uptime and health checks
  headers/       # header correctness and compliance
  features/      # BDD feature files
  steps/         # BDD step definitions
performance/
  ...            # latency/capacity/scalability suites
```

This structure enforces a no-gap default and makes adding new tests straightforward:
1. Pick the concern folder.
2. Add a tagged test.
3. Run by concern/tag in CI or locally.

## Validation Engine (Reusable and Centralized)

`core/validators/` now provides reusable validators for:
- Schema validation
- Response/status validation
- Header validation
- Error payload validation
- Availability probing
- Performance SLO validation (threshold + percentile)

All validators are importable from `core.validators` to keep tests concise and standardized.

## Coverage, Control, and Tagging

Each test uses structured tags:
- `scope`
- `intent`
- `concern`
- `type`
- `module`
- `release`

This supports precise slicing by module, concern, and execution purpose (smoke/regression/system/load/etc), and powers governance checks to prevent untagged tests.

## Execution + Orchestration + Distribution

- **Execution engine**: local/parallel/atomic execution.
- **Orchestration**: multi-repo GitLab triggering and routing.
- **Distribution**: local and Kubernetes-distributed runners.
- **Reporting**: canonical aggregation + HTML/Allure/dashboard artifacts.
- **History**: SQLite-backed trend persistence.
- **Dashboard**: FastAPI + frontend for live metrics.
- **Governance**: tag validation and policy checks.

## GitLab CI/CD (Optimized Flow)

Pipeline stages:
1. `validate` (governance + dry-run collection)
2. `orchestrate` (multi-repo orchestration)
3. `test` (parallel execution with `pytest -n auto`)
4. `report` (aggregate and publish artifacts)

This is designed for fast feedback, scalable execution, and repeatable releases.

## Quick Commands

```bash
# Validate governance and collect suite
python tagging/tag_governance.py functional performance governance
pytest --collect-only -q

# Local targeted execution
python orchestrator/execution_engine.py --query "scope=api AND intent=functional" --parallel 8 --atomic

# Parallel full run
pytest -n auto -q

# Distributed/Kubernetes execution
python runners/distributed_runner.py --execution-mode k8s --query "scope=api" --namespace qa

# Generate dashboard/report assets
python dashboard/dashboard.py --aggregated artifacts/aggregated_canonical.json --out artifacts/dashboard.html
```
