from __future__ import annotations

import json
import statistics
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

        total_duration = sum(t.get("call", {}).get("duration", 0.0) for t in tests)
        pass_rate = round((passed / total) * 100, 2) if total else 0.0
        fail_rate = round((failed / total) * 100, 2) if total else 0.0
        avg_duration = round((total_duration / total), 4) if total else 0.0

        by_concern: dict[str, int] = {}
        for test in tests:
            concern = test.get("tags", {}).get("concern", "unknown")
            by_concern[concern] = by_concern.get(concern, 0) + 1

        timeline = SQLiteManager(self.history_db_path).get_timeline()
        latency_trend = [point.get("latency_avg_ms", 0.0) for point in timeline]
        error_trend = [point.get("error_rate_avg", 0.0) for point in timeline]
        throughput_trend = [point.get("throughput_avg", 0.0) for point in timeline]

        flakiness = self._compute_flakiness(tests)
        regression_drift = self._compute_regression_drift(timeline, pass_rate)
        throughput = round(total / total_duration, 3) if total and total_duration > 0 else 0.0

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
                "throughput_tests_per_second": throughput,
                "flaky_tests": flakiness["flaky_count"],
                "flaky_rate": flakiness["flaky_rate"],
                "regression_drift_pct": regression_drift,
            },
            "trends": {
                "latency_avg_ms": latency_trend,
                "latency_direction": self._trend_direction(latency_trend, lower_is_better=True),
                "error_rate": error_trend,
                "error_rate_direction": self._trend_direction(error_trend, lower_is_better=True),
                "throughput": throughput_trend,
                "throughput_direction": self._trend_direction(throughput_trend, lower_is_better=False),
            },
            "quality": {
                "flakiness": flakiness["flaky_rate"],
                "flaky_count": flakiness["flaky_count"],
                "regression_stability": round(100 - (flakiness["flaky_rate"] * 100), 2),
                "regression_drift_pct": regression_drift,
            },
            "distribution": {"concern": by_concern},
        }

    def _compute_flakiness(self, tests: list[dict]) -> dict[str, float]:
        if not tests:
            return {"flaky_count": 0, "flaky_rate": 0.0}
        by_test: dict[str, set[str]] = {}
        for test in tests:
            nodeid = test.get("nodeid", "")
            outcome = test.get("outcome", "unknown")
            by_test.setdefault(nodeid, set()).add(outcome)

        flaky_count = sum(1 for outcomes in by_test.values() if len(outcomes) > 1)
        return {
            "flaky_count": flaky_count,
            "flaky_rate": round(flaky_count / max(len(by_test), 1), 4),
        }

    def _compute_regression_drift(self, timeline: list[dict], current_pass_rate: float) -> float:
        if not timeline:
            return 0.0
        historical_pass_rates = [round((1 - point.get("error_rate_avg", 0.0)) * 100, 2) for point in timeline]
        baseline = statistics.mean(historical_pass_rates) if historical_pass_rates else current_pass_rate
        return round(current_pass_rate - baseline, 2)

    def _trend_direction(self, points: list[float], lower_is_better: bool) -> str:
        if len(points) < 2:
            return "stable"
        delta = points[-1] - points[0]
        if abs(delta) < 1e-9:
            return "stable"
        improving = delta < 0 if lower_is_better else delta > 0
        return "improving" if improving else "degrading"

    def write(self, output_path: str | None = None) -> Path:
        env_values = load_env_file("config/runtime.env")
        destination = Path(output_path or env_values.get("KPI_REPORT_PATH", "artifacts/kpi_report.json"))
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(self.compute(), indent=2), encoding="utf-8")
        return destination


if __name__ == "__main__":
    written = KPIEngine().write()
    print(f"KPI report generated: {written}")
