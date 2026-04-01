from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import argparse
import json
import subprocess
import sys

from history.html_trend_report import render_trend_html
from history.sqlite_manager import SQLiteManager
from reporting.canonical_formatter import build_canonical_report, write_canonical_report
from reporting.html_report import render_html_report
from tagging.tag_parser import compile_query_expression, evaluate_query_expression


def _filter_tests(pytest_report: dict, query: str) -> None:
    if not query:
        return
    expression = compile_query_expression(query)

    filtered = []
    for test in pytest_report.get("tests", []):
        tags = test.get("tags", {})
        if evaluate_query_expression(expression, tags):
            filtered.append(test)

    pytest_report["tests"] = filtered
    summary = pytest_report.get("summary", {})
    summary["total"] = len(filtered)
    summary["passed"] = sum(1 for t in filtered if t.get("outcome") == "passed")
    summary["failed"] = sum(1 for t in filtered if t.get("outcome") == "failed")
    summary["skipped"] = sum(1 for t in filtered if t.get("outcome") == "skipped")
    pytest_report["summary"] = summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", default="")
    parser.add_argument("--tag-guard-mode", choices=["strict", "warn"], default="strict")
    parser.add_argument("--tag-autofix", action="store_true")
    args = parser.parse_args()

    report_path = Path("artifacts/pytest_report.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "functional",
        "governance",
        f"--tag-guard-mode={args.tag_guard_mode}",
    ]
    if args.tag_autofix:
        cmd.append("--tag-autofix")

    rc = subprocess.call(cmd)

    if not report_path.exists():
        return rc

    raw = json.loads(report_path.read_text(encoding="utf-8"))
    _filter_tests(raw, args.query)

    canonical = build_canonical_report(raw, args.query)
    write_canonical_report(canonical)
    render_html_report(canonical)

    db = SQLiteManager()
    failed = canonical["summary"]["failed"]
    total = canonical["summary"]["total"] or 1
    error_rate = failed / total

    for result in canonical["results"]:
        db.insert_metric(
            run_id=canonical["run_id"],
            timestamp=canonical["timestamp"],
            api_name=result["test_name"],
            latency=float(result["duration"]),
            error_rate=error_rate,
            throughput=float(total),
        )

    render_trend_html(db.fetch_all(), "artifacts/history_trends.html")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
