from __future__ import annotations

import pytest

from dashboard.dashboard import build_dashboard_html



@pytest.mark.tag("scope=ui", "intent=functional", "concern=flow", "type=system", "module=platform", "release=R2026.04-S7")
def test_dashboard_contains_chartjs_trend_sections() -> None:
    payload = {
        "dashboard": {
            "kpis": {"total_runs": 2, "total_tests": 10, "total_failed": 1, "pass_rate": 0.9},
            "scope_breakdown": {"api": 6, "ui": 4},
            "timeline": [
                {"timestamp": "2026-04-01T00:00:00Z", "latency_avg_ms": 120, "error_rate": 0.1, "pass_rate": 0.9, "failed": 1},
            ],
            "release_readiness": {"status": "ready", "failure_budget_used_pct": 10},
        }
    }

    html = build_dashboard_html(payload)
    assert "chart.js" in html.lower()
    assert "Latency (ms)" in html
    assert "Release Readiness" in html


@pytest.mark.tag("scope=ui", "intent=functional", "concern=interaction", "type=smoke", "module=platform", "release=R2026.04-S7")
def test_dashboard_contains_tag_query_builder_fields() -> None:
    html = build_dashboard_html({"dashboard": {}})
    for field in ["scope", "intent", "concern", "type", "module"]:
        assert f"tag-{field}" in html
