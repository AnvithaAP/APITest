from __future__ import annotations

import argparse
import json
from pathlib import Path


TAG_QUERY_FIELDS = ["scope", "intent", "concern", "type", "module"]


def _try_render_matplotlib_charts(aggregated_payload: dict, output_path: Path) -> str:
    try:
        import matplotlib.pyplot as plt
    except Exception:
        return ""

    dashboard = aggregated_payload.get("dashboard", {})
    timeline = dashboard.get("timeline", [])
    labels = [item.get("timestamp", "") for item in timeline]
    latency = [item.get("latency_avg_ms", 0) for item in timeline]
    pass_rate = [item.get("pass_rate", 0) for item in timeline]

    fig, axes = plt.subplots(2, 1, figsize=(10, 6), constrained_layout=True)
    axes[0].plot(labels, latency, marker="o")
    axes[0].set_title("Latency Trend (ms)")
    axes[0].tick_params(axis="x", rotation=45)

    axes[1].plot(labels, pass_rate, marker="o", color="tab:green")
    axes[1].set_title("Pass Rate Trend")
    axes[1].tick_params(axis="x", rotation=45)

    png_path = output_path.with_name("dashboard_trends.png")
    fig.savefig(png_path, dpi=120)
    plt.close(fig)
    return png_path.name


def _tag_query_ui() -> str:
    inputs = "\n".join(
        f"<label>{field}<input id='tag-{field}' placeholder='{field}=value[,value]'/></label>"
        for field in TAG_QUERY_FIELDS
    )
    return f"""
  <h2>Tag Query Builder</h2>
  <div id='tagBuilder'>
    {inputs}
    <label>operator
      <select id='tag-operator'>
        <option value='AND'>AND</option>
        <option value='OR'>OR</option>
      </select>
    </label>
    <button onclick='buildTagQuery()'>Build Query</button>
    <code id='queryOut'></code>
  </div>
  <script>
    function buildTagQuery() {{
      const keys = {json.dumps(TAG_QUERY_FIELDS)};
      const operator = document.getElementById('tag-operator').value;
      const parts = [];
      for (const key of keys) {{
        const value = document.getElementById(`tag-${{key}}`).value.trim();
        if (!value) continue;
        if (value.includes('=')) parts.push(value);
        else parts.push(`${{key}}=${{value}}`);
      }}
      document.getElementById('queryOut').textContent = parts.join(` ${{operator}} `);
    }}
  </script>
"""


def build_dashboard_html(aggregated_payload: dict) -> str:
    dashboard = aggregated_payload.get("dashboard", {})
    kpis = dashboard.get("kpis", {})
    scope_breakdown = dashboard.get("scope_breakdown", {})
    timeline = dashboard.get("timeline", [])
    release = dashboard.get("release_readiness", {})

    labels = [item.get("timestamp", "") for item in timeline]
    latency = [item.get("latency_avg_ms", 0) for item in timeline]
    pass_trend = [item.get("pass_rate", 0) for item in timeline]
    fail_trend = [item.get("failed", 0) for item in timeline]

    return f"""
<!doctype html>
<html>
<head>
  <meta charset='utf-8' />
  <title>Enterprise Quality Dashboard</title>
  <script src='https://cdn.jsdelivr.net/npm/chart.js'></script>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 20px; }}
    .kpi {{ display: inline-block; border: 1px solid #ddd; padding: 12px; margin-right: 8px; min-width: 150px; }}
    #charts {{ display: grid; grid-template-columns: 1fr; gap: 20px; }}
    #tagBuilder {{ display: grid; gap: 8px; max-width: 600px; margin-bottom: 20px; }}
    #tagBuilder input, #tagBuilder select {{ margin-left: 8px; }}
  </style>
</head>
<body>
  <h1>Enterprise Test Dashboard</h1>
  <div>
    <div class='kpi'><b>Total Runs</b><br/>{kpis.get('total_runs', 0)}</div>
    <div class='kpi'><b>Total Tests</b><br/>{kpis.get('total_tests', 0)}</div>
    <div class='kpi'><b>Total Failed</b><br/>{kpis.get('total_failed', 0)}</div>
    <div class='kpi'><b>Pass Rate</b><br/>{kpis.get('pass_rate', 0)}</div>
    <div class='kpi'><b>Release Readiness</b><br/>{release.get('status', 'unknown')}</div>
  </div>

  {_tag_query_ui()}

  <h2>Release Readiness View</h2>
  <p>Gate: {release.get('status', 'unknown')} | Failure budget used: {release.get('failure_budget_used_pct', 0)}%</p>

  <div id='charts'>
    <canvas id='scopeChart' height='120'></canvas>
    <canvas id='latencyChart' height='120'></canvas>
    <canvas id='passFailChart' height='120'></canvas>
  </div>

  <script>
    const scopeData = {json.dumps(scope_breakdown)};
    new Chart(document.getElementById('scopeChart'), {{
      type: 'bar',
      data: {{
        labels: Object.keys(scopeData),
        datasets: [{{ label: 'Tests by Scope', data: Object.values(scopeData), backgroundColor: '#1f77b4' }}]
      }}
    }});

    const labels = {json.dumps(labels)};
    const latency = {json.dumps(latency)};
    const passTrend = {json.dumps(pass_trend)};
    const failTrend = {json.dumps(fail_trend)};

    new Chart(document.getElementById('latencyChart'), {{
      type: 'line',
      data: {{ labels, datasets: [{{ label: 'Latency (ms)', data: latency, borderColor: '#ff7f0e', tension: 0.2 }}] }}
    }});

    new Chart(document.getElementById('passFailChart'), {{
      type: 'line',
      data: {{ labels, datasets: [
        {{ label: 'Pass Rate', data: passTrend, borderColor: '#2ca02c', tension: 0.2 }},
        {{ label: 'Failed Tests', data: failTrend, borderColor: '#d62728', tension: 0.2 }}
      ] }}
    }});
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
        html = html.replace("</body>", f"<h2>Static Trends (Matplotlib)</h2><img src='{png_name}' style='max-width:100%;border:1px solid #ddd;'/><br/>\n</body>")

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
