from __future__ import annotations

from fastapi import FastAPI, Query

from history.sqlite_manager import SQLiteManager

app = FastAPI(title="Live Metrics Backend", version="1.0.0")


@app.get("/health")
def health() -> dict:
    return {"ok": True}


@app.get("/metrics")
def metrics(db_path: str = Query(default="artifacts/history.db"), limit: int = Query(default=100, ge=1, le=2000)) -> dict:
    db = SQLiteManager(db_path)
    rows = db.get_recent_runs(limit=limit)
    timeline = db.get_timeline()
    return {
        "total_runs": len(rows),
        "recent": rows,
        "timeline": timeline,
    }
