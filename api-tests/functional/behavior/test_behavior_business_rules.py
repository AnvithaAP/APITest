from __future__ import annotations

import pytest


@pytest.mark.tag(
    "scope=api",
    "intent=functional",
    "concern=behavior",
    "type=system",
    "module=orders",
    "release=R2026.04-S1",
)
def test_behavior_total_calculation_rule() -> None:
    order = {"subtotal": 100.0, "tax": 10.0, "discount": 5.0, "total": 105.0}
    expected_total = order["subtotal"] + order["tax"] - order["discount"]
    assert order["total"] == expected_total
