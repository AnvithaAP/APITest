import pytest


@pytest.mark.tag("scope=api", "intent=functional", "concern=behavior", "type=system", "module=orders", "release=R2026.04-S7")
def test_state_transition_workflow():
    state = "CREATED"
    transitions = {"CREATED": "PAID", "PAID": "SHIPPED"}
    state = transitions[state]
    assert state == "PAID"
    state = transitions[state]
    assert state == "SHIPPED"
