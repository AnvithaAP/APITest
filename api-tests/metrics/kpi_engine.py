from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.config import load_env_file, load_runtime_config
from history.sqlite_manager import SQLiteManager


class KPIEngine:
    def __init__(
        self,
        report_path: str = "artifacts/pytest_report.json",
        history_db_path: str = "artifacts/history.db",
    ) -> None:
        self.report_path = Path(report_path)
        self.history_db_path = history_db_path

    def compute(self) -> dict:
        if not self.report_path.exists():
            raise FileNotFoundError(f"Pytest report not found: {self.report_path}")

        payload = json.loads(self.report_path.read_text(encoding="utf-8"))
        summary = payload.get("summary", {})
        tests = payload.get("tests", [])

        total = int(summary.get("total", len(tests)))
        passed = int(summary.get("passed", 0))
        failed = int(summary.get("failed", 0))
        skipped = int(summary.get("skipped", 0))

        pass_rate = round((passed / total) * 100, 2) if total else 0.0
        fail_rate = round((failed / total) * 100, 2) if total else 0.0
        avg_duration = round(
            (sum(t.get("call", {}).get("duration", 0.0) for t in tests) / total), 4
        ) if total else 0.0

        by_concern: dict[str, int] = {}
        for test in tests:
            concern = test.get("tags", {}).get("concern", "unknown")
            by_concern[concern] = by_concern.get(concern, 0) + 1

        timeline = SQLiteManager(self.history_db_path).get_timeline()
        latency_trend = [point.get("latency_avg_ms", 0.0) for point in timeline]
        error_trend = [point.get("error_rate_avg", 0.0) for point in timeline]
        throughput_trend = [point.get("throughput_avg", 0.0) for point in timeline]

        flakiness = self._compute_flakiness(tests)
        regression_stability = round(100 - (flakiness * 100), 2)

        runtime = load_runtime_config()
        return {
            "environment": runtime.environment,
            "base_url": runtime.base_url,
            "summary": {
                "total": total,
                "passed": passed,
                "failed": failed,
                "skipped": skipped,
                "pass_rate": pass_rate,
                "fail_rate": fail_rate,
                "avg_duration_seconds": avg_duration,
                "error_rate": round((failed / total), 5) if total else 0.0,
                "throughput_tests_per_second": round((total / max(sum(t.get('call', {}).get('duration', 0.0) for t in tests), 1e-9)), 3) if total else 0.0,
            },
            "trends": {
                "latency_avg_ms": latency_trend,
                "error_rate": error_trend,
                "throughput": throughput_trend,
            },
            "quality": {
                "flakiness": round(flakiness, 4),
                "regression_stability": regression_stability,
            },
            "distribution": {"concern": by_concern},
        }

    def _compute_flakiness(self, tests: list[dict]) -> float:
        if not tests:
            return 0.0
        by_test: dict[str, set[str]] = {}
        for test in tests:
            nodeid = test.get("nodeid", "")
            outcome = test.get("outcome", "unknown")
            by_test.setdefault(nodeid, set()).add(outcome)

        flaky_count = sum(1 for outcomes in by_test.values() if len(outcomes) > 1)
        return flaky_count / max(len(by_test), 1)

    def write(self, output_path: str | None = None) -> Path:
        env_values = load_env_file("config/runtime.env")
        destination = Path(output_path or env_values.get("KPI_REPORT_PATH", "artifacts/kpi_report.json"))
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(self.compute(), indent=2), encoding="utf-8")
        return destination


if __name__ == "__main__":
    written = KPIEngine().write()
    print(f"KPI report generated: {written}")
