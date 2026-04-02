from __future__ import annotations

import json
from pathlib import Path
from typing import Any



def latency_trend(results: list[dict[str, Any]]) -> list[float]:
    return [float(r.get("metrics", {}).get("latency", r.get("duration", 0)) or 0) for r in results]


def error_rate(results: list[dict[str, Any]]) -> float:
    total = len(results)
    failed = sum(1 for r in results if r.get("status") == "failed")
    return round(failed / total, 5) if total else 0.0


def throughput(results: list[dict[str, Any]]) -> float:
    total_time = sum(float(r.get("duration", 0) or 0) for r in results)
    return round(len(results) / total_time, 5) if total_time else 0.0


def flaky_tests(history: list[dict[str, Any]]) -> list[str]:
    outcomes_by_test: dict[str, list[str]] = {}
    for row in history:
        name = row.get("test_name", "")
        status = row.get("status", "unknown")
        outcomes_by_test.setdefault(name, []).append(status)

    flaky: list[str] = []
    for test_name, outcomes in outcomes_by_test.items():
        transitions = sum(1 for i in range(1, len(outcomes)) if outcomes[i] != outcomes[i - 1])
        if transitions > 0:
            flaky.append(test_name)
    return sorted(flaky)


def regression_drift(current: list[dict[str, Any]], baseline: list[dict[str, Any]]) -> float:
    current_latency = latency_trend(current)
    baseline_latency = latency_trend(baseline)
    if not baseline_latency:
        return 0.0

    current_avg = sum(current_latency) / max(len(current_latency), 1)
    baseline_avg = sum(baseline_latency) / len(baseline_latency)
    if baseline_avg == 0:
        return 0.0
    return round(((current_avg - baseline_avg) / baseline_avg) * 100, 3)


def calculate_kpis(aggregated_results: dict[str, Any]) -> dict[str, Any]:
    results = aggregated_results.get("results", [])
    runs = aggregated_results.get("runs", [])
    baseline = runs[-2].get("results", []) if len(runs) > 1 else []

    total = len(results)
    passed = sum(1 for r in results if r.get("status") == "passed")

    return {
        "pass_rate": round(passed / total, 5) if total else 0.0,
        "error_rate": error_rate(results),
        "latency_trend": latency_trend(results),
        "throughput": throughput(results),
        "flaky_tests": flaky_tests(results),
        "regression_drift": regression_drift(results, baseline),
        "total_tests": total,
    }


class KPIEngine:
    def __init__(self, aggregated_path: str = "reporting/output/aggregated_results.json") -> None:
        self.aggregated_path = Path(aggregated_path)

    def compute(self) -> dict[str, Any]:
        if not self.aggregated_path.exists():
            return calculate_kpis({"results": [], "runs": []})
        payload = json.loads(self.aggregated_path.read_text(encoding="utf-8"))
        return calculate_kpis(payload)

    def write(self, output_path: str = "reporting/output/kpi_report.json") -> Path:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(self.compute(), indent=2), encoding="utf-8")
        return out
