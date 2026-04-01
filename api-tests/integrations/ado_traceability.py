from __future__ import annotations

import json
from pathlib import Path


def _iter_results(payload: dict) -> tuple[list[dict], dict]:
    if "results" in payload:
        return payload.get("results", []), payload

    dashboard = payload.get("dashboard", {})
    canonical_stub = {
        "run_id": payload.get("run_id", "aggregated"),
        "source_repo": payload.get("source_repo", "multi-repo"),
        "timestamp": payload.get("timestamp", ""),
        "query": payload.get("query", ""),
        "dashboard": dashboard,
    }

    results = []
    for row in dashboard.get("merged_results", []):
        results.append(
            {
                "test_name": row.get("test"),
                "status": row.get("status"),
                "tags": row.get("tags", {}),
            }
        )
    return results, canonical_stub


def build_ado_traceability_payload(canonical_path: str, run_url: str = "") -> dict:
    canonical = json.loads(Path(canonical_path).read_text(encoding="utf-8"))
    source_results, context = _iter_results(canonical)

    tests = []
    for result in source_results:
        tags = result.get("tags", {})
        pbi_id = tags.get("pbi") or tags.get("ado-pbi") or ""
        test_case_id = tags.get("testcase") or tags.get("ado-testcase") or result.get("test_name")
        tests.append(
            {
                "automatedTestName": result.get("test_name"),
                "outcome": result.get("status"),
                "release": tags.get("release", context.get("timestamp", "")),
                "module": tags.get("module", "platform"),
                "traceability": {
                    "pbiId": pbi_id,
                    "testCaseRef": test_case_id,
                    "automationRef": {
                        "repository": context.get("source_repo"),
                        "pipelineRun": context.get("run_id"),
                    },
                    "resultRef": {
                        "runId": context.get("run_id"),
                        "status": result.get("status"),
                    },
                    "dashboardRef": {
                        "kpiSnapshot": context.get("dashboard", {}).get("kpis", {}),
                        "releaseReadiness": context.get("dashboard", {}).get("release_readiness", {}),
                    },
                },
                "automationDetails": {
                    "query": context.get("query", ""),
                    "runUrl": run_url,
                },
            }
        )

    return {
        "runId": context.get("run_id"),
        "sourceRepo": context.get("source_repo"),
        "timestamp": context.get("timestamp"),
        "traceabilityChain": "PBI -> Test Case -> Run -> Result -> Dashboard",
        "results": tests,
    }


def write_ado_traceability_payload(canonical_path: str, output_path: str = "artifacts/ado_traceability.json") -> Path:
    payload = build_ado_traceability_payload(canonical_path)
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return out
