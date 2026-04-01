from __future__ import annotations


def diff_schema(old_schema: dict, new_schema: dict) -> dict:
    old_props = old_schema.get("properties") or {}
    new_props = new_schema.get("properties") or {}

    old_keys = set(old_props)
    new_keys = set(new_props)

    type_changes: dict[str, dict[str, str]] = {}
    for key in old_keys & new_keys:
        old_type = old_props.get(key, {}).get("type", "unknown")
        new_type = new_props.get(key, {}).get("type", "unknown")
        if old_type != new_type:
            type_changes[key] = {"from": old_type, "to": new_type}

    old_required = set(old_schema.get("required", []))
    new_required = set(new_schema.get("required", []))

    return {
        "added": sorted(new_keys - old_keys),
        "removed": sorted(old_keys - new_keys),
        "type_changes": type_changes,
        "required_added": sorted(new_required - old_required),
        "required_removed": sorted(old_required - new_required),
        "unchanged": sorted(old_keys & new_keys),
    }


def assert_backward_compatible(old_schema: dict, new_schema: dict) -> None:
    diff = diff_schema(old_schema, new_schema)
    violations: list[str] = []
    if diff["removed"]:
        violations.append(f"Removed fields: {diff['removed']}")
    if diff["type_changes"]:
        violations.append(f"Type changes: {sorted(diff['type_changes'].keys())}")
    if diff["required_added"]:
        violations.append(f"New required fields: {diff['required_added']}")

    if violations:
        raise AssertionError("Backward incompatibility detected. " + " | ".join(violations))
