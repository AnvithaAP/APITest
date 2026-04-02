from __future__ import annotations

import pytest

from orchestrator.query_engine import build_query_from_tags, build_query_string, parse_nested_ui_tree, parse_query


@pytest.mark.tag("scope=api", "intent=functional", "concern=auth", "type=smoke", "module=platform", "release=R2026.04-S7")
def test_build_query_string_from_structured_filters() -> None:
    query = build_query_string(
        {
            "scope": ["api"],
            "intent": ["functional"],
            "concern": ["security"],
            "type": ["regression"],
            "module": ["billing"],
        },
        group_operator="AND",
    )
    assert query == "scope=api AND intent=functional AND concern=security AND type=regression AND module=billing"


@pytest.mark.tag("scope=api", "intent=functional", "concern=auth", "type=smoke", "module=platform", "release=R2026.04-S7")
def test_parse_query_supports_explicit_and_or_expression() -> None:
    parsed = parse_query("(scope=api OR scope=ui) AND intent=performance AND type=load")
    assert len(parsed.groups) == 2


@pytest.mark.tag("scope=api", "intent=functional", "concern=auth", "type=smoke", "module=platform", "release=R2026.04-S7")
def test_build_query_from_tags_omits_all_defaults() -> None:
    query = build_query_from_tags({"scope": ["ALL"], "intent": ["performance"], "type": ["load", "stress"]})
    assert query == "intent=performance AND (type=load OR type=stress)"


@pytest.mark.tag("scope=api", "intent=functional", "concern=auth", "type=smoke", "module=platform", "release=R2026.04-S7")
def test_parse_nested_tree_supports_grouping_logic() -> None:
    parsed = parse_nested_ui_tree(
        {
            "operator": "AND",
            "children": [
                {"key": "scope", "values": ["api", "ui"]},
                {
                    "operator": "OR",
                    "children": [
                        {"key": "intent", "values": ["functional"]},
                        {"key": "type", "values": ["load"]},
                    ],
                },
            ],
        }
    )
    assert len(parsed.groups) == 4


@pytest.mark.tag("scope=api", "intent=functional", "concern=auth", "type=smoke", "module=platform", "release=R2026.04-S7")
def test_parse_query_rejects_invalid_intent_type_combo() -> None:
    with pytest.raises(ValueError):
        parse_query("intent=functional AND type=load")
