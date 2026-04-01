from __future__ import annotations

import pytest


@pytest.mark.tag(
    "scope=api",
    "intent=functional",
    "concern=data",
    "type=regression",
    "module=platform",
    "release=R2026.04-S1",
)
def test_template_replace_with_real_assertions() -> None:
    """Template test case with required tags for governance compliance."""
    assert True
