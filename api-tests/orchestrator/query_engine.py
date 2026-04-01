from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tagging.tag_parser import parse_query


def build_pytest_tag_filter(query: str) -> str:
    filters = parse_query(query)
    return " and ".join([f"{k}={v}" for k, v in filters.items()])


def query_to_marker_expression(query: str) -> str:
    filters = parse_query(query)
    if not filters:
        return ""
    # marker expression references the single marker name; precise filtering is performed in runner plugin.
    return "tag"
