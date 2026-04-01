from __future__ import annotations

from collections import defaultdict
import json
from pathlib import Path
import shutil

from history.sqlite_manager import SQLiteManager


def merge_canonical_reports(
    paths: list[str],
    output_path: str,
    copy_allure_to: str | None = None,
    sqlite_db_path: str | None = "artifacts/history.db",
) -> Path:
    merged_runs: list[dict] = []
    merged_cucumber: list[dict] = []
    for path in paths:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        if payload.get("schema") == "open-bdd-v1":
            merged_runs.append(payload.get("canonical", {}))
            merged_cucumber.extend(payload.get("cucumber", []))
            continue
        if "runs" in payload:
            merged_runs.extend(payload["runs"])
        else:
            merged_runs.append(payload)

    normalized = [_normalize_run(run) for run in merged_runs if run]
    summary = _build_summary(normalized)
    dashboard = _build_dashboard_payload(normalized, summary)

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(
            {
                "schema_version": "3.1",
                "aggregated_from": paths,
                "runs": normalized,
                "summary": summary,
                "dashboard": dashboard,
                "cucumber": merged_cucumber,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    dashboard_out = out.with_name("dashboard_ready.json")
    dashboard_out.write_text(json.dumps(dashboard, indent=2), encoding="utf-8")

    cucumber_out = out.with_name("cucumber_aggregated.json")
    cucumber_out.write_text(json.dumps(merged_cucumber, indent=2), encoding="utf-8")

    if copy_allure_to:
        aggregate_allure_results(paths, copy_allure_to)

    if sqlite_db_path:
        _write_history_metrics(normalized, sqlite_db_path)

    return out


def _normalize_run(run: dict) -> dict:
    scope = (run.get("scope") or run.get("repo_type") or "api").lower()
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


def _build_summary(runs: list[dict]) -> dict:
    scopes = {"ui": 0, "api": 0, "e2e": 0, "device": 0, "other": 0}
    scope_runs = defaultdict(int)
    for run in runs:
        scope = run.get("scope", "other")
        if scope not in scopes:
            scope = "other"
        test_count = run.get("summary", {}).get("total", 0)
        scopes[scope] += test_count
        scope_runs[scope] += 1

    return {
        "total_runs": len(runs),
        "total_tests": sum(run.get("summary", {}).get("total", 0) for run in runs),
        "total_failed": sum(run.get("summary", {}).get("failed", 0) for run in runs),
        "scopes": scopes,
        "runs_by_scope": dict(scope_runs),
    }


def _build_dashboard_payload(runs: list[dict], summary: dict) -> dict:
    timeline = []
    repo_cards = []
    merged_results = []
    for run in sorted(runs, key=lambda r: r.get("timestamp", "")):
        metrics = run.get("normalized_metrics", {})
        total = run.get("summary", {}).get("total", 0)
        failed = run.get("summary", {}).get("failed", 0)
        timeline.append(
            {
                "timestamp": run.get("timestamp"),
                "repo": run.get("source_repo"),
                "scope": run.get("scope"),
                "failed": failed,
                "pass_rate": round(1 - (failed / max(total, 1)), 4),
                "error_rate": metrics.get("error_rate", 0),
                "latency_avg_ms": metrics.get("latency_avg_ms", 0),
            }
        )
        repo_cards.append(
            {
                "repo": run.get("source_repo"),
                "run_id": run.get("run_id"),
                "scope": run.get("scope"),
                "intent": run.get("intent"),
                "total": run.get("summary", {}).get("total", 0),
                "failed": run.get("summary", {}).get("failed", 0),
                "query": run.get("query", ""),
            }
        )
        for result in run.get("results", []):
            merged_results.append(
                {
                    "repo": run.get("source_repo"),
                    "run_id": run.get("run_id"),
                    "test": result.get("test_name"),
                    "status": result.get("status"),
                    "duration": result.get("duration", 0),
                    "tags": result.get("tags", {}),
                }
            )

    total_tests = summary.get("total_tests", 0)
    total_failed = summary.get("total_failed", 0)
    pass_rate = round(1 - (total_failed / max(total_tests, 1)), 4)
    failure_budget_used_pct = round((total_failed / max(total_tests, 1)) * 100, 2)

    return {
        "kpis": {
            "total_runs": summary.get("total_runs", 0),
            "total_tests": total_tests,
            "total_failed": total_failed,
            "pass_rate": pass_rate,
        },
        "scope_breakdown": summary.get("scopes", {}),
        "timeline": timeline,
        "repo_cards": repo_cards,
        "merged_results": merged_results,
        "release_readiness": {
            "status": "ready" if pass_rate >= 0.95 else "at_risk",
            "failure_budget_used_pct": failure_budget_used_pct,
        },
    }


def _write_history_metrics(runs: list[dict], sqlite_db_path: str) -> None:
    db = SQLiteManager(sqlite_db_path)
    for run in runs:
        metrics = run.get("normalized_metrics", {})
        db.insert_metric(
            run_id=run.get("run_id", ""),
            timestamp=run.get("timestamp", ""),
            api_name=run.get("source_repo", "unknown"),
            latency=float(metrics.get("latency_avg_ms", 0)),
            error_rate=float(metrics.get("error_rate", 0)),
            throughput=float(run.get("summary", {}).get("total", 0)),
            scope=run.get("scope", "unknown"),
        )


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
