from __future__ import annotations


def diff_schema_keys(old_schema: dict, new_schema: dict) -> dict:
    old_props = old_schema.get("properties") or {}
    new_props = new_schema.get("properties") or {}

    old_keys = set(old_props.keys())
    new_keys = set(new_props.keys())

    changed_types = []
    for key in sorted(old_keys & new_keys):
        old_type = (old_props.get(key) or {}).get("type")
        new_type = (new_props.get(key) or {}).get("type")
        if old_type != new_type:
            changed_types.append({"field": key, "old": old_type, "new": new_type})

    return {
        "added": sorted(new_keys - old_keys),
        "removed": sorted(old_keys - new_keys),
        "unchanged": sorted(old_keys & new_keys),
        "changed_types": changed_types,
    }


def assert_backward_compatible(old_schema: dict, new_schema: dict) -> None:
    diff = diff_schema_keys(old_schema, new_schema)
    violations = []
    if diff["removed"]:
        violations.append(f"Removed fields: {diff['removed']}")
    if diff["changed_types"]:
        violations.append(f"Type changes: {diff['changed_types']}")

    old_required = set(old_schema.get("required") or [])
    new_required = set(new_schema.get("required") or [])
    if not old_required.issubset(new_required):
        violations.append(f"Required fields removed: {sorted(old_required - new_required)}")

    if violations:
        raise AssertionError("Backward incompatibility detected. " + " | ".join(violations))
