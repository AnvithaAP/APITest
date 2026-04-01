from __future__ import annotations

import pytest

from orchestrator.query_engine import build_query_string


@pytest.mark.tag("scope=api", "intent=functional", "concern=auth", "type=smoke", "module=platform", "release=R2026.04-S7")
def test_build_query_string_from_structured_filters() -> None:
    query = build_query_string(
        {
            "scope": ["api"],
            "intent": ["functional", "performance"],
            "concern": ["security"],
            "type": ["regression"],
            "module": ["billing"],
        },
        group_operator="AND",
    )
    assert "scope=api" in query
    assert "intent=functional" in query
    assert "intent=performance" in query
    assert "AND" in query
