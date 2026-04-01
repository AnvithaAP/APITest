from __future__ import annotations

import pytest

import json
from pathlib import Path

from orchestrator.enterprise_orchestrator import _canonical_paths_from_results



@pytest.mark.tag("scope=api", "intent=governance", "concern=traceability", "type=compliance", "module=platform", "release=R2026.04-S7")
def test_canonical_paths_filters_existing_files(tmp_path: Path) -> None:
    good = tmp_path / "good.json"
    good.write_text("{}", encoding="utf-8")

    payload = {
        "results": [
            {"name": "a", "canonical": str(good)},
            {"name": "b", "canonical": str(tmp_path / "missing.json")},
            {"name": "c", "canonical": ""},
        ]
    }
    results = tmp_path / "results.json"
    results.write_text(json.dumps(payload), encoding="utf-8")

    resolved = _canonical_paths_from_results(str(results))
    assert resolved == [str(good)]
