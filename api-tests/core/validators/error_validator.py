from __future__ import annotations


def validate_error_payload(payload: dict, expected_code: str, expected_message_contains: str) -> None:
    code = payload.get("error_code")
    if code != expected_code:
        raise AssertionError(f"Expected error_code={expected_code!r}, got {code!r}")

    message = str(payload.get("message", ""))
    if expected_message_contains not in message:
        raise AssertionError(
            f"Expected error message to contain {expected_message_contains!r}, got {message!r}"
        )
