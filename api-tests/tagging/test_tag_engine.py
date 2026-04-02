from __future__ import annotations

import pytest

from tagging.tag_engine import tag_engine


@pytest.mark.tag("scope=api", "intent=functional", "concern=contract", "type=regression", "module=platform", "release=R2026.04-S7")
def test_tag_engine_supports_nested_ui_query_tree() -> None:
    tree = {
        "operator": "AND",
        "children": [
            {"key": "scope", "values": ["api", "ui"]},
            {
                "operator": "OR",
                "children": [
                    {"key": "intent", "values": ["functional"]},
                    {"key": "intent", "values": ["reliability"]},
                ],
            },
        ],
    }

    parsed = tag_engine.from_ui_tree(tree)
    assert len(parsed.groups) == 4
    assert any(clause.key == "scope" for clause in parsed.groups[0])
