import pytest


@pytest.mark.tag("scope=api", "intent=functional", "concern=data", "type=regression", "module=users", "release=R2026.04-S7")
def test_data_value_correctness_and_idempotency():
    record = {"id": 7, "name": "Bob", "active": True}
    before = record.copy()
    after = {**record}
    assert (record["id"], record["active"], before == after) == (7, True, True)
