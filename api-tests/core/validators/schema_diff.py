from __future__ import annotations


def diff_schema_keys(old_schema: dict, new_schema: dict) -> dict:
    old_props = set((old_schema.get("properties") or {}).keys())
    new_props = set((new_schema.get("properties") or {}).keys())
    return {
        "added": sorted(new_props - old_props),
        "removed": sorted(old_props - new_props),
        "unchanged": sorted(old_props & new_props),
    }


def assert_backward_compatible(old_schema: dict, new_schema: dict) -> None:
    diff = diff_schema_keys(old_schema, new_schema)
    if diff["removed"]:
        raise AssertionError(f"Backward incompatibility detected. Removed fields: {diff['removed']}")
