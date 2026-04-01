from __future__ import annotations

import pytest

from core.validators import validate_error_payload, validate_status_code


@pytest.mark.tag(
    "scope=api",
    "intent=functional",
    "concern=error",
    "type=regression",
    "module=payments",
    "release=R2026.04-S1",
)
def test_error_payload_structure_and_code() -> None:
    status = 422
    payload = {"error_code": "PAYMENT_422", "message": "payment amount must be positive"}

    validate_status_code(status, 422)
    validate_error_payload(payload, expected_code="PAYMENT_422", expected_message_contains="must be positive")
