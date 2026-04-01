# Enterprise API Testing Framework

Production-grade, modular API quality framework for **functional**, **performance**, and **governance** testing with strict tag governance, canonical reporting, and historical trend analytics.

## Highlights
- Python + Pytest + Requests functional stack.
- k6 primary performance runner (Gatling optional wrapper).
- Strict required tag contract with pre-execution enforcement.
- Query-driven selective execution (`scope=api AND intent=functional ...`).
- Canonical JSON output + Allure + HTML summary.
- SQLite run history + trend HTML report.

## Structure
See project folders under `api-tests/` matching required architecture.

## Prerequisites
- Python 3.11+
- Node + k6 (for performance)
- Java + Gatling (optional)

Install Python deps:
```bash
pip install -r requirements.txt
```

## Configuration
- `config/env.yaml`: environment-specific base URLs and defaults.
- `config/endpoints.yaml`: endpoint catalog.
- Secrets are resolved using `config/secrets_manager.py` from AWS/GCP/local env vars. No plaintext secrets in code.

## Tag Model (Required)
Each test must include all tags via `@pytest.mark.tag(...)`:
- `scope=api`
- `intent=functional|performance`
- `concern=<allowed>`
- `type=<allowed>`
- `module=<api_group>`

Examples:
```python
@pytest.mark.tag(
    "scope=api",
    "intent=functional",
    "concern=data",
    "type=regression",
    "module=users"
)
```

## Run tests by tag query
```bash
python orchestrator/execution_router.py \
  --runner pytest \
  --query "scope=api AND intent=functional AND concern=data AND type=regression"
```

## Direct runners
```bash
python runners/pytest_runner.py --query "scope=api AND intent=functional"
python runners/k6_runner.py --script performance/latency/k6_latency.js
python runners/gatling_runner.py --simulation simulations.BasicSimulation
```

## Reports
Generated under `artifacts/`:
- `canonical_run.json` (mandatory canonical format)
- `html_report.html`
- `allure-results/` (if plugin installed)
- `history_trends.html`

## Add a new functional test
1. Place test under appropriate concern folder in `functional/`.
2. Add required tags using `@pytest.mark.tag`.
3. Reuse `core/client/http_client.py` and validators.
4. Add/update response schema under `schemas/responses/` and validate in the test.

## Add a new API module
1. Add endpoint definitions in `config/endpoints.yaml`.
2. Add module-scoped tests with `module=<new_group>`.
3. Update allowed modules in `tagging/tag_validator.py` (controlled extension).

## View history and trends
After each functional run, history is persisted into SQLite and trends are regenerated:
```bash
python history/trend_analyzer.py --db artifacts/history.db --out artifacts/history_trends.html
```

## CI/CD (GitLab)
`.gitlab-ci.yml` accepts query variables and stores reports as artifacts for downstream aggregation.
