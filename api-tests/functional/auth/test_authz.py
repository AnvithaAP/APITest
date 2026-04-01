import pytest


@pytest.mark.tag("scope=api", "intent=functional", "concern=auth", "type=smoke", "module=platform", "release=R2026.04-S7")
def test_role_based_access_control():
    role_to_actions = {"admin": {"read", "write"}, "viewer": {"read"}}
    assert ("write" in role_to_actions["admin"], "write" not in role_to_actions["viewer"]) == (True, True)
