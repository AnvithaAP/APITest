from __future__ import annotations

from pathlib import Path


def render_html_report(canonical_report: dict, output_path: str = "artifacts/html_report.html") -> Path:
    rows = "".join(
        f"<tr><td>{r['test_name']}</td><td>{r['status']}</td><td>{r['duration']:.4f}</td></tr>"
        for r in canonical_report["results"]
    )
    html = f"""
    <html><body>
    <h1>API Test Run Report</h1>
    <p>Run ID: {canonical_report['run_id']}</p>
    <table border='1' cellspacing='0' cellpadding='6'>
    <tr><th>Test</th><th>Status</th><th>Duration(s)</th></tr>
    {rows}
    </table>
    </body></html>
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")
    return path
