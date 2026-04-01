from __future__ import annotations

import base64
import json
from urllib import error, request


class AzureDevOpsAPI:
    """Full ADO wiring for run creation, results push, and attachments."""

    def __init__(self, organization_url: str, project: str, pat: str, timeout_s: int = 30) -> None:
        self.organization_url = organization_url.rstrip("/")
        self.project = project
        self.timeout_s = timeout_s
        token = f":{pat}".encode("utf-8")
        self.auth_header = f"Basic {base64.b64encode(token).decode('utf-8')}"

    def create_test_run(self, payload: dict) -> dict:
        return self._request("POST", "_apis/test/runs", payload)

    def add_test_results(self, run_id: str | int, results: list[dict]) -> dict:
        return self._request("POST", f"_apis/test/runs/{run_id}/results", results)

    def add_attachment(self, run_id: str | int, payload: dict) -> dict:
        return self._request("POST", f"_apis/test/runs/{run_id}/attachments", payload)

    def complete_test_run(self, run_id: str | int, payload: dict) -> dict:
        return self._request("PATCH", f"_apis/test/runs/{run_id}", payload)

    def _request(self, method: str, path: str, payload: dict | list) -> dict:
        url = f"{self.organization_url}/{self.project}/{path}?api-version=7.1-preview.1"
        req = request.Request(url, data=json.dumps(payload).encode("utf-8"), method=method)
        req.add_header("Authorization", self.auth_header)
        req.add_header("Content-Type", "application/json")

        try:
            with request.urlopen(req, timeout=self.timeout_s) as response:
                return {
                    "ok": True,
                    "status": response.status,
                    "body": json.loads(response.read().decode("utf-8") or "{}"),
                }
        except error.HTTPError as exc:
            return {
                "ok": False,
                "status": exc.code,
                "error": exc.read().decode("utf-8", errors="ignore"),
            }
        except Exception as exc:  # pragma: no cover
            return {"ok": False, "status": 0, "error": str(exc)}
