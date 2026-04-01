from __future__ import annotations

from pathlib import Path


def render_trend_html(rows: list[tuple], output_path: str) -> Path:
    table_rows = "".join(
        f"<tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]:.4f}</td><td>{r[4]:.4f}</td><td>{r[5]:.2f}</td></tr>"
        for r in rows
    )

    latencies = [float(r[3]) for r in rows]
    error_rates = [float(r[4]) for r in rows]
    throughputs = [float(r[5]) for r in rows]

    html = f"""
    <html><body>
    <h1>API Run History & Trends</h1>
    <h2>Latency Trend</h2>
    {_sparkline_svg(latencies, '#1f77b4')}
    <h2>Error Rate Trend</h2>
    {_sparkline_svg(error_rates, '#d62728')}
    <h2>Throughput Trend</h2>
    {_sparkline_svg(throughputs, '#2ca02c')}
    <h2>Historical Comparison</h2>
    {_comparison(latencies, error_rates)}
    <table border='1' cellspacing='0' cellpadding='6'>
    <tr><th>Run ID</th><th>Timestamp</th><th>API</th><th>Latency</th><th>Error Rate</th><th>Throughput</th></tr>
    {table_rows}
    </table>
    </body></html>
    """
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    return out


def _comparison(latencies: list[float], errors: list[float]) -> str:
    if len(latencies) < 2:
        return "<p>Not enough data for historical comparison.</p>"
    prev_l, cur_l = latencies[-2], latencies[-1]
    prev_e, cur_e = errors[-2], errors[-1]
    lat_delta = ((cur_l - prev_l) / prev_l * 100) if prev_l else 0
    err_delta = ((cur_e - prev_e) / prev_e * 100) if prev_e else 0
    return (
        f"<p>Latest vs previous: latency {lat_delta:+.2f}% | error rate {err_delta:+.2f}%</p>"
    )


def _sparkline_svg(values: list[float], color: str) -> str:
    if not values:
        return "<p>No data</p>"
    width, height = 480, 120
    v_min, v_max = min(values), max(values)
    span = (v_max - v_min) or 1.0
    points: list[str] = []
    for idx, value in enumerate(values):
        x = int((idx / max(1, len(values) - 1)) * (width - 20)) + 10
        normalized = (value - v_min) / span
        y = height - int(normalized * (height - 20)) - 10
        points.append(f"{x},{y}")
    return (
        f"<svg width='{width}' height='{height}' style='border:1px solid #ddd'>"
        f"<polyline fill='none' stroke='{color}' stroke-width='2' points='{' '.join(points)}'/>"
        "</svg>"
    )
