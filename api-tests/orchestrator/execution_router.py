from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import argparse
import subprocess

from orchestrator.query_engine import parse_query


def main() -> int:
    parser = argparse.ArgumentParser(description="Execution router for API test framework")
    parser.add_argument("--runner", choices=["pytest", "k6", "gatling", "distributed"], required=True)
    parser.add_argument("--query", default="")
    parser.add_argument("--script", default="")
    parser.add_argument("--parallel", type=int, default=0)
    parser.add_argument("--retries", type=int, default=0)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--repos-file", default="")
    parser.add_argument("--repo", default="api-tests")
    parser.add_argument("--repo-type", default="api")
    parser.add_argument("--aggregate-out", default="artifacts/aggregated_canonical.json")
    parser.add_argument("--results-out", default="artifacts/orchestrator_results.json")
    args = parser.parse_args()

    if args.query.strip():
        parse_query(args.query)

    if args.repos_file:
        cmd = [
            sys.executable,
            "orchestrator/multi_repo_orchestrator.py",
            "--repos-file",
            args.repos_file,
            "--default-query",
            args.query,
            "--runner",
            args.runner,
            "--aggregate-out",
            args.aggregate_out,
            "--parallel",
            str(args.parallel or 4),
            "--results-out",
            args.results_out,
        ]
    elif args.runner == "pytest":
        cmd = [sys.executable, "runners/pytest_runner.py", "--query", args.query, "--repo", args.repo, "--repo-type", args.repo_type]
        if args.parallel > 0:
            cmd.extend(["--parallel", str(args.parallel)])
        if args.retries > 0:
            cmd.extend(["--retries", str(args.retries)])
        if args.dry_run:
            cmd.append("--dry-run")
    elif args.runner == "k6":
        cmd = [sys.executable, "runners/k6_runner.py", "--query", args.query, "--script", args.script]
    elif args.runner == "gatling":
        cmd = [sys.executable, "runners/gatling_runner.py", "--query", args.query]
    else:
        cmd = [sys.executable, "runners/distributed_runner.py", "--query", args.query, "--repo", args.repo, "--repo-type", args.repo_type]
        if args.parallel > 0:
            cmd.extend(["--nodes", str(args.parallel)])

    return subprocess.call(cmd)


if __name__ == "__main__":
    raise SystemExit(main())
