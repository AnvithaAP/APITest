from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tagging.tag_parser import parse_query


def build_pytest_tag_filter(query: str) -> str:
    filters = parse_query(query)
    parts: list[str] = []
    for k, values in filters.items():
        joined = ",".join(values)
        parts.append(f"{k}={joined}")
    return " and ".join(parts)


def query_to_marker_expression(query: str) -> str:
    filters = parse_query(query)
    if not filters:
        return ""
    return "tag"
