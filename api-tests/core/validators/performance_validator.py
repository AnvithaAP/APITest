from __future__ import annotations


def validate_response_time(duration_ms: float, threshold_ms: float) -> None:
    if duration_ms > threshold_ms:
        raise AssertionError(
            f"Response time {duration_ms:.2f}ms exceeded threshold {threshold_ms:.2f}ms"
        )


def validate_percentile(value_ms: float, percentile_name: str, threshold_ms: float) -> None:
    if value_ms > threshold_ms:
        raise AssertionError(f"{percentile_name}={value_ms:.2f}ms exceeded threshold {threshold_ms:.2f}ms")
