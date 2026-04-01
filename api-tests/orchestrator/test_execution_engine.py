from __future__ import annotations

from pathlib import Path

import pytest

from orchestrator.execution_engine import run_execution_engine


@pytest.mark.tag("scope=api","intent=functional","concern=behavior","type=smoke","module=platform","release=R2026.04-S1")
def test_execution_engine_dry_run_writes_selected_tests(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("orchestrator.execution_engine._discover_tests", lambda query: ["functional/test_a.py::test_a"])

    out = tmp_path / "engine.json"
    rc = run_execution_engine(
        query="scope=api",
        dry_run=True,
        parallel=2,
        atomic=False,
        runner="local",
        out=out,
    )

    assert rc == 0
    payload = out.read_text(encoding="utf-8")
    assert "dry-run" in payload
    assert "test_a" in payload
