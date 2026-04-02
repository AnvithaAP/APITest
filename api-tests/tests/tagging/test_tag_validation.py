from __future__ import annotations

import pytest

from orchestrator.query_engine import parse_query
from tagging.tag_guard import enforce
from tagging.tag_parser import parse_tag_entries
from tagging.tag_validator import validate_intent_type


@pytest.mark.tag("scope=api", "intent=functional", "concern=contract", "type=system", "module=platform", "release=R2026.04-S1")
def test_invalid_combo() -> None:
    tags = {"intent": "functional", "type": "load"}
    with pytest.raises(ValueError):
        validate_intent_type(tags)


@pytest.mark.tag("scope=api", "intent=functional", "concern=contract", "type=system", "module=platform", "release=R2026.04-S1")
def test_valid_combo() -> None:
    validate_intent_type({"intent": "performance", "type": "stress"})


@pytest.mark.tag("scope=api", "intent=functional", "concern=contract", "type=system", "module=platform", "release=R2026.04-S1")
def test_tag_parser_rejects_invalid_intent_type_combo() -> None:
    _, errors = parse_tag_entries(("intent=functional", "type=load"))
    assert any("Invalid type 'load' for intent 'functional'" in error for error in errors)


@pytest.mark.tag("scope=api", "intent=functional", "concern=contract", "type=system", "module=platform", "release=R2026.04-S1")
def test_query_parser_rejects_invalid_intent_type_combo() -> None:
    with pytest.raises(ValueError):
        parse_query("intent=functional AND type=load")


@pytest.mark.tag("scope=api", "intent=functional", "concern=contract", "type=system", "module=platform", "release=R2026.04-S1")
def test_tag_guard_enforces_strict_mapping() -> None:
    with pytest.raises(ValueError):
        enforce({"intent": "functional", "type": "load"})
