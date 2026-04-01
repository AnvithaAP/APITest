from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from pathlib import Path
import subprocess
import sys
import time

from reporting.aggregator_client import merge_canonical_reports


def run_repo(repo: dict, default_query: str, runner: str) -> dict:
    repo_name = repo.get("name", repo["path"])
    query = repo.get("query", default_query)
    started = time.time()
    cmd = [
        sys.executable,
        "orchestrator/execution_router.py",
        "--runner",
        runner,
        "--query",
        query,
    ]
    rc = subprocess.call(cmd, cwd=repo["path"])
    duration = time.time() - started
    canonical = Path(repo["path"]) / "artifacts" / "canonical_run.json"
    return {
        "name": repo_name,
        "path": repo["path"],
        "query": query,
        "rc": rc,
        "duration_s": round(duration, 3),
        "canonical": str(canonical) if canonical.exists() else "",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run orchestrated test execution across multiple repositories")
    parser.add_argument("--repos-file", required=True, help="JSON file: { repos: [{name, path, query?}] }")
    parser.add_argument("--default-query", default="scope=api")
    parser.add_argument("--runner", choices=["pytest", "k6", "gatling"], default="pytest")
    parser.add_argument("--parallel", type=int, default=4)
    parser.add_argument("--aggregate-out", default="artifacts/aggregated_canonical.json")
    parser.add_argument("--results-out", default="artifacts/orchestrator_results.json")
    args = parser.parse_args()

    payload = json.loads(Path(args.repos_file).read_text(encoding="utf-8"))
    repos = payload.get("repos", [])
    results: list[dict] = []

    workers = max(1, min(args.parallel, len(repos) or 1))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(run_repo, repo, args.default_query, args.runner) for repo in repos]
        for future in as_completed(futures):
            results.append(future.result())

    canonical_paths = [r["canonical"] for r in results if r["canonical"]]
    if canonical_paths:
        merge_canonical_reports(canonical_paths, args.aggregate_out, copy_allure_to="artifacts/allure-results-merged")

    out = Path(args.results_out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(
            {
                "runner": args.runner,
                "total_repos": len(repos),
                "successful": sum(1 for r in results if r["rc"] == 0),
                "failed": [r["name"] for r in results if r["rc"] != 0],
                "results": sorted(results, key=lambda x: x["name"]),
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    failed = [r["name"] for r in results if r["rc"] != 0]
    if failed:
        print(f"Orchestration failed in: {', '.join(failed)}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
