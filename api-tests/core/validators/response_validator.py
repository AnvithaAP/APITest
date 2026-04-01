from __future__ import annotations

from collections.abc import Iterable


def validate_status_code(actual: int, expected: int | Iterable[int]) -> None:
    if isinstance(expected, int):
        if actual != expected:
            raise AssertionError(f"Expected status {expected}, got {actual}")
        return

    expected_set = set(expected)
    if actual not in expected_set:
        raise AssertionError(f"Expected status in {sorted(expected_set)}, got {actual}")


def validate_json_field(payload: dict, field: str, expected_value: object) -> None:
    if field not in payload:
        raise AssertionError(f"Expected field '{field}' to exist in response payload")
    if payload[field] != expected_value:
        raise AssertionError(f"Field '{field}' expected {expected_value!r}, got {payload[field]!r}")


def validate_required_fields(payload: dict, required_fields: Iterable[str]) -> None:
    missing = [name for name in required_fields if name not in payload]
    if missing:
        raise AssertionError(f"Missing required fields: {missing}")
