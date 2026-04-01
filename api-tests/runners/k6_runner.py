from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import argparse
import subprocess


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--script", default="performance/latency/k6_latency.js")
    parser.add_argument("--query", default="")
    args = parser.parse_args()

    cmd = ["k6", "run", args.script]
    return subprocess.call(cmd)


if __name__ == "__main__":
    raise SystemExit(main())
