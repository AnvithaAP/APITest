from __future__ import annotations

import pytest

from core.validators import validate_json_schema


@pytest.mark.tag(
    "scope=api",
    "intent=functional",
    "concern=contract",
    "type=regression",
    "module=platform",
    "release=R2026.04-S1",
)
def test_contract_schema_validation_for_user_payload() -> None:
    payload = {"id": 100, "name": "Ada", "active": True}
    schema = {
        "type": "object",
        "required": ["id", "name", "active"],
        "properties": {
            "id": {"type": "integer"},
            "name": {"type": "string"},
            "active": {"type": "boolean"},
        },
        "additionalProperties": False,
    }
    validate_json_schema(payload, schema)
