from __future__ import annotations

import json
from pathlib import Path


def merge_canonical_reports(paths: list[str], output_path: str) -> Path:
    merged: list[dict] = []
    for path in paths:
        merged.append(json.loads(Path(path).read_text(encoding="utf-8")))
    out = Path(output_path)
    out.write_text(json.dumps({"runs": merged}, indent=2), encoding="utf-8")
    return out
