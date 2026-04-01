from __future__ import annotations

import base64
import json
import os
from urllib import request


class AdoAdapter:
    def __init__(self, organization_url: str, project: str, pipeline_id: str, pat_env: str = "ADO_PAT") -> None:
        self.organization_url = organization_url.rstrip("/")
        self.project = project
        self.pipeline_id = pipeline_id
        self.pat = os.getenv(pat_env, "")

    def _headers(self) -> dict[str, str]:
        token = base64.b64encode(f":{self.pat}".encode("utf-8")).decode("utf-8")
        return {
            "Authorization": f"Basic {token}",
            "Content-Type": "application/json",
        }

    def trigger_pipeline(self, branch: str, variables: dict[str, str] | None = None) -> dict:
        if not self.pat:
            raise RuntimeError("ADO personal access token is missing (set ADO_PAT)")

        url = f"{self.organization_url}/{self.project}/_apis/pipelines/{self.pipeline_id}/runs?api-version=7.1"
        payload = {
            "resources": {"repositories": {"self": {"refName": f"refs/heads/{branch}"}}},
            "variables": {k: {"value": v} for k, v in (variables or {}).items()},
        }
        data = json.dumps(payload).encode("utf-8")
        req = request.Request(url=url, data=data, headers=self._headers(), method="POST")
        with request.urlopen(req) as response:
            return json.loads(response.read().decode("utf-8"))
