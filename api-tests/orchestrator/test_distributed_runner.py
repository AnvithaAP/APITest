from __future__ import annotations

import pytest

from runners.distributed_runner import _build_k8s_job_spec, _chunk_tests


@pytest.mark.tag("scope=api", "intent=functional", "concern=contract", "type=regression", "module=platform", "release=R2026.04-S7")
def test_chunk_tests_spreads_across_nodes() -> None:
    chunks = _chunk_tests(["a", "b", "c", "d", "e"], 3)
    assert chunks == [["a", "d"], ["b", "e"], ["c"]]


@pytest.mark.tag("scope=api", "intent=functional", "concern=auth", "type=smoke", "module=platform", "release=R2026.04-S7")
def test_build_k8s_job_spec_contains_job_and_container_details() -> None:
    spec = _build_k8s_job_spec(1, "scope=api", "api-tests", "api", ["a"], "qa")
    assert spec["kind"] == "Job"
    assert spec["metadata"]["namespace"] == "qa"
    assert spec["spec"]["template"]["spec"]["containers"][0]["name"] == "runner"
