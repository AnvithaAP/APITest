# Enterprise API Testing Framework

A production-oriented quality platform with **intelligence layer**, **cross-repo orchestration**, **real aggregation**, and **dashboard-ready outputs**.

## Delivered Capabilities
- Advanced tag query engine with **AND/OR grouping**, parenthesis, multi-select conversion, and **tag inheritance**.
- Tag guard with **auto-fix + AI-style suggestions** for invalid taxonomy values.
- Full multi-repo orchestrator for GitLab CI with parallel triggers across **UI/API/E2E/Device** repos.
- Canonical aggregation engine that merges multi-repo JSON and emits **dashboard_ready.json**.
- Allure full integration with hooks, executor/environment metadata, attachments, and step-level reporting.
- Trend analytics with **Plotly/Matplotlib charts** + historical delta comparison.
- Azure DevOps traceability payload for **PBI → Test Case → Automation → Result** mapping.

## Modular Structure
```
api-tests/
  functional/                # tagged API functional suites
  governance/                # governance tests + engine
  performance/               # k6 + gatling scripts
  tagging/                   # parser, guard, validator, autofix
  orchestrator/              # query engine + execution routers
  reporting/                 # canonical, html, allure, aggregation
  history/                   # sqlite metrics + trend graph html
  core/validators/           # schema validation + diff engine
  integrations/              # ADO traceability payload hooks
  artifacts/                 # generated outputs
```

## Tag Query Engine (USP)
Examples:
```bash
# AND
scope=api AND intent=functional AND type=regression

# OR groups with parenthesis
scope=api AND (intent=functional OR intent=performance)
```

Tag inheritance examples:
- `scope=e2e` can match `scope=ui` and `scope=api`.
- `scope=device` can match `scope=api`.

## Cross-Repo Orchestrator
Run local orchestrator:
```bash
python orchestrator/execution_router.py --runner pytest --query "scope=api AND intent=functional"
```

Run full multi-repo orchestration:
```bash
python orchestrator/execution_router.py --runner pytest --repos-file repos.json --query "scope=api"
```

`repos.json`:
```json
{
  "repos": [
    {
      "name": "ui-tests",
      "path": "/workspace/ui-tests",
      "repo_type": "ui",
      "runner": "pytest",
      "query": "scope=ui AND intent=functional",
      "parallel": 4
    },
    {
      "name": "api-tests",
      "path": "/workspace/api-tests",
      "repo_type": "api",
      "runner": "pytest",
      "query": "scope=api AND intent=functional"
    },
    {
      "name": "e2e-tests",
      "path": "/workspace/e2e-tests",
      "repo_type": "e2e",
      "runner": "pytest",
      "query": "scope=e2e"
    }
  ]
}
```

## Aggregation + Dashboard Output
Produced under `artifacts/`:
- `aggregated_canonical.json`
- `dashboard_ready.json`
- `orchestrator_results.json`
- `gitlab_orchestrator_summary.json`
- `allure-results-merged/`

## Trend Graphs (Real Charts)
`history/html_trend_report.py` produces:
- interactive Plotly charts (when available)
- matplotlib PNG export (`history_trends.png`)
- HTML report (`history_trends.html`)

## Azure DevOps Traceability
`integrations/ado_traceability.py` creates payloads that align:
**PBI → Test Case → Automation Repo/Run → Result**.

## Schema Validation + Diff
```bash
python core/validators/schema_diff_cli.py --old schemas/responses/user_v1.json --new schemas/versions/user_v2.json --strict
```
