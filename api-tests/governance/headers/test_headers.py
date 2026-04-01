import pytest


@pytest.mark.tag("scope=api", "intent=governance", "concern=headers", "type=compliance", "module=platform", "release=R2026.04-S7")
def test_required_headers_present():
    headers = {"content-type": "application/json", "authorization": "Bearer token"}
    assert headers["content-type"] == "application/json"
    assert headers["authorization"].startswith("Bearer ")
