from __future__ import annotations

from pathlib import Path
import yaml


BASE_DIR = Path(__file__).resolve().parents[2]


def load_yaml(relative_path: str) -> dict:
    path = BASE_DIR / relative_path
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}
