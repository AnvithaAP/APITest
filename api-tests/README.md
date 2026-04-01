# Enterprise API Testing Framework

Production-grade, modular API quality framework for **functional**, **performance**, and **governance** testing with strict tag governance, canonical reporting, and historical trend analytics.

## Highlights
- Python + Pytest + Requests functional stack.
- k6 primary performance runner + Gatling support.
- Strict required tag contract with optional autofix mode.
- Boolean query-driven selective execution (`AND`, `OR`, parenthesis).
- Canonical JSON output + Allure + HTML summary + aggregation metadata.
- SQLite run history + embedded trend graphs.
- Multi-repo orchestrator trigger via repo manifest.
- CI-ready GitLab pipeline and ADO trigger adapter.

## Run tests by tag query
```bash
python orchestrator/execution_router.py \
  --runner pytest \
  --query "scope=api AND (intent=functional OR concern=contract)"
```

## Multi-repo orchestration
```json
{
  "repos": [
    {"name": "api-tests", "path": "/workspace/APITest/api-tests"},
    {"name": "payments-tests", "path": "/workspace/payments-tests"}
  ]
}
```

```bash
python orchestrator/execution_router.py --runner pytest --query "scope=api" --repos-file repos.json
```

## Tag guard modes
- `strict` (default): fail collection when tags are invalid.
- `warn`: continue run and emit warnings.
- `--tag-autofix`: replace invalid marker values with compliant defaults.

## Performance layer
```bash
python runners/k6_runner.py --query "scope=api AND intent=performance AND concern=latency"
python runners/gatling_runner.py --query "scope=api AND intent=performance AND concern=capacity"
```

## History & analytics
```bash
python history/trend_analyzer.py --db artifacts/history.db --out artifacts/history_trends.html
```

## ADO integration
`integrations/ado_adapter.py` provides `AdoAdapter.trigger_pipeline()` to launch Azure DevOps pipelines with branch and variable overrides.

## GitLab
`.gitlab-ci.yml` is production-ready for tag validation, functional execution, performance execution, and report publishing.
