# Enterprise API Testing Framework

A production-oriented API quality platform with modular layers for **functional**, **performance**, and **governance** testing.

## Delivered Capabilities
- Full orchestrator with **single repo** and **multi-repo trigger** modes.
- Tag query engine with **AND/OR** logic and comma value unions.
- Strict `tag_guard` enforcement with **auto-fix** utilities.
- Canonical reporting + HTML + Allure output and cross-repo aggregation.
- SQLite-backed run history with trend graphs.
- k6 and Gatling runner integrations.
- Schema validation and backward-compatibility diff engine.
- Governance engine for convention and standards checks.
- Azure DevOps traceability payload generation hooks.
- GitLab pipeline suitable for production bootstrap.
- VSCode tasks/settings for tag enforcement workflows.

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

## Tagging (Enforced Entry Point)
Every pytest test must carry one `@pytest.mark.tag(...)` marker with required keys:
- `scope`, `intent`, `concern`, `type`, `module`, `release`

Auto-fix invalid or missing tags:
```bash
python tagging/tag_autofix.py functional governance
```

## Query Engine
Examples:
```bash
# AND
scope=api AND intent=functional AND type=regression

# OR groups
intent=functional AND module=users OR intent=performance AND concern=latency
```

## Orchestrator
Run local orchestrator:
```bash
python orchestrator/execution_router.py --runner pytest --query "scope=api AND intent=functional"
```

Run multi-repo orchestrator:
```bash
python orchestrator/execution_router.py --runner pytest --repos-file repos.json --query "scope=api"
```

`repos.json`:
```json
{
  "repos": [
    {"name": "repo-a", "path": "/workspace/repo-a", "query": "scope=api AND intent=functional"},
    {"name": "repo-b", "path": "/workspace/repo-b", "query": "scope=api AND intent=performance"}
  ]
}
```

## Performance Layer
k6:
```bash
python runners/k6_runner.py --script performance/latency/k6_latency.js --query "intent=performance"
```

Gatling:
```bash
python runners/gatling_runner.py --simulation BasicSimulation --query "intent=performance"
```

## Reporting + History
Outputs under `artifacts/`:
- `canonical_run.json`
- `html_report.html`
- `allure-results/`
- `history.db`
- `history_trends.html`
- `ado_traceability.json`

## Schema Validation + Diff
```bash
python core/validators/schema_diff_cli.py --old schemas/responses/user_v1.json --new schemas/versions/user_v2.json --strict
```

## GitLab Base Pipeline
Use `.gitlab-ci.yml` to validate tags/schema, run functional + governance + perf, and publish canonical/history/ADO artifacts.

## VSCode Integration
- `Tag Guard: Validate`
- `Tag Guard: Auto-fix`

Configured under `.vscode/tasks.json` and `.vscode/settings.json`.
