@scope:api
@intent:functional
@concern:behavior
@type:smoke
@module:platform
@release:R2026.04-S1
Feature: API health and readiness

  Scenario: Readiness endpoint returns healthy payload
    Given the readiness endpoint is reachable
    When I request the readiness status
    Then the API should report healthy
