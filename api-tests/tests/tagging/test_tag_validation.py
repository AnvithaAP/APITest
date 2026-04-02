from __future__ import annotations

import pytest

from tagging.tag_validator import validate_intent_type


@pytest.mark.tag("scope=api", "intent=governance", "concern=standards", "type=compliance", "module=platform", "release=R2026.04-S1")
def test_invalid_combo() -> None:
    tags = {"intent": "functional", "type": "load"}
    with pytest.raises(ValueError):
        validate_intent_type(tags)


@pytest.mark.tag("scope=api", "intent=governance", "concern=standards", "type=compliance", "module=platform", "release=R2026.04-S1")
def test_valid_combo() -> None:
    validate_intent_type({"intent": "performance", "type": "stress"})
