from __future__ import annotations

from orchestrator.query_engine import (
    ParsedQuery,
    flatten_query,
    matches_query as evaluate_query,
    parse_query as parse_advanced_query,
    parse_ui_selections,
)
from tagging.tag_validator import normalize_tag_value


def parse_tag_entries(entries: tuple[str, ...]) -> tuple[dict[str, str], list[str]]:
    tags: dict[str, str] = {}
    errors: list[str] = []
    for entry in entries:
        if "=" not in entry:
            errors.append(f"invalid tag format '{entry}', expected key=value")
            continue
        key, value = [s.strip() for s in entry.split("=", 1)]
        key = key.lower()
        value = normalize_tag_value(value)
        if key in tags:
            errors.append(f"duplicate tag key '{key}'")
            continue
        tags[key] = value
    return tags, errors


def parse_query(query: str) -> dict[str, list[str]]:
    return flatten_query(parse_advanced_query(query))


def parse_query_groups(query: str) -> ParsedQuery:
    return parse_advanced_query(query)



def parse_ui_query(filters: dict[str, list[str]], group_operator: str = "AND") -> ParsedQuery:
    return parse_ui_selections(filters, group_operator=group_operator)

def matches_query(tags: dict[str, str], query_filters: dict[str, list[str]] | ParsedQuery) -> bool:
    if isinstance(query_filters, ParsedQuery):
        return evaluate_query(tags, query_filters)

    if not query_filters:
        return True
    for key, accepted_values in query_filters.items():
        actual = tags.get(key)
        if actual is None:
            return False
        actual_values = [normalize_tag_value(v) for v in actual.replace("|", ",").split(",") if v.strip()]
        normalized_expected = {normalize_tag_value(v) for v in accepted_values}
        if normalized_expected and set(actual_values).isdisjoint(normalized_expected):
            return False
    return True
