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
from reporting.canonical_formatter import build_canonical_report, write_canonical_report
from reporting.html_report import render_html_report
from tagging.tag_parser import compile_query_expression, evaluate_query_expression



    args = parser.parse_args()

    report_path = Path("artifacts/pytest_report.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)



    rc = subprocess.call(cmd)

    if args.dry_run or not report_path.exists():
        return rc

    raw = json.loads(report_path.read_text(encoding="utf-8"))

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
