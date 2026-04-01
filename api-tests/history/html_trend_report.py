from __future__ import annotations

from pathlib import Path


def _sparkline(values: list[float], color: str, width: int = 420, height: int = 80) -> str:
    if not values:
        return "<svg></svg>"
    min_v, max_v = min(values), max(values)
    spread = (max_v - min_v) or 1
    step = width / max(len(values) - 1, 1)
    points = []
    for i, val in enumerate(values):
        x = i * step
        y = height - ((val - min_v) / spread) * height
        points.append(f"{x:.2f},{y:.2f}")
    polyline = " ".join(points)
    return f"<svg width='{width}' height='{height}'><polyline fill='none' stroke='{color}' stroke-width='2' points='{polyline}'/></svg>"


def render_trend_html(rows: list[tuple], output_path: str) -> Path:
    table_rows = "".join(
        f"<tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td><td>{r[4]}</td><td>{r[5]}</td></tr>"
        for r in rows
    )

    latency_vals = [float(r[3]) for r in rows]
    error_vals = [float(r[4]) for r in rows]
    throughput_vals = [float(r[5]) for r in rows]

    html = f"""
    <html><body>
    <h1>API Run History & Trends</h1>
    <table border='1' cellspacing='0' cellpadding='6'>
    <tr><th>Run ID</th><th>Timestamp</th><th>API</th><th>Latency</th><th>Error Rate</th><th>Throughput</th></tr>
    {table_rows}
    </table>
    <h2>Trend Graphs</h2>
    <h3>Latency</h3>
    {_sparkline(latency_vals, '#2563eb')}
    <h3>Error Rate</h3>
    {_sparkline(error_vals, '#dc2626')}
    <h3>Throughput</h3>
    {_sparkline(throughput_vals, '#16a34a')}
    </body></html>
    """
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    return out
