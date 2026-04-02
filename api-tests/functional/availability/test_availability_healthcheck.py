from __future__ import annotations

import pytest

from core.validators import validate_service_availability


@pytest.mark.tag(
    "scope=api",
    "intent=functional",
    "concern=behavior",
    "type=smoke",
    "module=platform",
    "release=R2026.04-S1",
)
def test_availability_probe_with_retry() -> None:
    state = {"calls": 0}

    def probe() -> bool:
        state["calls"] += 1
        return state["calls"] >= 2

    validate_service_availability(probe, retries=3, wait_seconds=0)
