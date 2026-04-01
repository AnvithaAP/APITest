# Enterprise API Testing Framework

Modular API quality framework with two primary execution domains:
- `functional/` for API functional + governance + contract quality.
- `performance/` for API non-functional performance workloads.

## Core Design Goals
- **Portable execution:** query + tag driven test selection in any runner.
- **Strict governance:** hard validation of required tags at collection time.
- **Standardized reporting:** canonical JSON payload for cross-repo aggregation.
- **Local + CI visibility:** HTML + Allure + Extent-compatible canonical data.
- **Historical analytics:** SQLite persistence + post-run trend HTML generation.

## Folder Architecture
```
api-tests/
  functional/           # pytest suites by concern
  governance/           # API governance checks (headers/body/naming/consistency)
  performance/          # k6 scripts by concern
  schemas/              # request/response schemas + version contracts
  tagging/              # tag parser/validator/guard + schema contract
  runners/              # pytest, k6, gatling adapters
  orchestrator/         # query router for local/remote runners
  reporting/            # canonical + html + multi-repo aggregation
  history/              # sqlite storage + trend html rendering
  artifacts/            # generated outputs
```

## Mandatory Tag Contract (6 tags)
All test cases must declare one `@pytest.mark.tag(...)` with:
1. `scope=api`
2. `intent=functional|performance|security|reliability`
3. `concern=<context-aware by intent>`
4. `type=<context-aware by intent>`
5. `module=<product module>`
6. `release=RYYYY.MM-SN` (example: `R2026.04-S7`)

Example:
```python
@pytest.mark.tag(
    "scope=api",
    "intent=functional",
    "concern=contract",
    "type=regression",
    "module=users",
    "release=R2026.04-S7"
)
```

## Query-driven Execution (granular)
Supports AND combinations and multi-value selectors:
- `scope=api AND intent=functional AND type=regression`
- `intent=functional AND module=users,orders AND release=R2026.04-S7`

Run functional/governance via router:
```bash
python orchestrator/execution_router.py --runner pytest --query "scope=api AND intent=functional"
```

Run with dry-run / parallel / retries:
```bash
python runners/pytest_runner.py --query "intent=functional" --dry-run
python runners/pytest_runner.py --query "intent=functional AND type=regression" --parallel 4 --retries 2
```

## Performance Execution
```bash
python runners/k6_runner.py --script performance/latency/k6_latency.js --query "intent=performance AND concern=latency"
```

## Reporting Standard
Generated under `artifacts/`:
- `pytest_report.json` raw run output.
- `canonical_run.json` standardized run payload (schema v1.1).
- `html_report.html` local summary.
- `allure-results/` for Allure consumption.
- `history.db` SQLite historical metrics.
- `history_trends.html` table + trend graph snapshots.

Cross-repo aggregation:
```python
from reporting.aggregator_client import merge_canonical_reports
merge_canonical_reports([
  "repoA/artifacts/canonical_run.json",
  "repoB/artifacts/canonical_run.json"
], "artifacts/aggregated_canonical.json")
```

## ADO/GitLab Traceability Model
Recommended mapping:
- ADO PBI / Feature ID -> include in test metadata and node naming.
- ADO Test Case Work Item ID -> include as structured test metadata.
- Tag `module` + `release` + canonical `test_name` -> deterministic linkage to results.
- Export canonical JSON to Azure DevOps dashboard pipeline for unified quality views.

## Add New Tests Quickly
1. Add file under correct concern in `functional/` or script in `performance/`.
2. Apply required six-tag contract.
3. Reuse shared clients/validators from `core/`.
4. Add or version schemas under `schemas/`.
5. Execute targeted query locally before CI.

## GitLab CI
Use `.gitlab-ci.yml` with `TAG_QUERY` and persist `artifacts/` as job artifacts for downstream aggregation/publishing.
