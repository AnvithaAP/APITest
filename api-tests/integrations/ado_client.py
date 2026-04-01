from __future__ import annotations

import argparse
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

    def update_test_run(self, run_id: str, payload: dict) -> dict:
        return self._patch(f"_apis/test/runs/{run_id}", payload)

    def link_result_to_pbi(self, pbi_id: str, payload: dict) -> dict:
        return self._patch(f"_apis/wit/workitems/{pbi_id}", payload, content_type="application/json-patch+json")

    def _post(self, path: str, payload: dict) -> dict:
        return self._request("POST", path, payload)

    def _patch(self, path: str, payload: dict, content_type: str = "application/json") -> dict:
        return self._request("PATCH", path, payload, content_type=content_type)

    def _request(self, method: str, path: str, payload: dict, content_type: str = "application/json") -> dict:
        url = f"{self.organization_url}/{self.project}/{path}?api-version=7.1-preview.1"
        req = request.Request(url, data=json.dumps(payload).encode("utf-8"), method=method)
        req.add_header("Authorization", f"Bearer {self.token}")
        req.add_header("Content-Type", content_type)
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
    pbi_links = []
    for row in dashboard.get("merged_results", []):
        tags = row.get("tags", {})
        pbi = tags.get("pbi") or tags.get("ado-pbi")
        testcase = tags.get("testcase") or tags.get("ado-testcase")
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
                        "pbi": pbi,
                        "testcase": testcase,
                    }
                ),
            }
        )
        if pbi:
            pbi_links.append({"pbi": str(pbi), "automation_id": f"{row.get('repo')}::{row.get('test')}"})

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
        "pbi_links": pbi_links,
    }


def write_ado_submission(aggregated_json: str, output_path: str = "artifacts/ado_submission.json") -> Path:
    payload = json.loads(Path(aggregated_json).read_text(encoding="utf-8"))
    submission = build_ado_submission(payload)
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(submission, indent=2), encoding="utf-8")
    return out


def push_ado_submission(submission_path: str, org_url: str, project: str, token: str) -> dict:
    payload = json.loads(Path(submission_path).read_text(encoding="utf-8"))
    client = AzureDevOpsClient(org_url, project, token)
    run_response = client.push_results(payload)

    link_responses = []
    for link in payload.get("pbi_links", []):
        patch = [
            {
                "op": "add",
                "path": "/fields/System.History",
                "value": f"Automation result linked: {link.get('automation_id')}",
            }
        ]
        link_responses.append({"pbi": link.get("pbi"), "response": client.link_result_to_pbi(link.get("pbi"), patch)})

    return {"test_run": run_response, "pbi_updates": link_responses}


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate and optionally push ADO run payload")
    parser.add_argument("--aggregated", default="artifacts/aggregated_canonical.json")
    parser.add_argument("--out", default="artifacts/ado_submission.json")
    parser.add_argument("--push", action="store_true")
    parser.add_argument("--org-url", default="")
    parser.add_argument("--project", default="")
    parser.add_argument("--token", default="")
    args = parser.parse_args()

    out = write_ado_submission(args.aggregated, args.out)
    if args.push and args.org_url and args.project and args.token:
        result = push_ado_submission(str(out), args.org_url, args.project, args.token)
        Path("artifacts/ado_push_result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
        return 0 if result.get("test_run", {}).get("ok") else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
