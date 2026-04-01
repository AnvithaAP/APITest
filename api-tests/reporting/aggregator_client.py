from __future__ import annotations

import json
from pathlib import Path


def merge_canonical_reports(paths: list[str], output_path: str) -> Path:
    merged_runs: list[dict] = []
    for path in paths:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if "runs" in data:
            merged_runs.extend(data["runs"])
        else:
            merged_runs.append(data)

    summary = {
        "total_runs": len(merged_runs),
        "total_tests": sum(run.get("summary", {}).get("total", 0) for run in merged_runs),
        "total_failed": sum(run.get("summary", {}).get("failed", 0) for run in merged_runs),
    }

    payload = {
        "runs": merged_runs,
        "summary": summary,
        "artifacts": {
            "allure_results": "artifacts/allure-results",
            "html_report": "artifacts/html_report.html",
            "canonical": output_path,
        },
    }

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return out
