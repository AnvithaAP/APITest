from __future__ import annotations

import time
from collections.abc import Callable


def validate_service_availability(probe: Callable[[], bool], retries: int = 3, wait_seconds: float = 0.2) -> None:
    for attempt in range(1, retries + 1):
        if probe():
            return
        if attempt < retries:
            time.sleep(wait_seconds)
    raise AssertionError(f"Service availability probe failed after {retries} attempts")
