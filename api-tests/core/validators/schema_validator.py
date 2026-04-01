from __future__ import annotations


def _validate_type(value, expected: str) -> bool:
    mapping = {
        "integer": int,
        "string": str,
        "boolean": bool,
        "object": dict,
        "array": list,
    }
    py_type = mapping.get(expected)
    return True if py_type is None else isinstance(value, py_type)


def validate_json_schema(instance: dict, schema: dict) -> None:
    required = schema.get("required", [])
    properties = schema.get("properties", {})

    for key in required:
        if key not in instance:
            raise AssertionError(f"Schema validation failed: missing required key '{key}'")

    for key, rules in properties.items():
        if key not in instance:
            continue
        expected_type = rules.get("type")
        if expected_type and not _validate_type(instance[key], expected_type):
            raise AssertionError(
                f"Schema validation failed: key '{key}' expected {expected_type}, got {type(instance[key]).__name__}"
            )
