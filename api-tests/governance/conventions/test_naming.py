import re

import pytest


@pytest.mark.tag("scope=api", "intent=functional", "concern=data", "type=sanity", "module=platform", "release=R2026.04-S7")
def test_snake_case_field_convention():
    payload = {"order_id": 1, "created_at": "2026-01-01T00:00:00Z"}
    for key in payload:
        assert re.match(r"^[a-z]+(_[a-z]+)*$", key)
