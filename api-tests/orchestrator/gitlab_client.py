from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
import json
from urllib import error, parse, request


@dataclass(frozen=True)
class GitLabPipelineRequest:
    project_id: str
    ref: str = "main"
    variables: dict[str, str] | None = None


class GitLabClient:
    """Authenticated GitLab API client for pipeline trigger and status retrieval."""

    def __init__(self, base_url: str, private_token: str, timeout_s: int = 30) -> None:
        self.base_url = base_url.rstrip("/")
        self.private_token = private_token
        self.timeout_s = timeout_s

    def trigger_pipeline(self, pipeline_request: GitLabPipelineRequest) -> dict:
        encoded_project = parse.quote(str(pipeline_request.project_id), safe="")
        url = f"{self.base_url}/api/v4/projects/{encoded_project}/pipeline"

        body = {"ref": pipeline_request.ref}
        for key, value in (pipeline_request.variables or {}).items():
            body[f"variables[{key}]"] = value

        req = request.Request(url, data=parse.urlencode(body).encode("utf-8"), method="POST")
        req.add_header("PRIVATE-TOKEN", self.private_token)
        req.add_header("Content-Type", "application/x-www-form-urlencoded")
        return self._send(req)

    def get_pipeline(self, project_id: str, pipeline_id: str | int) -> dict:
        encoded_project = parse.quote(str(project_id), safe="")
        url = f"{self.base_url}/api/v4/projects/{encoded_project}/pipelines/{pipeline_id}"
        req = request.Request(url, method="GET")
        req.add_header("PRIVATE-TOKEN", self.private_token)
        return self._send(req)

    def trigger_multi_repo(self, requests: list[GitLabPipelineRequest], max_parallel: int = 4) -> list[dict]:
        workers = max(1, min(max_parallel, len(requests) or 1))
        outputs: list[dict] = []
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = {pool.submit(self.trigger_pipeline, req): req for req in requests}
            for future in as_completed(futures):
                outputs.append(future.result())
        return outputs

    def _send(self, req: request.Request) -> dict:
        try:
            with request.urlopen(req, timeout=self.timeout_s) as response:
                payload = json.loads(response.read().decode("utf-8") or "{}")
                return {"ok": True, "status": response.status, "data": payload}
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="ignore")
            return {"ok": False, "status": exc.code, "error": detail}
        except Exception as exc:  # pragma: no cover
            return {"ok": False, "status": 0, "error": str(exc)}
