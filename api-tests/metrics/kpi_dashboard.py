from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.config import load_env_file
from metrics.kpi_engine import KPIEngine


def render_markdown(kpi_payload: dict) -> str:
    summary = kpi_payload.get("summary", {})
    concern_distribution = kpi_payload.get("distribution", {}).get("concern", {})

    lines = [
        "# KPI Dashboard",
        "",
        f"- **Environment**: `{kpi_payload.get('environment', 'unknown')}`",
        f"- **Base URL**: `{kpi_payload.get('base_url', 'n/a')}`",
        "",
        "## Execution Health",
        "",
        f"- Total tests: **{summary.get('total', 0)}**",
        f"- Passed: **{summary.get('passed', 0)}**",
        f"- Failed: **{summary.get('failed', 0)}**",
        f"- Skipped: **{summary.get('skipped', 0)}**",
        f"- Pass rate: **{summary.get('pass_rate', 0)}%**",
        f"- Fail rate: **{summary.get('fail_rate', 0)}%**",
        f"- Avg test duration: **{summary.get('avg_duration_seconds', 0)}s**",
        f"- Error rate: **{summary.get('error_rate', 0)}**",
        f"- Throughput (tests/s): **{summary.get('throughput_tests_per_second', 0)}**",
        f"- Flaky tests: **{summary.get('flaky_tests', 0)}**",
        f"- Regression drift: **{summary.get('regression_drift_pct', 0)}%**",
        "",
        "## Coverage by Concern",
        "",
    ]

    if not concern_distribution:
        lines.append("- No concern distribution data available.")
    else:
        for concern, count in sorted(concern_distribution.items()):
            lines.append(f"- {concern}: **{count}**")

    return "\n".join(lines) + "\n"


def generate_dashboard(report_path: str = "artifacts/pytest_report.json") -> tuple[Path, Path]:
    env_values = load_env_file("config/runtime.env")
    kpi_json_path = Path(env_values.get("KPI_REPORT_PATH", "artifacts/kpi_report.json"))
    dashboard_path = Path(env_values.get("KPI_DASHBOARD_PATH", "artifacts/kpi_dashboard.md"))

    payload = KPIEngine(report_path=report_path).compute()
    kpi_json_path.parent.mkdir(parents=True, exist_ok=True)
    kpi_json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    dashboard_path.parent.mkdir(parents=True, exist_ok=True)
    dashboard_path.write_text(render_markdown(payload), encoding="utf-8")

    return kpi_json_path, dashboard_path


if __name__ == "__main__":
    report_file, dashboard_file = generate_dashboard()
    print(f"KPI JSON: {report_file}")
    print(f"KPI dashboard: {dashboard_file}")
