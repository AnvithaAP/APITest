from __future__ import annotations

from pathlib import Path


def ensure_allure_dir(path: str = "artifacts/allure-results") -> Path:
    out = Path(path)
    out.mkdir(parents=True, exist_ok=True)
    return out
