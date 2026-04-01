from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import argparse
import subprocess
import sys


def main() -> int:
    parser = argparse.ArgumentParser(description="Execution router for API test framework")
    parser.add_argument("--runner", choices=["pytest", "k6", "gatling"], required=True)
    parser.add_argument("--query", default="")
    parser.add_argument("--script", default="")
    args = parser.parse_args()

    if args.runner == "pytest":
        cmd = [sys.executable, "runners/pytest_runner.py", "--query", args.query]
    elif args.runner == "k6":
        cmd = [sys.executable, "runners/k6_runner.py", "--query", args.query, "--script", args.script]
    else:
        cmd = [sys.executable, "runners/gatling_runner.py", "--query", args.query]

    return subprocess.call(cmd)


if __name__ == "__main__":
    raise SystemExit(main())
