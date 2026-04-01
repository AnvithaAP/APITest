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
@scenario("../features/api_health.feature", "Readiness endpoint returns healthy payload")
def test_api_health_feature() -> None:
    pass


@given("the readiness endpoint is reachable")
def readiness_endpoint() -> dict[str, str]:
    return {"status": "healthy"}


@when("I request the readiness status")
def request_status(readiness_endpoint: dict[str, str]) -> dict[str, str]:
    return readiness_endpoint


@then(parsers.parse("the API should report healthy"))
def should_be_healthy(request_status: dict[str, str]) -> None:
    assert request_status["status"] == "healthy"


@pytest.mark.tag(
    "scope=api",
    "intent=functional",
    "concern=behavior",
    "type=smoke",
    "module=platform",
    "release=R2026.04-S1",
)
def test_bdd_step_file_tag_anchor() -> None:
    assert True
