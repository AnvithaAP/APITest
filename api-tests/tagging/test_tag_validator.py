from __future__ import annotations

import pytest

from tagging.tag_validator import validate_tags


@pytest.mark.tag("scope=api", "intent=functional", "concern=contract", "type=system", "module=platform", "release=R2026.04-S1")
def test_validate_tags_rejects_functional_with_performance_type() -> None:
    result = validate_tags(
        {
            "scope": "api",
            "intent": "functional",
            "concern": "data",
            "type": "load",
            "module": "platform",
            "release": "R2026.04-S1",
        }
    )

    assert not result.ok
    assert any("functional type must be one of" in error for error in result.errors)


@pytest.mark.tag("scope=api", "intent=functional", "concern=contract", "type=system", "module=platform", "release=R2026.04-S1")
def test_validate_tags_rejects_performance_with_functional_type() -> None:
    result = validate_tags(
        {
            "scope": "api",
            "intent": "performance",
            "concern": "latency",
            "type": "regression",
            "module": "platform",
            "release": "R2026.04-S1",
        }
    )

    assert not result.ok
    assert any("performance type must be one of" in error for error in result.errors)


@pytest.mark.tag("scope=api", "intent=functional", "concern=contract", "type=system", "module=platform", "release=R2026.04-S1")
def test_validate_tags_accepts_functional_and_performance_type_mappings() -> None:
    functional = validate_tags(
        {
            "scope": "api",
            "intent": "functional",
            "concern": "data",
            "type": "smoke",
            "module": "platform",
            "release": "R2026.04-S1",
        }
    )
    performance = validate_tags(
        {
            "scope": "api",
            "intent": "performance",
            "concern": "latency",
            "type": "stress",
            "module": "platform",
            "release": "R2026.04-S1",
        }
    )

    assert functional.ok
    assert performance.ok
