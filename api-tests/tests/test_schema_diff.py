import pytest

from core.validators.schema_diff import assert_backward_compatible, diff_schema_keys


@pytest.mark.tag("scope=api", "intent=functional", "concern=contract", "type=regression", "module=platform")
def test_schema_diff_reports_type_changes():
    old = {"properties": {"id": {"type": "integer"}}}
    new = {"properties": {"id": {"type": "string"}, "name": {"type": "string"}}}
    diff = diff_schema_keys(old, new)
    assert diff["added"] == ["name"]
    assert diff["changed_types"] == [{"field": "id", "old": "integer", "new": "string"}]


@pytest.mark.tag("scope=api", "intent=functional", "concern=contract", "type=regression", "module=platform")
def test_backward_compatibility_fails_on_removed_field():
    old = {"properties": {"id": {"type": "integer"}, "name": {"type": "string"}}, "required": ["id", "name"]}
    new = {"properties": {"id": {"type": "integer"}}, "required": ["id"]}
    with pytest.raises(AssertionError):
        assert_backward_compatible(old, new)
