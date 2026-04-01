from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
import json
from pathlib import Path
import time
from urllib import error, parse, request


@dataclass(frozen=True)
class RepoPipelineTarget:
    name: str
    project_id: str
    ref: str = "main"
    variables: dict[str, str] | None = None


class GitLabOrchestrator:
    def __init__(self, base_url: str, token: str, timeout_s: int = 30) -> None:
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout_s = timeout_s

    def trigger_pipeline(self, target: RepoPipelineTarget) -> dict:
        body = {"ref": target.ref}
        for key, value in (target.variables or {}).items():
            body[f"variables[{key}]"] = value

        encoded_project = parse.quote(str(target.project_id), safe="")
        url = f"{self.base_url}/api/v4/projects/{encoded_project}/pipeline"
        payload = parse.urlencode(body).encode("utf-8")
        req = request.Request(url, data=payload, method="POST")
        req.add_header("PRIVATE-TOKEN", self.token)
        req.add_header("Content-Type", "application/x-www-form-urlencoded")

        started = time.time()
        try:
            with request.urlopen(req, timeout=self.timeout_s) as response:
                data = json.loads(response.read().decode("utf-8"))
            return {
                "name": target.name,
                "project_id": target.project_id,
                "status": "triggered",
                "pipeline_id": data.get("id"),
                "web_url": data.get("web_url", ""),
                "duration_s": round(time.time() - started, 3),
            }
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="ignore")
            return {
                "name": target.name,
                "project_id": target.project_id,
                "status": "failed",
                "error": f"HTTP {exc.code}: {detail}",
                "duration_s": round(time.time() - started, 3),
            }
        except Exception as exc:  # pragma: no cover - network exceptions are environment-specific
            return {
                "name": target.name,
                "project_id": target.project_id,
                "status": "failed",
                "error": str(exc),
                "duration_s": round(time.time() - started, 3),
            }

    def trigger_multi_repo(self, targets: list[RepoPipelineTarget], parallel: int = 4) -> list[dict]:
        workers = max(1, min(parallel, len(targets) or 1))
        results: list[dict] = []
        with ThreadPoolExecutor(max_workers=workers) as pool:
            future_map = {pool.submit(self.trigger_pipeline, target): target for target in targets}
            for future in as_completed(future_map):
                results.append(future.result())
        return sorted(results, key=lambda item: item["name"])


def load_targets(payload: dict) -> list[RepoPipelineTarget]:
    targets = []
    for item in payload.get("repos", []):
        targets.append(
            RepoPipelineTarget(
                name=item["name"],
                project_id=str(item["project_id"]),
                ref=item.get("ref", "main"),
                variables=item.get("variables", {}),
            )
        )
    return targets


def main() -> int:
    parser = argparse.ArgumentParser(description="Trigger pipelines across UI/API/Device/E2E repositories via GitLab API")
    parser.add_argument("--repos-file", required=True, help="JSON with {repos:[{name,project_id,ref?,variables?}]}")
    parser.add_argument("--gitlab-url", default="https://gitlab.com")
    parser.add_argument("--token", required=True)
    parser.add_argument("--parallel", type=int, default=4)
    parser.add_argument("--output", default="artifacts/gitlab_pipeline_triggers.json")
    args = parser.parse_args()

    payload = json.loads(Path(args.repos_file).read_text(encoding="utf-8"))
    targets = load_targets(payload)

    orchestrator = GitLabOrchestrator(args.gitlab_url, args.token)
    results = orchestrator.trigger_multi_repo(targets, parallel=args.parallel)

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(
            {
                "schema": "gitlab-multi-repo-v1",
                "gitlab_url": args.gitlab_url,
                "total": len(results),
                "triggered": sum(1 for item in results if item["status"] == "triggered"),
                "failed": [item["name"] for item in results if item["status"] != "triggered"],
                "results": results,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    return 0 if all(item["status"] == "triggered" for item in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
