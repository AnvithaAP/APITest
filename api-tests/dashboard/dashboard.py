from __future__ import annotations

import argparse
import json
from pathlib import Path


def _try_render_matplotlib_charts(aggregated_payload: dict, output_path: Path) -> str:
    try:
        import matplotlib.pyplot as plt
    except Exception:
        return ""

    dashboard = aggregated_payload.get("dashboard", {})
    timeline = dashboard.get("timeline", [])
    labels = [item.get("timestamp", "") for item in timeline]
    latency = [item.get("latency_avg_ms", 0) for item in timeline]
    errors = [item.get("error_rate", 0) for item in timeline]

    fig, axes = plt.subplots(2, 1, figsize=(10, 6), constrained_layout=True)
    axes[0].plot(labels, latency, marker="o")
    axes[0].set_title("Latency Trend (ms)")
    axes[0].tick_params(axis="x", rotation=45)

    axes[1].plot(labels, errors, marker="o", color="tab:red")
    axes[1].set_title("Error Rate Trend")
    axes[1].tick_params(axis="x", rotation=45)

    png_path = output_path.with_name("dashboard_trends.png")
    fig.savefig(png_path, dpi=120)
    plt.close(fig)
    return png_path.name


def build_dashboard_html(aggregated_payload: dict) -> str:
    dashboard = aggregated_payload.get("dashboard", {})
    kpis = dashboard.get("kpis", {})
    scope_breakdown = dashboard.get("scope_breakdown", {})
    timeline = dashboard.get("timeline", [])

    labels = [item.get("timestamp", "") for item in timeline]
    latency = [item.get("latency_avg_ms", 0) for item in timeline]
    errors = [item.get("error_rate", 0) for item in timeline]

    return f"""
<!doctype html>
<html>
<head>
  <meta charset='utf-8' />
  <title>Enterprise Quality Dashboard</title>
  <script src='https://cdn.plot.ly/plotly-2.35.2.min.js'></script>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 20px; }}
    .kpi {{ display: inline-block; border: 1px solid #ddd; padding: 12px; margin-right: 8px; min-width: 120px; }}
    #charts {{ display: grid; grid-template-columns: 1fr; gap: 20px; }}
  </style>
</head>
<body>
  <h1>Enterprise Test Dashboard</h1>
  <div>
    <div class='kpi'><b>Total Runs</b><br/>{kpis.get('total_runs', 0)}</div>
    <div class='kpi'><b>Total Tests</b><br/>{kpis.get('total_tests', 0)}</div>
    <div class='kpi'><b>Total Failed</b><br/>{kpis.get('total_failed', 0)}</div>
    <div class='kpi'><b>Pass Rate</b><br/>{kpis.get('pass_rate', 0)}</div>
  </div>

  <h2>Scope Breakdown</h2>
  <div id='scopeChart' style='height:350px;'></div>

  <div id='charts'>
    <div id='latencyChart' style='height:350px;'></div>
    <div id='errorChart' style='height:350px;'></div>
  </div>

  <script>
    const scopeData = [{json.dumps(scope_breakdown)}];
    Plotly.newPlot('scopeChart', [{{
      type: 'bar',
      x: Object.keys(scopeData[0]),
      y: Object.values(scopeData[0]),
      marker: {{ color: '#1f77b4' }}
    }}], {{ title: 'Tests by Scope' }});

    const labels = {json.dumps(labels)};
    const latency = {json.dumps(latency)};
    const errors = {json.dumps(errors)};

    Plotly.newPlot('latencyChart', [{{ x: labels, y: latency, type: 'scatter', mode: 'lines+markers', name: 'Latency (ms)' }}], {{ title: 'Latency Trend' }});
    Plotly.newPlot('errorChart', [{{ x: labels, y: errors, type: 'scatter', mode: 'lines+markers', name: 'Error Rate' }}], {{ title: 'Error Trend' }});
  </script>
</body>
</html>
"""


def render_dashboard(aggregated_json_path: str, output_path: str = "artifacts/dashboard.html") -> Path:
    aggregated = json.loads(Path(aggregated_json_path).read_text(encoding="utf-8"))

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    png_name = _try_render_matplotlib_charts(aggregated, out)

    html = build_dashboard_html(aggregated)
    if png_name:
        html = html.replace("</body>", f"<h2>Static Trends (Matplotlib)</h2><img src='{png_name}' style='max-width:100%;border:1px solid #ddd;'/>\n</body>")

    out.write_text(html, encoding="utf-8")
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Render enterprise dashboard from aggregated canonical payload")
    parser.add_argument("--aggregated", default="artifacts/aggregated_canonical.json")
    parser.add_argument("--out", default="artifacts/dashboard.html")
    args = parser.parse_args()

    render_dashboard(args.aggregated, args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
