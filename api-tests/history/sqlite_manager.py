from __future__ import annotations

import sqlite3
from pathlib import Path


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS run_metrics (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  run_id TEXT NOT NULL,
  timestamp TEXT NOT NULL,
  api_name TEXT NOT NULL,
  scope TEXT DEFAULT 'api',
  latency REAL DEFAULT 0,
  error_rate REAL DEFAULT 0,
  throughput REAL DEFAULT 0
);
"""


class SQLiteManager:
    def __init__(self, db_path: str = "artifacts/history.db") -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.execute(SCHEMA_SQL)
        self._ensure_columns(conn)
        conn.commit()
        return conn

    def insert_metric(
        self,
        run_id: str,
        timestamp: str,
        api_name: str,
        latency: float,
        error_rate: float,
        throughput: float,
        scope: str = "api",
    ) -> None:
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO run_metrics(run_id,timestamp,api_name,scope,latency,error_rate,throughput) VALUES(?,?,?,?,?,?,?)",
                (run_id, timestamp, api_name, scope, latency, error_rate, throughput),
            )
            conn.commit()

    def fetch_all(self) -> list[tuple]:
        with self.connect() as conn:
            return conn.execute("SELECT run_id,timestamp,api_name,latency,error_rate,throughput FROM run_metrics ORDER BY id").fetchall()

    def get_recent_runs(self, limit: int = 50) -> list[dict]:
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT run_id,timestamp,api_name,scope,latency,error_rate,throughput FROM run_metrics ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [
            {
                "run_id": r[0],
                "timestamp": r[1],
                "api_name": r[2],
                "scope": r[3],
                "latency": r[4],
                "error_rate": r[5],
                "throughput": r[6],
            }
            for r in rows
        ]

    def get_timeline(self) -> list[dict]:
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT timestamp, AVG(latency), AVG(error_rate), AVG(throughput), COUNT(*) FROM run_metrics GROUP BY timestamp ORDER BY timestamp"
            ).fetchall()
        return [
            {
                "timestamp": r[0],
                "latency_avg_ms": round(r[1] or 0, 3),
                "error_rate_avg": round(r[2] or 0, 5),
                "throughput_avg": round(r[3] or 0, 3),
                "sample_size": r[4],
            }
            for r in rows
        ]

    def _ensure_columns(self, conn: sqlite3.Connection) -> None:
        columns = {row[1] for row in conn.execute("PRAGMA table_info(run_metrics)").fetchall()}
        if "scope" not in columns:
            conn.execute("ALTER TABLE run_metrics ADD COLUMN scope TEXT DEFAULT 'api'")
