from __future__ import annotations

import json
from pathlib import Path
from urllib import error, request


class AzureDevOpsClient:
    def __init__(self, organization_url: str, project: str, token: str, timeout_s: int = 30) -> None:
        self.organization_url = organization_url.rstrip("/")
        self.project = project
        self.token = token
        self.timeout_s = timeout_s

    def push_results(self, payload: dict) -> dict:
        return self._post("_apis/test/runs", payload)

    def push_status(self, payload: dict) -> dict:
        return self._post("_apis/build/builds", payload)

    def push_metadata(self, payload: dict) -> dict:
        return self._post("_apis/testresults/attachments", payload)

    def _post(self, path: str, payload: dict) -> dict:
        # Uses bearer token so teams can wire service principal tokens without PAT encoding.
        url = f"{self.organization_url}/{self.project}/{path}?api-version=7.1-preview.1"
        req = request.Request(url, data=json.dumps(payload).encode("utf-8"), method="POST")
        req.add_header("Authorization", f"Bearer {self.token}")
        req.add_header("Content-Type", "application/json")
        try:
            with request.urlopen(req, timeout=self.timeout_s) as response:
                return {
                    "ok": True,
                    "status": response.status,
                    "body": json.loads(response.read().decode("utf-8") or "{}"),
                }
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="ignore")
            return {"ok": False, "status": exc.code, "error": detail}


def build_ado_submission(aggregated_payload: dict) -> dict:
    dashboard = aggregated_payload.get("dashboard", {})
    kpis = dashboard.get("kpis", {})
    results = []
    for row in dashboard.get("merged_results", []):
        tags = row.get("tags", {})
        results.append(
            {
                "testName": row.get("test"),
                "outcome": row.get("status"),
                "automatedTestStorage": row.get("repo"),
                "automatedTestType": "pytest",
                "automationId": f"{row.get('repo')}::{row.get('test')}",
                "comment": json.dumps(
                    {
                        "runId": row.get("run_id"),
                        "scope": tags.get("scope"),
                        "intent": tags.get("intent"),
                        "pbi": tags.get("pbi") or tags.get("ado-pbi"),
                        "testcase": tags.get("testcase") or tags.get("ado-testcase"),
                    }
                ),
            }
        )

    return {
        "name": "Enterprise Automation Run",
        "state": "Completed",
        "isAutomated": True,
        "comment": f"total={kpis.get('total_tests', 0)} failed={kpis.get('total_failed', 0)}",
        "results": results,
        "metadata": {
            "total_runs": kpis.get("total_runs", 0),
            "scope_breakdown": dashboard.get("scope_breakdown", {}),
            "traceability": "PBI -> Test Case -> Automation -> Result",
        },
    }


def write_ado_submission(aggregated_json: str, output_path: str = "artifacts/ado_submission.json") -> Path:
    payload = json.loads(Path(aggregated_json).read_text(encoding="utf-8"))
    submission = build_ado_submission(payload)
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(submission, indent=2), encoding="utf-8")
    return out
