from __future__ import annotations

from pathlib import Path
import json
from typing import Any


def build_cucumber_report(pytest_json: dict[str, Any]) -> list[dict[str, Any]]:
    """Convert internal pytest JSON report into Cucumber JSON format."""
    features: dict[str, dict[str, Any]] = {}

    for test in pytest_json.get("tests", []):
        nodeid = test.get("nodeid", "")
        file_path, scenario_name = _parse_nodeid(nodeid)
        tags = test.get("tags", {}) or {}

        feature = features.setdefault(
            file_path,
            {
                "uri": file_path,
                "name": _feature_name(file_path),
                "id": _slugify(file_path),
                "keyword": "Feature",
                "elements": [],
                "tags": _format_tags(tags),
            },
        )

        status = _to_cucumber_status(test.get("outcome", "failed"))
        duration_ns = int(float(test.get("call", {}).get("duration", 0) or 0) * 1_000_000_000)

        feature["elements"].append(
            {
                "id": _slugify(f"{file_path}-{scenario_name}"),
                "keyword": "Scenario",
                "name": scenario_name,
                "type": "scenario",
                "steps": [
                    {
                        "keyword": "Then ",
                        "name": "the scenario should pass",
                        "result": {
                            "status": status,
                            "duration": duration_ns,
                        },
                    }
                ],
                "tags": _format_tags(tags),
            }
        )

    return list(features.values())


def write_cucumber_report(cucumber_report: list[dict[str, Any]], output_path: str = "artifacts/cucumber-report.json") -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(cucumber_report, indent=2), encoding="utf-8")
    return path


def _parse_nodeid(nodeid: str) -> tuple[str, str]:
    if "::" not in nodeid:
        return nodeid, nodeid
    file_path, scenario = nodeid.split("::", 1)
    return file_path, scenario.replace("_", " ")


def _feature_name(file_path: str) -> str:
    name = Path(file_path).stem.replace("test_", "").replace("_", " ").strip()
    return name.title() or "API Feature"


def _slugify(value: str) -> str:
    return value.lower().replace("/", "-").replace("_", "-").replace(".", "-").replace("::", "-")


def _format_tags(tags: dict[str, str]) -> list[dict[str, str]]:
    return [{"name": f"@{k}:{v}"} for k, v in sorted(tags.items())]


def _to_cucumber_status(pytest_status: str) -> str:
    if pytest_status == "passed":
        return "passed"
    if pytest_status == "skipped":
        return "skipped"
    return "failed"
