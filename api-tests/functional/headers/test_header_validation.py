from __future__ import annotations

import pytest

from core.validators import validate_header_value, validate_required_headers


@pytest.mark.tag(
    "scope=api",
    "intent=functional",
    "concern=contract",
    "type=regression",
    "module=platform",
    "release=R2026.04-S1",
)
def test_header_compliance_for_json_apis() -> None:
    headers = {
        "Content-Type": "application/json",
        "X-Correlation-Id": "cid-123",
        "Cache-Control": "no-store",
    }

    validate_required_headers(headers, ["Content-Type", "X-Correlation-Id"])
    validate_header_value(headers, "Content-Type", "application/json")
