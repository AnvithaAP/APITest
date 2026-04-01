from __future__ import annotations

import pytest

from dashboard.dashboard import build_dashboard_html



@pytest.mark.tag("scope=ui", "intent=governance", "concern=traceability", "type=compliance", "module=platform", "release=R2026.04-S7")
def test_dashboard_contains_plotly_trend_sections() -> None:
    payload = {
        "dashboard": {
            "kpis": {"total_runs": 2, "total_tests": 10, "total_failed": 1, "pass_rate": 0.9},
            "scope_breakdown": {"api": 6, "ui": 4},
            "timeline": [
                {"timestamp": "2026-04-01T00:00:00Z", "latency_avg_ms": 120, "error_rate": 0.1},
            ],
        }
    }

    html = build_dashboard_html(payload)
    assert "plotly" in html.lower()
    assert "Latency Trend" in html
    assert "Error Trend" in html
