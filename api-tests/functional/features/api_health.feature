@scope_api
@intent_functional
@concern_data
@type_regression
@module_platform
@release_R2026.04-S1
Feature: API health and readiness

  Scenario: Readiness endpoint returns healthy payload
    Given the readiness endpoint is reachable
    When I request the readiness status
    Then the API should report healthy
