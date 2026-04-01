from __future__ import annotations

import pytest

from config.secrets_manager import get_secret


@pytest.mark.tag("scope=api", "intent=functional", "concern=auth", "type=regression", "module=platform", "release=R2026.04-S7")
def test_get_secret_prefers_direct_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MY_SECRET", "value-1")
    monkeypatch.setenv("AWS_SECRET_MY_SECRET", "value-2")
    assert get_secret("MY_SECRET") == "value-1"
