from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

CANONICAL_NAME = "canonical.json"
DEFAULT_OUTPUT_DIR = Path("reporting/output")


def _iter_canonical_paths(base_dir: Path = DEFAULT_OUTPUT_DIR) -> list[Path]:
    if not base_dir.exists():
        return []
    return sorted(path for path in base_dir.rglob(CANONICAL_NAME) if path.is_file())


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def aggregate_all(base_dir: Path | str = DEFAULT_OUTPUT_DIR) -> dict[str, Any]:
    root = Path(base_dir)
    canonical_paths = _iter_canonical_paths(root)

    runs: list[dict[str, Any]] = []
    merged_results: list[dict[str, Any]] = []
    for path in canonical_paths:
        payload = _load_json(path)
        runs.append(payload)
        for result in payload.get("results", []):
            enriched = dict(result)
            enriched["run_id"] = payload.get("run_id")
            enriched["timestamp"] = payload.get("timestamp")
            merged_results.append(enriched)

    total = len(merged_results)
    failed = sum(1 for r in merged_results if r.get("status") == "failed")
    passed = sum(1 for r in merged_results if r.get("status") == "passed")

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "canonical_paths": [str(path) for path in canonical_paths],
        "runs": runs,
        "results": merged_results,
        "summary": {
            "total_runs": len(runs),
            "total": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": round(passed / total, 4) if total else 0.0,
        },
    }


def write_aggregated(output_path: str = "reporting/output/aggregated_results.json") -> Path:
    aggregated = aggregate_all()
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(aggregated, indent=2), encoding="utf-8")
    return out
