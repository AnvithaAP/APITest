from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import argparse
import json
import subprocess

from history.html_trend_report import render_trend_html
from history.sqlite_manager import SQLiteManager
from reporting.allure_adapter import write_allure_results
from reporting.canonical_formatter import build_canonical_report, write_canonical_report
from reporting.html_report import render_html_report
from tagging.tag_parser import parse_query


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", default="")
    parser.add_argument("--parallel", type=int, default=0)
    parser.add_argument("--retries", type=int, default=0)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--repo", default="api-tests")
    args = parser.parse_args()

    report_path = Path("artifacts/pytest_report.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [sys.executable, "-m", "pytest", "functional", "governance", f"--tag-query={args.query}"]

    if args.dry_run:
        cmd.append("--collect-only")

    if args.parallel > 0:
        cmd.extend(["-n", str(args.parallel)])

    if args.retries > 0:
        cmd.extend(["--reruns", str(args.retries)])

    rc = subprocess.call(cmd)

    if args.dry_run or not report_path.exists():
        return rc

    raw = json.loads(report_path.read_text(encoding="utf-8"))
    query_tags = parse_query(args.query)

    canonical = build_canonical_report(raw, args.query, query_tags, source_repo=args.repo)
    write_canonical_report(canonical)
    write_allure_results(canonical)
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
