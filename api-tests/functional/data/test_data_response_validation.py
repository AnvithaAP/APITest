from __future__ import annotations

import pytest

from core.validators import validate_json_field, validate_required_fields, validate_status_code


@pytest.mark.tag(
    "scope=api",
    "intent=functional",
    "concern=data",
    "type=regression",
    "module=users",
    "release=R2026.04-S1",
)
def test_data_layer_response_validation() -> None:
    status = 200
    payload = {"id": "user-1", "email": "user@example.com", "enabled": True}

    validate_status_code(status, {200, 201})
    validate_required_fields(payload, ["id", "email", "enabled"])
    validate_json_field(payload, "enabled", True)
