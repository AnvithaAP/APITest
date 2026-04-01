from __future__ import annotations

import json
from pathlib import Path


def build_ado_traceability_payload(canonical_path: str, run_url: str = "") -> dict:
    canonical = json.loads(Path(canonical_path).read_text(encoding="utf-8"))
    tests = []
    for result in canonical.get("results", []):
        tags = result.get("tags", {})
        pbi_id = tags.get("pbi") or tags.get("ado-pbi") or ""
        test_case_id = tags.get("testcase") or tags.get("ado-testcase") or result.get("test_name")
        tests.append(
            {
                "automatedTestName": result.get("test_name"),
                "outcome": result.get("status"),
                "release": tags.get("release", canonical.get("timestamp", "")),
                "module": tags.get("module", "platform"),
                "traceability": {
                    "pbiId": pbi_id,
                    "testCaseRef": test_case_id,
                    "automationRef": {
                        "repository": canonical.get("source_repo"),
                        "pipelineRun": canonical.get("run_id"),
                    },
                    "resultRef": {
                        "runId": canonical.get("run_id"),
                        "status": result.get("status"),
                    },
                },
                "automationDetails": {
                    "query": canonical.get("query", ""),
                    "runUrl": run_url,
                },
            }
        )

    return {
        "runId": canonical.get("run_id"),
        "sourceRepo": canonical.get("source_repo"),
        "timestamp": canonical.get("timestamp"),
        "traceabilityChain": "PBI -> Test Case -> Automation -> Result",
        "results": tests,
    }


def write_ado_traceability_payload(canonical_path: str, output_path: str = "artifacts/ado_traceability.json") -> Path:
    payload = build_ado_traceability_payload(canonical_path)
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return out
