from __future__ import annotations

import json
from pathlib import Path
import shutil


def merge_canonical_reports(paths: list[str], output_path: str, copy_allure_to: str | None = None) -> Path:
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
                "schema_version": "1.2",
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

    if copy_allure_to:
        aggregate_allure_results(paths, copy_allure_to)

    return out


def aggregate_allure_results(canonical_paths: list[str], output_dir: str) -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    for canonical in canonical_paths:
        root = Path(canonical).parent
        allure_dir = root / "allure-results"
        if not allure_dir.exists():
            continue
        repo_name = root.parent.name
        for file in allure_dir.glob("*"):
            target = out / f"{repo_name}_{file.name}"
            if file.is_file():
                shutil.copy2(file, target)
    return out
