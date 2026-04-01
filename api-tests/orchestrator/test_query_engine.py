from __future__ import annotations

import pytest

from orchestrator.query_engine import build_query_from_tags, build_query_string, parse_query


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
    assert query == "scope=api AND (intent=functional OR intent=performance) AND concern=security AND type=regression AND module=billing"


@pytest.mark.tag("scope=api", "intent=functional", "concern=auth", "type=smoke", "module=platform", "release=R2026.04-S7")
def test_parse_query_supports_explicit_and_or_expression() -> None:
    parsed = parse_query("(scope=api OR scope=ui) AND intent=performance AND type=load")
    assert len(parsed.groups) == 2


@pytest.mark.tag("scope=api", "intent=functional", "concern=auth", "type=smoke", "module=platform", "release=R2026.04-S7")
def test_build_query_from_tags_omits_all_defaults() -> None:
    query = build_query_from_tags({"scope": ["ALL"], "intent": ["performance"], "type": ["load", "stress"]})
    assert query == "intent=performance AND (type=load OR type=stress)"
