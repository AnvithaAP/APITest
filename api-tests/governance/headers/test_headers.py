import pytest


@pytest.mark.tag("scope=api", "intent=functional", "concern=contract", "type=sanity", "module=platform")
def test_required_headers_present():
    headers = {"content-type": "application/json", "authorization": "Bearer token"}
    assert headers["content-type"] == "application/json"
    assert headers["authorization"].startswith("Bearer ")
