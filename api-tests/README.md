# Enterprise API Testing Framework

A governance-first, config-driven, and enterprise-scalable framework for validating API quality across functional correctness, resilience, performance, and release-readiness.

---

## 1. Framework Goals

This framework is designed to ensure:

- **TESTING**: deep API validation by concern (contract, auth, data, behavior, errors, availability, headers, performance)
- **EXECUTION**: atomic, local, and parallel execution paths
- **ORCHESTRATION**: selective query-driven routing and multi-repo workflows
- **DISTRIBUTION**: local + Kubernetes-backed distributed execution
- **REPORTING**: canonical result aggregation and artifact generation
- **HISTORY**: trend persistence and historical analytics
- **DASHBOARD**: digestible quality dashboard output
- **CI/CD**: validate → orchestrate → test → report pipeline model
- **GOVERNANCE**: enforced tagging and quality standards
- **DOCUMENTATION**: best-practice and leadership-ready docs
- **METRICS**: KPI layer with pass/fail and concern-level insights
- **CONFIG CONTROL**: centralized config for reusable modular execution

---

## 2. Architecture Overview

```text
api-tests/
  core/
    client/               # HTTP primitives
    config/               # central configuration loader
    validators/           # reusable validation components

  functional/             # behavior-focused API correctness suites
    contract/
    data/
    behavior/
    error/
    auth/
    availability/
    headers/
    features/             # BDD feature files
    steps/                # BDD step definitions

  performance/            # latency/capacity/scalability/stability

  governance/             # naming/header/response standards and policy checks
  tagging/                # tag schema, parser, governance enforcement

  orchestrator/           # query/execution routing + enterprise orchestration
  runners/                # pytest/k6/gatling/distributed runners
  infra/k8s/              # Kubernetes distribution primitives

  reporting/              # canonical + html/allure adapters
  history/                # sqlite persistence + trend analysis
  dashboard/              # backend + frontend dashboard components
  metrics/                # KPI computation and dashboard markdown generation

  integrations/           # ADO traceability and enterprise connectors
  deployment/             # setup docs for GitLab, K8s, AWS IAM, ADO

  config/
    runtime.env           # frequently changing values (edit once)
    env.yaml              # environment topology defaults
    endpoints.yaml        # endpoint mappings

  docs/
    best_practices.md     # governance/maintainability rules
    presentation.md       # leadership demo narrative
```

---

## 3. Execution Model

### Local execution
Run specific suites directly with `pytest` and tag-query filters.

### Query-driven selective execution
Use `--tag-query` (or orchestrator query engines) to execute only relevant subsets:

- smoke
- regression
- module-specific
- concern-specific
- release-specific

### Parallel and atomic execution
- Parallel: `pytest -n auto`
- Atomic mode: execution engine can isolate targeted runs for deterministic debugging.

---

## 4. Tagging System (Governance Core)

Mandatory tags per test:

- `scope`
- `intent`
- `concern`
- `type`
- `module`
- `release`

Why this matters:

- Prevents unstructured tests
- Enables selective slicing and CI optimization
- Supports governance checks and portfolio-level traceability

Governance entrypoints:

- `tagging/tag_governance.py`
- `tagging/tag_guard.py`

---


## Tag Rules

Core invariant:

- `scope + intent -> allowed concerns + allowed types`

The source of truth is `tagging/tag_model.py` and every test/query must satisfy that matrix.
Examples:

- `scope=ui + intent=functional` only allows concerns from `[visual, interaction, data, state, flow]` and types from `[smoke, sanity, regression, system]`
- `scope=api + intent=performance` only allows concerns from `[latency, capacity, scalability, stability]` and types from `[load, stress, spike, soak, benchmark]`

Invalid combinations will:

- fail locally
- fail CI
- block execution

---

## 5. Centralized Config-Driven Architecture (Critical)

### Frequently changing values: `config/runtime.env`
Use this file for fast-moving values such as:

- target environment
- base URL override
- request timeout
- default release label
- KPI output paths

### Stable environment topology: `config/env.yaml`
Stores environment names and base URL defaults.

### Endpoint mapping: `config/endpoints.yaml`
Stores service and endpoint paths to remove hardcoding.

### Single access point
Use `core.config.load_runtime_config()` so updates to config files propagate framework-wide.

**Result:** change once → reflect everywhere.

---

## 6. KPI / Metrics Layer

### Files
- `metrics/kpi_engine.py`
- `metrics/kpi_dashboard.py`

### Current KPIs
- pass rate
- fail rate
- average test duration
- execution distribution by concern

### Extension roadmap
- latency trends
- failure-rate trend movement
- regression stability index
- release quality scoring

---

## 7. Reporting, History, and Dashboard

- `reporting/`: canonical formatting, Cucumber/BDD JSON, standardized multi-repo envelopes, HTML, and Allure adapters
- `history/`: SQLite trend storage and analyzers
- `dashboard/`: backend and frontend presentation layer
- `metrics/`: KPI markdown and JSON generation for leadership-level summaries

---


### BDD / Cucumber outputs

Every pytest execution is now exported as:

- `artifacts/pytest_report.json` (internal execution result)
- `artifacts/canonical_run.json` (normalized framework run contract)
- `artifacts/cucumber-report.json` (Cucumber JSON compatible with BDD dashboards)
- `artifacts/standardized-report.json` (`open-bdd-v1` portable envelope for cross-repo aggregation)

This allows each repository to publish a standard artifact that can be merged into a single dashboard feed.


### Local pre-commit enforcement

Install the repository-managed Git hook so commits are blocked when tag rules are violated:

```bash
git config core.hooksPath .githooks
chmod +x .githooks/pre-commit
```

The hook runs `python -m tagging.tag_validator_cli` before every commit.

---

## 8. CI/CD Flow (GitLab)

Standard stage flow:

1. **validate**
   - tagging governance checks
   - test collection sanity
2. **orchestrate**
   - multi-repo/targeted run planning
3. **test**
   - distributed or parallel execution
4. **report**
   - aggregate canonical output + generate dashboard/KPI artifacts

---

## 9. Integrations and Enterprise Scale

- **K8s distribution**: scalable run execution
- **GitLab orchestration**: controlled CI execution strategy
- **ADO integration**: traceability and work-item alignment
- **AWS IAM setup**: secure cloud access patterns

This enables platform-scale adoption across teams and services.

---

## 10. Practical Commands

```bash
# 1) Governance checks
python tagging/tag_governance.py functional performance governance
pytest --collect-only -q

# 2) Selective execution
pytest -q --tag-query "scope=api AND intent=functional AND type=smoke"

# 3) Orchestrated execution
python orchestrator/execution_engine.py --query "scope=api AND concern=auth" --parallel 8 --atomic

# 4) Distributed execution
python runners/distributed_runner.py --execution-mode k8s --query "scope=api" --namespace qa

# 5) Dashboard + KPI outputs
python dashboard/dashboard.py --aggregated artifacts/aggregated_canonical.json --out artifacts/dashboard.html
python metrics/kpi_engine.py
python metrics/kpi_dashboard.py

# 6) Multi-repo standardized aggregation
python reporting/aggregate_reports.py ../repo-a/artifacts/standardized-report.json ../repo-b/artifacts/standardized-report.json --out artifacts/aggregated_canonical.json
```

---

## 11. Modular Design Philosophy

- Keep tests concern-specific and atomic.
- Reuse validators from `core/validators`.
- Keep orchestration independent from test logic.
- Keep config centralized and environment-aware.
- Keep KPI/reporting separated from execution for maintainability.

This separation protects long-term maintainability and prevents framework degradation.

---

## 12. Documentation Additions

- Best practices guide: `docs/best_practices.md`
- Leadership presentation: `docs/presentation.md`

These docs support operational excellence and executive communication.
