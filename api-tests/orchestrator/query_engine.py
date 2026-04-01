from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class QueryClause:
    key: str
    values: list[str]


@dataclass(frozen=True)
class ParsedQuery:
    groups: list[list[QueryClause]]


def parse_query(query: str) -> ParsedQuery:
    """Parse a query into OR groups containing AND clauses.

    Supported syntax examples:
    - scope=api AND intent=functional
    - intent=functional AND module=users,orders OR intent=performance
    """
    if not query or not query.strip():
        return ParsedQuery(groups=[])

    groups: list[list[QueryClause]] = []
    for raw_group in _split_by_operator(query, "OR"):
        clauses: list[QueryClause] = []
        for token in _split_by_operator(raw_group, "AND"):
            if "=" not in token:
                raise ValueError(f"Invalid query token '{token}', expected key=value")
            key, raw_values = [part.strip() for part in token.split("=", 1)]
            values = [value.strip() for value in raw_values.split(",") if value.strip()]
            if not key or not values:
                raise ValueError(f"Invalid query token '{token}', expected key=value1,value2")
            clauses.append(QueryClause(key=key, values=values))
        if clauses:
            groups.append(clauses)
    return ParsedQuery(groups=groups)


def flatten_query(parsed: ParsedQuery) -> dict[str, list[str]]:
    """Backward compatibility helper for modules expecting a dict.

    For OR queries this merges values by key across groups.
    """
    merged: dict[str, set[str]] = {}
    for group in parsed.groups:
        for clause in group:
            merged.setdefault(clause.key, set()).update(clause.values)
    return {key: sorted(values) for key, values in merged.items()}


def matches_query(tags: dict[str, str], parsed: ParsedQuery) -> bool:
    if not parsed.groups:
        return True

    for group in parsed.groups:  # OR groups
        if _matches_all_clauses(tags, group):
            return True
    return False


def _matches_all_clauses(tags: dict[str, str], clauses: list[QueryClause]) -> bool:
    for clause in clauses:
        if tags.get(clause.key) not in clause.values:
            return False
    return True


def _split_by_operator(query: str, operator: str) -> list[str]:
    pattern = rf"\s+{operator}\s+"
    return [token.strip() for token in re.split(pattern, query.strip()) if token.strip()]
