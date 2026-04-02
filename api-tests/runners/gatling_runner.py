from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import argparse
import subprocess
from datetime import datetime, timezone
import uuid

from reporting.canonical_formatter import write_canonical_report
from tagging.tag_parser import parse_query


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--simulation", default="simulations.BasicSimulation")
    parser.add_argument("--query", default="")
    args = parser.parse_args()
    cmd = ["gatling", "-s", args.simulation]
    rc = subprocess.call(cmd)

    query_tags = parse_query(args.query)
    canonical = {
        "run_id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source_repo": "api-tests",
        "repo_type": "performance",
        "results": [
            {
                "test_name": args.simulation,
                "status": "passed" if rc == 0 else "failed",
                "duration": 0,
                "tags": {
                    "scope": (query_tags.get("scope") or ["api"])[0],
                    "intent": (query_tags.get("intent") or ["performance"])[0],
                    "concern": (query_tags.get("concern") or ["latency"])[0],
                    "type": (query_tags.get("type") or ["load"])[0],
                },
                "metrics": {"latency": 0, "error": rc != 0},
            }
        ],
        "summary": {"total": 1, "passed": 1 if rc == 0 else 0, "failed": 0 if rc == 0 else 1, "skipped": 0},
    }
    write_canonical_report(canonical, output_path="reporting/output/canonical.json")

    return rc


if __name__ == "__main__":
    raise SystemExit(main())
