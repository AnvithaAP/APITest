from __future__ import annotations

import pytest

from runners.distributed_runner import _chunk_tests


@pytest.mark.tag("scope=api", "intent=functional", "concern=contract", "type=regression", "module=platform", "release=R2026.04-S7")
def test_chunk_tests_spreads_across_nodes() -> None:
    chunks = _chunk_tests(["a", "b", "c", "d", "e"], 3)
    assert chunks == [["a", "d"], ["b", "e"], ["c"]]
