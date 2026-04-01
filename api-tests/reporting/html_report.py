from __future__ import annotations

from pathlib import Path


def render_html_report(canonical_report: dict, output_path: str = "artifacts/html_report.html") -> Path:
    rows = []
    for idx, result in enumerate(canonical_report["results"]):
        details = _render_tag_badges(result.get("tags", {}))
        rows.append(
            "<tr>"
            f"<td><a href='#t{idx}'>{result['test_name']}</a></td>"
            f"<td>{result['status']}</td>"
            f"<td>{result['duration']:.4f}</td>"
            f"<td>{details}</td>"
            "</tr>"
            f"<tr id='t{idx}'><td colspan='4'><details><summary>Drill-down</summary><pre>{result}</pre></details></td></tr>"
        )

    summary = canonical_report.get("summary", {})
    html = f"""
    <html><body>
    <h1>API Test Run Report</h1>
    <p>Run ID: {canonical_report['run_id']}</p>
    <p>Query: <code>{canonical_report.get('query', '')}</code></p>
    <p>Passed: {summary.get('passed', 0)} | Failed: {summary.get('failed', 0)} | Skipped: {summary.get('skipped', 0)}</p>
    <table border='1' cellspacing='0' cellpadding='6'>
    <tr><th>Test</th><th>Status</th><th>Duration(s)</th><th>Tags</th></tr>
    {''.join(rows)}
    </table>
    </body></html>
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")
    return path


def _render_tag_badges(tags: dict[str, str]) -> str:
    if not tags:
        return "-"
    return " ".join(f"<code>{k}:{v}</code>" for k, v in sorted(tags.items()))
