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

    def _ensure_columns(self, conn: sqlite3.Connection) -> None:
        columns = {row[1] for row in conn.execute("PRAGMA table_info(run_metrics)").fetchall()}
        if "scope" not in columns:
            conn.execute("ALTER TABLE run_metrics ADD COLUMN scope TEXT DEFAULT 'api'")
