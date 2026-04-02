from __future__ import annotations

import pytest

from run import _enforce_intent_type_alignment


@pytest.mark.tag("scope=api", "intent=governance", "concern=standards", "type=compliance", "module=platform", "release=R2026.04-S1")
def test_run_cli_rejects_cross_intent_types() -> None:
    with pytest.raises(SystemExit):
        _enforce_intent_type_alignment(
            {
                "intent": ["functional"],
                "type": ["load"],
            }
        )


@pytest.mark.tag("scope=api", "intent=governance", "concern=standards", "type=compliance", "module=platform", "release=R2026.04-S1")
def test_run_cli_accepts_valid_intent_type_pairing() -> None:
    _enforce_intent_type_alignment(
        {
            "intent": ["performance"],
            "type": ["load", "stress"],
        }
    )
