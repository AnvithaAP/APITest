from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, Query

from history.sqlite_manager import SQLiteManager

app = FastAPI(title="Live Metrics Backend", version="2.0.0")


def _safe_load_json(path: str) -> dict:
    file = Path(path)
    if not file.exists():
        return {}
    return json.loads(file.read_text(encoding="utf-8"))


@app.get("/health")
def health() -> dict:
    return {"ok": True}


@app.get("/metrics")
def metrics(
    db_path: str = Query(default="artifacts/history.db"),
    limit: int = Query(default=100, ge=1, le=2000),
    aggregated_path: str = Query(default="artifacts/aggregated_canonical.json"),
    kpi_path: str = Query(default="artifacts/kpi_report.json"),
) -> dict:
    db = SQLiteManager(db_path)
    rows = db.get_recent_runs(limit=limit)
    timeline = db.get_timeline()
    aggregated = _safe_load_json(aggregated_path)
    kpi = _safe_load_json(kpi_path)

    dashboard = aggregated.get("dashboard", {})
    return {
        "total_runs": len(rows),
        "recent": rows,
        "timeline": timeline,
        "aggregated": {
            "summary": aggregated.get("summary", {}),
            "kpis": dashboard.get("kpis", {}),
            "release_readiness": dashboard.get("release_readiness", {}),
            "repo_cards": dashboard.get("repo_cards", []),
        },
        "kpi": kpi,
    }
