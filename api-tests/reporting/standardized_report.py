from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any


def build_standardized_report(
    canonical_run: dict[str, Any],
    cucumber_report: list[dict[str, Any]],
    format_name: str = "open-bdd-v1",
) -> dict[str, Any]:
    """Create a repo-portable report envelope for multi-repo aggregation."""
    return {
        "schema": format_name,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "producer": {
            "repo": canonical_run.get("source_repo", "unknown"),
            "run_id": canonical_run.get("run_id", "unknown"),
            "scope": canonical_run.get("scope", "api"),
            "intent": canonical_run.get("intent", "unknown"),
        },
        "summary": canonical_run.get("summary", {}),
        "canonical": canonical_run,
        "cucumber": cucumber_report,
    }


def write_standardized_report(report: dict[str, Any], output_path: str = "artifacts/standardized-report.json") -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return path
