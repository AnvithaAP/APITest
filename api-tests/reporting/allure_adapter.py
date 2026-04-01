from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import uuid


def ensure_allure_dir(path: str = "artifacts/allure-results") -> Path:
    out = Path(path)
    out.mkdir(parents=True, exist_ok=True)
    return out


def write_allure_results(canonical_report: dict, path: str = "artifacts/allure-results") -> Path:
    out = ensure_allure_dir(path)
    _write_executor(out, canonical_report)
    _write_environment(out, canonical_report)

    for result in canonical_report.get("results", []):
        case_uuid = str(uuid.uuid4())
        history_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, result["test_name"]))
        payload = {
            "uuid": case_uuid,
            "historyId": history_id,
            "name": result["test_name"],
            "fullName": result["test_name"],
            "status": _map_status(result["status"]),
            "stage": "finished",
            "start": _ts_ms(),
            "stop": _ts_ms(),
            "labels": [
                {"name": "framework", "value": "pytest"},
                {"name": "intent", "value": canonical_report.get("intent", "unknown")},
                {"name": "source_repo", "value": canonical_report.get("source_repo", "unknown")},
                {"name": "scope", "value": canonical_report.get("scope", "unknown")},
            ],
            "steps": [
                {"name": "Apply tag query", "status": "passed", "stage": "finished"},
                {"name": "Execute test", "status": _map_status(result["status"]), "stage": "finished"},
                {"name": "Collect canonical metrics", "status": "passed", "stage": "finished"},
            ],
            "attachments": [
                {
                    "name": "test-tags",
                    "type": "application/json",
                    "source": f"{case_uuid}-tags.json",
                },
                {
                    "name": "test-metrics",
                    "type": "application/json",
                    "source": f"{case_uuid}-metrics.json",
                },
            ],
        }

        (out / f"{payload['uuid']}-result.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
        (out / f"{case_uuid}-tags.json").write_text(json.dumps(result.get("tags", {}), indent=2), encoding="utf-8")
        (out / f"{case_uuid}-metrics.json").write_text(json.dumps(result.get("metrics", {}), indent=2), encoding="utf-8")

        container = {
            "uuid": str(uuid.uuid4()),
            "name": result["test_name"],
            "children": [case_uuid],
            "befores": [{"name": "test setup", "status": "passed", "stage": "finished"}],
            "afters": [{"name": "test teardown", "status": "passed", "stage": "finished"}],
        }
        (out / f"{container['uuid']}-container.json").write_text(json.dumps(container, indent=2), encoding="utf-8")

    return out


def _write_executor(out: Path, canonical: dict) -> None:
    payload = {
        "name": "GitLab Orchestrator",
        "type": "gitlab",
        "buildName": canonical.get("run_id"),
        "buildUrl": canonical.get("metadata", {}).get("pipeline_url", ""),
        "reportUrl": canonical.get("metadata", {}).get("report_url", ""),
    }
    (out / "executor.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _write_environment(out: Path, canonical: dict) -> None:
    payload = {
        "source_repo": canonical.get("source_repo", ""),
        "scope": canonical.get("scope", ""),
        "intent": canonical.get("intent", ""),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    (out / "environment.properties").write_text("\n".join(f"{k}={v}" for k, v in payload.items()), encoding="utf-8")


def _map_status(status: str) -> str:
    mapping = {"passed": "passed", "failed": "failed", "skipped": "skipped"}
    return mapping.get(status, "broken")


def _ts_ms() -> int:
    return int(datetime.now(timezone.utc).timestamp() * 1000)
