from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys

from metrics.kpi_engine import calculate_kpis
from reporting.aggregator import aggregate_all, write_aggregated
from tagging.tag_validator import validate_tags


def _build_query_expression(query: dict[str, str]) -> str:
    parts: list[str] = []
    for key in ["scope", "intent", "concern", "type", "module"]:
        value = (query.get(key) or "").strip()
        if value and value.lower() != "all":
            parts.append(f"{key}={value}")
    return " AND ".join(parts)


def run_query(query: dict[str, str], dry_run: bool = False) -> dict:
    validation = validate_tags({**query, "release": query.get("release", "R2026.04-S1")})
    if not validation.ok:
        raise ValueError("validate_tags failed: " + "; ".join(validation.errors))

    query_expr = _build_query_expression(query)

    execution_cmd = [sys.executable, "runners/pytest_runner.py", "--query", query_expr]
    if dry_run:
        execution_cmd.append("--dry-run")
    execute_rc = subprocess.call(execution_cmd)

    aggregated = aggregate_all()
    write_aggregated()
    kpis = calculate_kpis(aggregated)

    dashboard_payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "execution": {"command": execution_cmd, "return_code": execute_rc},
        "query": query,
        "results": aggregated,
        "kpi": kpis,
    }
    out = Path("reporting/output/dashboard_live.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(dashboard_payload, indent=2), encoding="utf-8")
    return dashboard_payload
