from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import argparse
import subprocess


def main() -> int:
    parser = argparse.ArgumentParser(description="Execution router for API test framework")
    parser.add_argument("--runner", choices=["pytest", "k6", "gatling"], required=True)
    parser.add_argument("--query", default="")
    parser.add_argument("--script", default="")
    parser.add_argument("--parallel", type=int, default=0)
    parser.add_argument("--retries", type=int, default=0)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.runner == "pytest":
        cmd = [sys.executable, "runners/pytest_runner.py", "--query", args.query]
        if args.parallel > 0:
            cmd.extend(["--parallel", str(args.parallel)])
        if args.retries > 0:
            cmd.extend(["--retries", str(args.retries)])
        if args.dry_run:
            cmd.append("--dry-run")
    elif args.runner == "k6":
        cmd = [sys.executable, "runners/k6_runner.py", "--query", args.query, "--script", args.script]
    else:
        cmd = [sys.executable, "runners/gatling_runner.py", "--query", args.query]

    return subprocess.call(cmd)


if __name__ == "__main__":
    raise SystemExit(main())
