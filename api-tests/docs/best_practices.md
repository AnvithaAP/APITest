# API Test Framework Best Practices

## 1) Tagging Discipline (Governance-First)
- Every test **must** include complete `@pytest.mark.tag` attributes (`scope`, `intent`, `concern`, `type`, `module`, `release`).
- Keep tag values stable and taxonomy-driven; do not create ad-hoc variants.
- Use `tagging/tag_governance.py` in pre-merge checks to prevent untagged or malformed tests.

## 2) Atomic Test Design
- A test should validate **one behavior outcome** with a clear assertion intent.
- Keep test setup minimal and reusable via fixtures/helpers.
- Avoid chained assertions that make root-cause analysis ambiguous.

## 3) Config-Driven Execution
- Keep frequently changing settings in `config/runtime.env`.
- Keep environment topology in `config/env.yaml`.
- Keep endpoint mappings in `config/endpoints.yaml`.
- Access values only through `core.config.load_runtime_config()` to ensure single-point edits reflect globally.

## 4) Schema and Contract Management
- Store response/request schemas under `schemas/` with explicit versioning.
- Run schema drift checks as part of governance and CI validation stages.
- Treat contract changes as versioned releases; update `release` tag when behavior intentionally changes.

## 5) Maintainability and Scalability
- Keep modules concern-based (`functional/contract`, `functional/auth`, etc.).
- Prefer reusable validators from `core/validators/` rather than duplicating assertion logic.
- Separate execution, orchestration, distribution, reporting, and history layers for independent evolution.
- Track KPI trends continuously and review pass/fail movement with leadership.
