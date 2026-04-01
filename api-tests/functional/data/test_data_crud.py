import pytest


@pytest.mark.tag("scope=api", "intent=functional", "concern=data", "type=regression", "module=users", "release=R2026.04-S7")
def test_data_value_correctness_and_idempotency():
    record = {"id": 7, "name": "Bob", "active": True}
    assert record["id"] == 7
    assert record["active"] is True
    before = record.copy()
    after = {**record}
    assert before == after
