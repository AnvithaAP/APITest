from __future__ import annotations


def validate_required_headers(headers: dict[str, str], required: list[str]) -> None:
    normalized = {k.lower(): v for k, v in headers.items()}
    missing = [name for name in required if name.lower() not in normalized]
    if missing:
        raise AssertionError(f"Missing required headers: {missing}")


def validate_header_value(headers: dict[str, str], name: str, expected: str) -> None:
    normalized = {k.lower(): v for k, v in headers.items()}
    actual = normalized.get(name.lower())
    if actual != expected:
        raise AssertionError(f"Header {name!r} expected {expected!r}, got {actual!r}")
