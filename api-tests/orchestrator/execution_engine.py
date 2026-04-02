from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from pathlib import Path
import subprocess
import sys
import time
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from metrics.kpi_dashboard import generate_dashboard
from orchestrator.query_engine import parse_query


def _discover_tests(query: str) -> list[str]:
    cmd = [sys.executable, "-m", "pytest", "functional", "functional/features", "performance", "governance", "--collect-only", "-q"]
    if query:
        cmd.append(f"--tag-query={query}")
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if proc.returncode not in {0, 5}:
        raise RuntimeError(f"pytest collection failed: {proc.stderr or proc.stdout}")

    tests: list[str] = []
    for line in proc.stdout.splitlines():
        line = line.strip()
        if "::" in line and ".py::" in line:
            tests.append(line)
    return tests


def _chunk(items: list[str], parts: int) -> list[list[str]]:
    if parts <= 1:
        return [items]
    chunks = [[] for _ in range(parts)]
    for idx, item in enumerate(items):
        chunks[idx % parts].append(item)
    return chunks


def _run_pytest_chunk(tests: list[str], query: str, dry_run: bool) -> dict[str, Any]:
    started = time.time()
    if not tests:
        return {"rc": 0, "selected": [], "duration_s": 0.0}

    cmd = [sys.executable, "-m", "pytest", *tests]
    if query:
        cmd.append(f"--tag-query={query}")
    if dry_run:
        cmd.append("--collect-only")

    rc = subprocess.call(cmd)
    return {
        "rc": rc,
        "selected": tests,
        "duration_s": round(time.time() - started, 3),
    }


def run_execution_engine(
    query: str,
    dry_run: bool,
    parallel: int,
    atomic: bool,
    runner: str,
    out: Path,
) -> int:
    parse_query(query)
    tests = _discover_tests(query)

    if dry_run:
        payload = {
            "mode": "dry-run",
            "runner": runner,
            "query": query,
            "selected_tests": tests,
            "count": len(tests),
        }
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return 0

    if runner in {"k8s", "gitlab", "docker"}:
        cmd = [sys.executable, "runners/distributed_runner.py", "--query", query, "--execution-mode", "k8s"]
        if parallel > 0:
            cmd.extend(["--nodes", str(parallel)])
        rc = subprocess.call(cmd)
        return rc

    chunks = [[t] for t in tests] if atomic else _chunk(tests, max(1, parallel))
    results: list[dict[str, Any]] = []
    max_workers = min(len(chunks), max(1, parallel)) if parallel > 1 else 1

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = [pool.submit(_run_pytest_chunk, chunk, query, False) for chunk in chunks if chunk]
        for future in as_completed(futures):
            results.append(future.result())

    payload = {
        "mode": "execution",
        "runner": runner,
        "query": query,
        "parallel": max(1, parallel),
        "atomic": atomic,
        "total_tests": len(tests),
        "nodes": results,
        "queryability": {
            "supports": ["scope", "intent", "concern", "type", "module", "release"],
            "query": query,
        },
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    try:
        generate_dashboard(report_path="artifacts/pytest_report.json")
    except FileNotFoundError:
        # Distributed/external runners may not produce local pytest report artifacts.
        pass

    return 0 if all(node["rc"] == 0 for node in results) else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Execution engine: dry-run, parallel, atomic, runner-portable")
    parser.add_argument("--query", default="")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--parallel", type=int, default=1)
    parser.add_argument("--atomic", action="store_true")
    parser.add_argument("--runner", choices=["local", "docker", "k8s", "gitlab"], default="local")
    parser.add_argument("--out", default="artifacts/execution_engine.json")
    args = parser.parse_args()

    return run_execution_engine(
        query=args.query,
        dry_run=args.dry_run,
        parallel=max(1, args.parallel),
        atomic=args.atomic,
        runner=args.runner,
        out=Path(args.out),
    )


if __name__ == "__main__":
    raise SystemExit(main())
