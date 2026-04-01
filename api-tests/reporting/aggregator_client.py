from __future__ import annotations

import json
from pathlib import Path


def merge_canonical_reports(paths: list[str], output_path: str) -> Path:
    merged_runs: list[dict] = []
    for path in paths:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        if "runs" in payload:
            merged_runs.extend(payload["runs"])
        else:
            merged_runs.append(payload)

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(
            {
                "schema_version": "1.1",
                "aggregated_from": paths,
                "runs": merged_runs,
                "summary": {
                    "total_runs": len(merged_runs),
                    "total_tests": sum(run.get("summary", {}).get("total", 0) for run in merged_runs),
                    "total_failed": sum(run.get("summary", {}).get("failed", 0) for run in merged_runs),
                },
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return out
