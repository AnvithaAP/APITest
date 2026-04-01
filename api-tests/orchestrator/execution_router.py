from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import argparse
import json
import subprocess
import sys


def _build_command(runner: str, query: str, script: str, tag_guard_mode: str, tag_autofix: bool) -> list[str]:
    if runner == "pytest":
        cmd = [
            sys.executable,
            "runners/pytest_runner.py",
            "--query",
            query,
            "--tag-guard-mode",
            tag_guard_mode,
        ]
        if tag_autofix:
            cmd.append("--tag-autofix")
        return cmd
    if runner == "k6":
        return [sys.executable, "runners/k6_runner.py", "--query", query, "--script", script]
    return [sys.executable, "runners/gatling_runner.py", "--query", query]


def _run_single_repo(cmd: list[str], repo_path: Path) -> int:
    return subprocess.call(cmd, cwd=repo_path)


def _run_multi_repo(cmd: list[str], repos_file: Path) -> int:
    payload = json.loads(repos_file.read_text(encoding="utf-8"))
    repos = payload.get("repos", [])
    exit_codes = []
    for repo in repos:
        path = Path(repo["path"])
        if not path.exists():
            print(f"Skipping missing repo path: {path}")
            exit_codes.append(1)
            continue
        print(f"Running orchestrator for repo: {repo.get('name', path.name)} ({path})")
        exit_codes.append(_run_single_repo(cmd, path))
    return max(exit_codes) if exit_codes else 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Execution router for API test framework")
    parser.add_argument("--runner", choices=["pytest", "k6", "gatling"], required=True)
    parser.add_argument("--query", default="")
    parser.add_argument("--script", default="")
    parser.add_argument("--repos-file", default="")
    parser.add_argument("--tag-guard-mode", default="strict", choices=["strict", "warn"])
    parser.add_argument("--tag-autofix", action="store_true")
    args = parser.parse_args()

    cmd = _build_command(args.runner, args.query, args.script, args.tag_guard_mode, args.tag_autofix)

    if args.repos_file:
        return _run_multi_repo(cmd, Path(args.repos_file))
    return subprocess.call(cmd)


if __name__ == "__main__":
    raise SystemExit(main())
