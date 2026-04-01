import pytest


@pytest.mark.tag("scope=api", "intent=functional", "concern=error", "type=sanity", "module=payments", "release=R2026.04-S7")
def test_validation_error_shape():
    response = {"status": 400, "error": {"code": "VALIDATION_FAILED", "message": "amount is required"}}
    assert (response["status"], response["error"]["code"]) == (400, "VALIDATION_FAILED")
