from __future__ import annotations

from pathlib import Path


def render_trend_html(rows: list[tuple], output_path: str) -> Path:
    table_rows = "".join(
        f"<tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td><td>{r[4]}</td><td>{r[5]}</td></tr>"
        for r in rows
    )
    html = f"""
    <html><body>
    <h1>API Run History & Trends</h1>
    <table border='1' cellspacing='0' cellpadding='6'>
    <tr><th>Run ID</th><th>Timestamp</th><th>API</th><th>Latency</th><th>Error Rate</th><th>Throughput</th></tr>
    {table_rows}
    </table>
    <h2>Trend Graph Inputs</h2>
    <p>Latency over time, error rate over time, throughput trend data are available in the table for external graphing.</p>
    </body></html>
    """
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    return out
