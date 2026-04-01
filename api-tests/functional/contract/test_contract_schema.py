import json
from pathlib import Path

import pytest

from core.validators.schema_diff import assert_backward_compatible
from core.validators.schema_validator import validate_json_schema


@pytest.mark.tag("scope=api", "intent=functional", "concern=contract", "type=regression", "module=users", "release=R2026.04-S7")
def test_user_response_schema_and_backward_compatibility():
    sample = {"id": 1, "name": "Alice", "email": "alice@example.com"}
    v1 = json.loads(Path("schemas/responses/user_v1.json").read_text(encoding="utf-8"))
    v2 = json.loads(Path("schemas/versions/user_v2.json").read_text(encoding="utf-8"))
    validate_json_schema(sample, v1)
    assert_backward_compatible(v1, v2)
