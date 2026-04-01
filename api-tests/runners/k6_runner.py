from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import argparse
import subprocess

from tagging.tag_parser import parse_query


K6_SCRIPT_BY_CONCERN = {
    "latency": "performance/latency/k6_latency.js",
    "capacity": "performance/capacity/k6_capacity.js",
    "scalability": "performance/scalability/k6_scalability.js",
    "stability": "performance/stability/k6_stability.js",
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--script", default="")
    parser.add_argument("--query", default="")
    args = parser.parse_args()

    script = args.script
    if not script and args.query:
        concern = parse_query(args.query).get("concern", "")
        script = K6_SCRIPT_BY_CONCERN.get(concern, "")

    script = script or "performance/latency/k6_latency.js"
    if not Path(script).exists():
        raise FileNotFoundError(f"k6 script not found: {script}")

    cmd = ["k6", "run", script]
    return subprocess.call(cmd)


if __name__ == "__main__":
    raise SystemExit(main())
