from __future__ import annotations

import pytest

from core.validators import validate_percentile, validate_response_time


@pytest.mark.tag(
    "scope=api",
    "intent=performance",
    "concern=latency",
    "type=benchmark",
    "module=platform",
    "release=R2026.04-S1",
)
def test_performance_thresholds() -> None:
    validate_response_time(duration_ms=120, threshold_ms=250)
    validate_percentile(value_ms=180, percentile_name="p95", threshold_ms=300)
