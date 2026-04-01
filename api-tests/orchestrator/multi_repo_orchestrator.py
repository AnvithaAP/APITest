from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

from reporting.aggregator_client import merge_canonical_reports


def run_repo(repo_path: str, query: str, runner: str) -> int:
    cmd = [
        sys.executable,
        "orchestrator/execution_router.py",
        "--runner",
        runner,
        "--query",
        query,
    ]
    return subprocess.call(cmd, cwd=repo_path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run orchestrated test execution across multiple repositories")
    parser.add_argument("--repos-file", required=True, help="JSON file: { repos: [{name, path, query?}] }")
    parser.add_argument("--default-query", default="scope=api")
    parser.add_argument("--runner", choices=["pytest", "k6", "gatling"], default="pytest")
    parser.add_argument("--aggregate-out", default="artifacts/aggregated_canonical.json")
    args = parser.parse_args()

    payload = json.loads(Path(args.repos_file).read_text(encoding="utf-8"))
    canonical_paths: list[str] = []
    failures: list[str] = []

    for repo in payload.get("repos", []):
        repo_name = repo.get("name", repo["path"])
        query = repo.get("query", args.default_query)
        rc = run_repo(repo["path"], query, args.runner)
        if rc != 0:
            failures.append(repo_name)
            continue

        candidate = Path(repo["path"]) / "artifacts" / "canonical_run.json"
        if candidate.exists():
            canonical_paths.append(str(candidate))

    if canonical_paths:
        merge_canonical_reports(canonical_paths, args.aggregate_out)

    if failures:
        print(f"Orchestration failed in: {', '.join(failures)}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
