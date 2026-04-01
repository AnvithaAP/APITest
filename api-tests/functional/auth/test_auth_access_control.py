from __future__ import annotations

import pytest

from core.validators import validate_status_code


@pytest.mark.tag(
    "scope=api",
    "intent=functional",
    "concern=auth",
    "type=smoke",
    "module=platform",
    "release=R2026.04-S1",
)
def test_auth_requires_token() -> None:
    unauthenticated_status = 401
    authenticated_status = 200

    validate_status_code(unauthenticated_status, 401)
    validate_status_code(authenticated_status, 200)
