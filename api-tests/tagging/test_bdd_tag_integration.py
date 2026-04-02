from __future__ import annotations

import pytest

import conftest


class _FakeItem:
    def __init__(self, keywords: list[str]) -> None:
        self.keywords = {key: True for key in keywords}

    def iter_markers(self, name: str):
        return []


@pytest.mark.tag("scope=api", "intent=functional", "concern=contract", "type=system", "module=platform", "release=R2026.04-S7")
def test_extract_item_tags_infers_bdd_style_keywords() -> None:
    item = _FakeItem([
        "scope_api",
        "intent:functional",
        "concern=behavior",
        "smoke",
        "module_platform",
        "release_r2026.04-s1",
    ])

    tags = conftest._extract_item_tags(item)  # noqa: SLF001

    assert tags == {
        "scope": "api",
        "intent": "functional",
        "concern": "behavior",
        "type": "smoke",
        "module": "platform",
        "release": "r2026.04-s1",
    }
