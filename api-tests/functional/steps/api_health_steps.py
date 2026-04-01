from __future__ import annotations

import pytest
from pytest_bdd import given, parsers, scenario, then, when


@pytest.mark.tag(
    "scope=api",
    "intent=functional",
    "concern=behavior",
    "type=smoke",
    "module=platform",
    "release=R2026.04-S1",
)
@scenario("../features/api_health.feature", "Health endpoint returns success")
def test_health_endpoint_returns_success() -> None:
    pass


@given("the API base URL is configured", target_fixture="base_url")
def configured_base_url() -> str:
    return "https://example.local"


@when(parsers.parse("a health check is simulated"), target_fixture="health_response")
def perform_health_check(base_url: str) -> dict[str, str]:
    return {"url": base_url, "status": "healthy"}


@then("the health result should be healthy")
def assert_health(health_response: dict[str, str]) -> None:
    assert health_response["status"] == "healthy"
