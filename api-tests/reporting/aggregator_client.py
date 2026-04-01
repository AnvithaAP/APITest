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

    normalized = [_normalize_run(run) for run in merged_runs]
    by_scope = _group_summary(normalized)

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(
            {
                "schema_version": "2.0",
                "aggregated_from": paths,
                "runs": normalized,
                "summary": {
                    "total_runs": len(normalized),
                    "total_tests": sum(run.get("summary", {}).get("total", 0) for run in normalized),
                    "total_failed": sum(run.get("summary", {}).get("failed", 0) for run in normalized),
                    "scopes": by_scope,
                },
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    if copy_allure_to:
        aggregate_allure_results(paths, copy_allure_to)

    return out


def _normalize_run(run: dict) -> dict:
    scope = (run.get("scope") or "api").lower()
    intent = (run.get("intent") or "unknown").lower()
    results = run.get("results", [])
    duration_total = sum(float(r.get("duration", 0) or 0) for r in results)
    total = run.get("summary", {}).get("total", len(results)) or len(results)
    failed = run.get("summary", {}).get("failed", 0)
    run["scope"] = scope
    run["intent"] = intent
    run["normalized_metrics"] = {
        "latency_avg_ms": round((duration_total / max(total, 1)) * 1000, 3),
        "error_rate": round(failed / max(total, 1), 5),
        "total_duration_s": round(duration_total, 5),
    }
    return run


def _group_summary(runs: list[dict]) -> dict:
    scopes = {"ui": 0, "api": 0, "e2e": 0, "device": 0, "other": 0}
    for run in runs:
        scope = run.get("scope", "other")
        if scope not in scopes:
            scope = "other"
        scopes[scope] += run.get("summary", {}).get("total", 0)
    return scopes


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
