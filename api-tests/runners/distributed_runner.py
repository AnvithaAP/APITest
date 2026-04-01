from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from pathlib import Path
import subprocess
import sys
import time
import uuid


def _chunk_tests(selected_tests: list[str], nodes: int) -> list[list[str]]:
    if not selected_tests:
        return [[] for _ in range(nodes)]
    chunks = [[] for _ in range(nodes)]
    for idx, test in enumerate(selected_tests):
        chunks[idx % nodes].append(test)
    return chunks


def _build_k8s_job_spec(node_id: int, query: str, repo: str, repo_type: str, tests: list[str], namespace: str) -> dict:
    job_name = f"api-test-{repo}-{node_id}-{uuid.uuid4().hex[:6]}"
    return {
        "apiVersion": "batch/v1",
        "kind": "Job",
        "metadata": {
            "name": job_name,
            "namespace": namespace,
            "labels": {
                "app": "api-test-framework",
                "execution_mode": "distributed",
                "repo": repo,
                "repo_type": repo_type,
            },
        },
        "spec": {
            "backoffLimit": 0,
            "template": {
                "metadata": {
                    "labels": {
                        "job": job_name,
                    }
                },
                "spec": {
                    "restartPolicy": "Never",
                    "containers": [
                        {
                            "name": "runner",
                            "image": "python:3.11-slim",
                            "command": ["python", "runners/pytest_runner.py"],
                            "args": ["--query", query, "--repo", repo, "--repo-type", repo_type],
                            "env": [
                                {"name": "SELECTED_TESTS_JSON", "value": json.dumps(tests)},
                            ],
                        }
                    ],
                },
            },
        },
    }


def _execute_local_fallback(node_id: int, tests: list[str], query: str, repo: str, repo_type: str) -> dict:
    started = time.time()
    cmd = [sys.executable, "runners/pytest_runner.py", "--query", query, "--repo", repo, "--repo-type", repo_type]
    rc = subprocess.call(cmd)
    return {
        "node_id": f"pod-{node_id}",
        "selected_tests": tests,
        "rc": rc,
        "duration_s": round(time.time() - started, 3),
        "mode": "local-fallback",
    }


def _submit_k8s_job(job_spec: dict, timeout_s: int) -> dict:
    started = time.time()
    try:
        from kubernetes import client, config

        try:
            config.load_incluster_config()
        except Exception:
            config.load_kube_config()

        batch = client.BatchV1Api()
        namespace = job_spec["metadata"]["namespace"]
        created = batch.create_namespaced_job(namespace=namespace, body=job_spec)
        return {
            "node_id": created.metadata.name,
            "selected_tests": json.loads(job_spec["spec"]["template"]["spec"]["containers"][0]["env"][0]["value"]),
            "rc": 0,
            "duration_s": round(time.time() - started, 3),
            "mode": "k8s-job",
            "namespace": namespace,
            "timeout_s": timeout_s,
        }
    except Exception as exc:
        return {
            "node_id": job_spec["metadata"]["name"],
            "selected_tests": json.loads(job_spec["spec"]["template"]["spec"]["containers"][0]["env"][0]["value"]),
            "rc": 1,
            "duration_s": round(time.time() - started, 3),
            "mode": "k8s-job",
            "error": str(exc),
        }


def main() -> int:
    parser = argparse.ArgumentParser(description="Distributed execution layer with Kubernetes Jobs")
    parser.add_argument("--query", default="")
    parser.add_argument("--repo", default="api-tests")
    parser.add_argument("--repo-type", default="api")
    parser.add_argument("--nodes", type=int, default=3)
    parser.add_argument("--tests-file", default="")
    parser.add_argument("--out", default="artifacts/distributed_execution.json")
    parser.add_argument("--execution-mode", choices=["local", "k8s"], default="k8s")
    parser.add_argument("--namespace", default="default")
    parser.add_argument("--k8s-timeout", type=int, default=900)
    parser.add_argument("--jobs-spec-out", default="artifacts/k8s_jobs.json")
    args = parser.parse_args()

    selected_tests: list[str] = []
    if args.tests_file and Path(args.tests_file).exists():
        selected_tests = json.loads(Path(args.tests_file).read_text(encoding="utf-8")).get("tests", [])

    node_count = max(1, args.nodes)
    chunks = _chunk_tests(selected_tests, node_count)
    job_specs = [
        _build_k8s_job_spec(idx + 1, args.query, args.repo, args.repo_type, chunks[idx], args.namespace)
        for idx in range(node_count)
    ]

    specs_out = Path(args.jobs_spec_out)
    specs_out.parent.mkdir(parents=True, exist_ok=True)
    specs_out.write_text(json.dumps({"jobs": job_specs}, indent=2), encoding="utf-8")

    node_results: list[dict] = []
    with ThreadPoolExecutor(max_workers=node_count) as pool:
        if args.execution_mode == "k8s":
            futures = [pool.submit(_submit_k8s_job, spec, args.k8s_timeout) for spec in job_specs]
        else:
            futures = [
                pool.submit(_execute_local_fallback, idx + 1, chunks[idx], args.query, args.repo, args.repo_type)
                for idx in range(node_count)
            ]
        for future in as_completed(futures):
            node_results.append(future.result())

    payload = {
        "schema": "distributed-runner-v2",
        "execution_mode": args.execution_mode,
        "namespace": args.namespace,
        "nodes": sorted(node_results, key=lambda x: x["node_id"]),
        "parallel_scaling_factor": node_count,
        "query": args.query,
        "jobs_spec": str(specs_out),
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    return 0 if all(n.get("rc") == 0 for n in node_results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
