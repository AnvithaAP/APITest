from __future__ import annotations

import pytest

from tagging.tag_validator import validate_full_tag_model


@pytest.mark.tag("scope=integration", "intent=functional", "concern=flow", "type=system", "module=platform", "release=R2026.04-S1")
def test_invalid_ui_combo() -> None:
    tags = {
        "scope": "ui",
        "intent": "functional",
        "concern": "latency",
        "type": "load",
    }
    with pytest.raises(ValueError):
        validate_full_tag_model(tags)
