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


_TOKEN_RE = re.compile(r"\(|\)|\bAND\b|\bOR\b|[^\s()]+", re.IGNORECASE)


def parse_query(query: str) -> ParsedQuery:
    """Parse a query into disjunctive-normal-form OR groups containing AND clauses.

    Supports:
    - key=value
    - key=value1,value2
    - parentheses and precedence (AND > OR)

    Example:
      scope=api AND (intent=functional OR intent=performance)
    """
    if not query or not query.strip():
        return ParsedQuery(groups=[])

    tokens = _tokenize(query)
    groups, idx = _parse_expression(tokens, 0)
    if idx != len(tokens):
        raise ValueError(f"Unexpected token '{tokens[idx]}'")
    return ParsedQuery(groups=groups)


def flatten_query(parsed: ParsedQuery) -> dict[str, list[str]]:
    merged: dict[str, set[str]] = {}
    for group in parsed.groups:
        for clause in group:
            merged.setdefault(clause.key, set()).update(clause.values)
    return {key: sorted(values) for key, values in merged.items()}


def matches_query(tags: dict[str, str], parsed: ParsedQuery) -> bool:
    if not parsed.groups:
        return True
    for group in parsed.groups:
        if _matches_all_clauses(tags, group):
            return True
    return False


def _matches_all_clauses(tags: dict[str, str], clauses: list[QueryClause]) -> bool:
    for clause in clauses:
        actual_raw = tags.get(clause.key, "")
        actual_values = {v.strip().lower() for v in re.split(r"[|;,]", actual_raw) if v.strip()}
        if not actual_values:
            return False
        if actual_values.isdisjoint({v.lower() for v in clause.values}):
            return False
    return True


def _tokenize(query: str) -> list[str]:
    return [t.strip() for t in _TOKEN_RE.findall(query) if t.strip()]


def _parse_expression(tokens: list[str], idx: int) -> tuple[list[list[QueryClause]], int]:
    left, idx = _parse_term(tokens, idx)
    while idx < len(tokens) and tokens[idx].upper() == "OR":
        right, idx = _parse_term(tokens, idx + 1)
        left = left + right
    return left, idx


def _parse_term(tokens: list[str], idx: int) -> tuple[list[list[QueryClause]], int]:
    left, idx = _parse_factor(tokens, idx)
    while idx < len(tokens) and tokens[idx].upper() == "AND":
        right, idx = _parse_factor(tokens, idx + 1)
        left = _cross_and(left, right)
    return left, idx


def _parse_factor(tokens: list[str], idx: int) -> tuple[list[list[QueryClause]], int]:
    if idx >= len(tokens):
        raise ValueError("Incomplete query")
    token = tokens[idx]
    if token == "(":
        groups, idx = _parse_expression(tokens, idx + 1)
        if idx >= len(tokens) or tokens[idx] != ")":
            raise ValueError("Missing closing ')' in query")
        return groups, idx + 1
    if token in {"AND", "OR", ")"}:
        raise ValueError(f"Unexpected token '{token}'")
    return [[_parse_clause(token)]], idx + 1


def _parse_clause(token: str) -> QueryClause:
    if "=" not in token:
        raise ValueError(f"Invalid query token '{token}', expected key=value")
    key, raw_values = [part.strip() for part in token.split("=", 1)]
    values = [value.strip() for value in raw_values.split(",") if value.strip()]
    if not key or not values:
        raise ValueError(f"Invalid query token '{token}', expected key=value1,value2")
    return QueryClause(key=key, values=values)


def _cross_and(left: list[list[QueryClause]], right: list[list[QueryClause]]) -> list[list[QueryClause]]:
    product: list[list[QueryClause]] = []
    for left_group in left:
        for right_group in right:
            product.append(left_group + right_group)
    return product
