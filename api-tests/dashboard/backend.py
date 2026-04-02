from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

from history.sqlite_manager import SQLiteManager
from orchestrator.query_engine import parse_nested_ui_tree, parse_ui_selections


class TagQueryRequest(BaseModel):
    scope: list[str] = []
    intent: list[str] = []
    concern: list[str] = []
    type: list[str] = []
    module: list[str] = []
    operator: str = "AND"
    tree: dict | None = None


app = FastAPI(title="Enterprise Dashboard Backend", version="1.0.0")


@app.get("/health")
def health() -> dict:
    return {"ok": True}


@app.get("/dashboard/summary")
def dashboard_summary(db_path: str = Query(default="artifacts/history.db")) -> dict:
    db = SQLiteManager(db_path)
    rows = db.get_recent_runs(limit=50)
    return {
        "total_runs": len(rows),
        "rows": rows,
    }


@app.get("/dashboard/trends")
def dashboard_trends(db_path: str = Query(default="artifacts/history.db")) -> dict:
    db = SQLiteManager(db_path)
    return {"timeline": db.get_timeline()}


@app.post("/query/build")
def build_query(req: TagQueryRequest) -> dict:
    if req.tree:
        parsed = parse_nested_ui_tree(req.tree)
    else:
        filters = {
            "scope": req.scope,
            "intent": req.intent,
            "concern": req.concern,
            "type": req.type,
            "module": req.module,
        }
        parsed = parse_ui_selections(filters, group_operator=req.operator)

    query_groups = [[f"{clause.key}={','.join(clause.values)}" for clause in group] for group in parsed.groups]
    return {"groups": query_groups, "operator": req.operator}


@app.get("/artifacts/canonical")
def canonical(artifact_path: str = Query(default="artifacts/aggregated_canonical.json")) -> dict:
    path = Path(artifact_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Missing {artifact_path}")
    return json.loads(path.read_text(encoding="utf-8"))
