from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import uuid



    tests = pytest_json.get("tests", [])
    results = []
    for test in tests:
        results.append(
            {
                "test_name": test.get("nodeid"),
                "status": test.get("outcome"),
                "duration": test.get("call", {}).get("duration", 0),
                "metrics": test.get("keywords", {}),
                "tags": test.get("tags", {}),
            }
        )

    summary = pytest_json.get("summary", {})
    return {
        "schema_version": "1.1",
        "run_id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),

        "results": results,
        "summary": {
            "total": summary.get("total", len(results)),
            "passed": summary.get("passed", 0),
            "failed": summary.get("failed", 0),
            "skipped": summary.get("skipped", 0),
        },
    }


def _first_value(values: list[str] | None, default: str) -> str:
    if not values:
        return default
    return values[0]


def write_canonical_report(report: dict, output_path: str = "artifacts/canonical_run.json") -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return path
