from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

from dashboard.dashboard import render_dashboard
from integrations.ado_client import write_ado_submission
from orchestrator.gitlab_orchestrator import GitLabOrchestrator, load_targets
from reporting.aggregator_client import merge_canonical_reports


def main() -> int:
    parser = argparse.ArgumentParser(description="Enterprise orchestration: GitLab multi-repo + aggregation + dashboard + ADO payload")
    parser.add_argument("--gitlab-repos-file", default="", help="Optional JSON for GitLab pipeline triggers")
    parser.add_argument("--gitlab-url", default="https://gitlab.com")
    parser.add_argument("--gitlab-token", default="")
    parser.add_argument("--gitlab-output", default="artifacts/gitlab_pipeline_triggers.json")
    parser.add_argument("--local-repos-file", default="", help="Optional local repos.json to execute repositories")
    parser.add_argument("--query", default="scope=api")
    parser.add_argument("--runner", choices=["pytest", "k6", "gatling"], default="pytest")
    parser.add_argument("--parallel", type=int, default=4)
    parser.add_argument("--aggregate-out", default="artifacts/aggregated_canonical.json")
    parser.add_argument("--dashboard-out", default="artifacts/dashboard.html")
    parser.add_argument("--ado-out", default="artifacts/ado_submission.json")
    args = parser.parse_args()

    rc = 0

    if args.gitlab_repos_file and args.gitlab_token:
        payload = json.loads(Path(args.gitlab_repos_file).read_text(encoding="utf-8"))
        targets = load_targets(payload)
        results = GitLabOrchestrator(args.gitlab_url, args.gitlab_token).trigger_multi_repo(targets, parallel=args.parallel)
        out = Path(args.gitlab_output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps({"schema": "gitlab-multi-repo-v1", "results": results}, indent=2), encoding="utf-8")
        if any(item.get("status") != "triggered" for item in results):
            rc = 1

    if args.local_repos_file:
        command = [
            sys.executable,
            "orchestrator/multi_repo_orchestrator.py",
            "--repos-file",
            args.local_repos_file,
            "--default-query",
            args.query,
            "--runner",
            args.runner,
            "--parallel",
            str(args.parallel),
            "--aggregate-out",
            args.aggregate_out,
        ]
        step_rc = subprocess.call(command)
        if step_rc != 0:
            rc = step_rc

    canonical_paths = _canonical_paths_from_results("artifacts/orchestrator_results.json")
    if canonical_paths and not Path(args.aggregate_out).exists():
        merge_canonical_reports(canonical_paths, args.aggregate_out, copy_allure_to="artifacts/allure-results-merged")

    if Path(args.aggregate_out).exists():
        render_dashboard(args.aggregate_out, args.dashboard_out)
        write_ado_submission(args.aggregate_out, args.ado_out)

    return rc


def _canonical_paths_from_results(path: str) -> list[str]:
    results_file = Path(path)
    if not results_file.exists():
        return []
    payload = json.loads(results_file.read_text(encoding="utf-8"))
    paths: list[str] = []
    for item in payload.get("results", []):
        canonical = item.get("canonical")
        if canonical and Path(canonical).exists():
            paths.append(canonical)
    return paths


if __name__ == "__main__":
    raise SystemExit(main())
