from __future__ import annotations

import json
from pathlib import Path
import uuid


def ensure_allure_dir(path: str = "artifacts/allure-results") -> Path:
    out = Path(path)
    out.mkdir(parents=True, exist_ok=True)
    return out


def write_allure_results(canonical_report: dict, path: str = "artifacts/allure-results") -> Path:
    out = ensure_allure_dir(path)
    for result in canonical_report.get("results", []):
        payload = {
            "uuid": str(uuid.uuid4()),
            "name": result["test_name"],
            "status": result["status"],
            "stage": "finished",
            "labels": [
                {"name": "framework", "value": "pytest"},
                {"name": "intent", "value": canonical_report.get("intent", "unknown")},
                {"name": "source_repo", "value": canonical_report.get("source_repo", "unknown")},
            ],
        }
        (out / f"{payload['uuid']}-result.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return out
