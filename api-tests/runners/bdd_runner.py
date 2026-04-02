from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import argparse
import json
import subprocess

from reporting.canonical_formatter import build_canonical_report, write_canonical_report
from tagging.tag_parser import parse_query


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", default="")
    args = parser.parse_args()

    report_path = Path("artifacts/pytest_report.json")
    cmd = [sys.executable, "-m", "pytest", "functional/steps", "functional/features", f"--tag-query={args.query}"]
    rc = subprocess.call(cmd)

    if not report_path.exists():
        return rc

    raw = json.loads(report_path.read_text(encoding="utf-8"))
    canonical = build_canonical_report(raw, args.query, parse_query(args.query), source_repo="api-tests", repo_type="bdd")
    for result in canonical.get("results", []):
        duration = float(result.get("duration", 0) or 0)
        result["metrics"] = {"latency": duration, "error": result.get("status") == "failed"}
    write_canonical_report(canonical, output_path="reporting/output/canonical.json")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
