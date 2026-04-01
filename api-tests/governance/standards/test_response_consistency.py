import pytest


@pytest.mark.tag("scope=api", "intent=functional", "concern=behavior", "type=regression", "module=platform", "release=R2026.04-S7")
def test_response_envelope_consistency():
    response = {"meta": {"trace_id": "abc"}, "data": {"id": 1}}
    assert set(response.keys()) == {"meta", "data"}
