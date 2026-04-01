from __future__ import annotations

import pytest

from config.secrets_manager import get_secret


@pytest.mark.tag("scope=api", "intent=functional", "concern=auth", "type=regression", "module=platform", "release=R2026.04-S7")
def test_get_secret_prefers_direct_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MY_SECRET", "value-1")
    monkeypatch.setenv("AWS_SECRET_MY_SECRET", "value-2")
    assert get_secret("MY_SECRET") == "value-1"


@pytest.mark.tag("scope=api", "intent=functional", "concern=auth", "type=regression", "module=platform", "release=R2026.04-S7")
def test_get_secret_reads_vault(monkeypatch: pytest.MonkeyPatch) -> None:
    class _Resp:
        status_code = 200

        @staticmethod
        def json() -> dict:
            return {"data": {"data": {"value": "vault-token-value"}}}

    def _fake_get(*args, **kwargs):
        return _Resp()

    monkeypatch.delenv("MY_VAULT_SECRET", raising=False)
    monkeypatch.setenv("VAULT_ADDR", "https://vault.local")
    monkeypatch.setenv("VAULT_TOKEN", "abc")
    monkeypatch.setattr("requests.get", _fake_get)

    assert get_secret("MY_VAULT_SECRET") == "vault-token-value"
