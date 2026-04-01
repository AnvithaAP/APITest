@scope:api
@intent:functional
@concern:behavior
@type:smoke
@module:platform
@release:R2026.04-S1
Feature: API health endpoint behavior

  Scenario: Health endpoint returns success
    Given the API base URL is configured
    When a health check is simulated
    Then the health result should be healthy
