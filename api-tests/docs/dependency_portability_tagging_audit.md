# Dependency, Portability, and Tagging Governance Audit

_Date: 2026-04-01_

## Scope
- Dependency management completeness (`requirements.txt` as the primary dependency manifest).
- Framework portability across environments/runners.
- Consistency/governance of test tagging for pytest and BDD scenarios.

## 1) Dependency management completeness

### Findings
- The project uses **pip requirements** (`requirements.txt`) as dependency management.
- Several imported runtime libraries were not listed previously in `requirements.txt`:
  - `boto3` (AWS secret retrieval paths)
  - `google-cloud-secret-manager` (GCP secret retrieval paths)
  - `matplotlib` and `plotly` (history/dashboard chart rendering paths)

### Action taken
- Added the missing packages to `requirements.txt`, grouped as optional integration/charting dependencies.

### Residual notes
- k6 and Gatling runners are external executables (not Python packages), so they should be governed in environment setup docs/CI images, not pip requirements.

## 2) Framework portability

### Findings
- Python code is cross-platform in structure (no hardcoded OS shell assumptions in core test logic).
- Execution portability is **toolchain-dependent** for non-pytest runners:
  - `k6` binary required for `runners/k6_runner.py`.
  - `gatling` binary/JVM required for `runners/gatling_runner.py`.
- Dashboard/history chart rendering is resilient:
  - plotly/matplotlib are optional and code has fallback rendering paths if imports are unavailable.
- Cloud secret providers are optional and gracefully degrade to empty values when provider SDKs/config are absent.

### Governance recommendation
- Keep a CI preflight step that validates presence of required external binaries per selected runner mode (`pytest`, `k6`, `gatling`, `distributed`).

## 3) Tagging consistency and governance

### Findings
- Tag governance is implemented and enforceable via:
  - `tagging/tag_governance.py` scanner (pytest markers + feature tags)
  - `tagging/tag_validator.py` validation rules (required keys, allowed values, intent-to-concern/type constraints, release format)
  - `pytest.ini` marker contract for `tag(*pairs)`
- Governance model requires and checks these keys:
  - `scope`, `intent`, `concern`, `type`, `module`, `release`
- BDD feature governance is explicit and validated as `@key:value` lines before `Feature:`.

### Validation status
- Governance checks pass for current repository tests and tag governance test suite.

## Conclusion
- Dependency manifest completeness improved for actual imported Python runtime modules.
- Framework portability is good for Python-only flows, with expected environment prerequisites for k6/Gatling/distributed execution.
- Tagging appears consistent and properly governed through both static rules and executable checks.
