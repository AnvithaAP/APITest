from __future__ import annotations

from jsonschema import Draft202012Validator


def validate_json_schema(instance: dict, schema: dict) -> None:
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(instance), key=lambda e: list(e.path))
    if not errors:
        return

    formatted = []
    for error in errors:
        path = ".".join(str(p) for p in error.path) or "<root>"
        formatted.append(f"{path}: {error.message}")

    raise AssertionError("Schema validation failed: " + " | ".join(formatted))
