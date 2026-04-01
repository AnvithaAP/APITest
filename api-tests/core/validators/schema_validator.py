from __future__ import annotations

from jsonschema import Draft202012Validator


def validate_json_schema(instance: dict, schema: dict) -> None:
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(instance), key=lambda e: e.path)
    if errors:
        head = errors[0]
        path = ".".join(str(p) for p in head.path) or "<root>"
        raise AssertionError(f"Schema validation failed at {path}: {head.message}")
