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


TAG_INHERITANCE = {
    "scope": {
        "e2e": ["ui", "api"],
        "device": ["api"],
    },
    "intent": {
        "reliability": ["functional"],
    },
}


def parse_query(query: str) -> ParsedQuery:
    """Parse query with parenthesized AND/OR support into DNF groups."""
    if not query or not query.strip():
        return ParsedQuery(groups=[])

    tokens = _tokenize(query)
    groups, idx = _parse_expression(tokens, 0)
    if idx != len(tokens):
        raise ValueError(f"Unexpected token '{tokens[idx]}'")
    return ParsedQuery(groups=groups)


def parse_ui_selections(filters: dict[str, list[str]], group_operator: str = "AND") -> ParsedQuery:
    """Convert multi-select UI filters to query groups.

    - AND mode: every key must match any selected value in that key.
    - OR mode: any key/value pair can match.
    """
    normalized = {k: [v for v in values if v] for k, values in filters.items() if values}
    if not normalized:
        return ParsedQuery(groups=[])

    if group_operator.upper() == "OR":
        groups: list[list[QueryClause]] = []
        for key, values in normalized.items():
            for value in values:
                groups.append([QueryClause(key=key, values=[value])])
        return ParsedQuery(groups=groups)

    clauses = [QueryClause(key=key, values=values) for key, values in normalized.items()]
    return ParsedQuery(groups=[clauses])



def build_query_string(filters: dict[str, list[str]], group_operator: str = "AND", intra_field_operator: str = "OR") -> str:
    """Build a human-readable query string from structured filters.

    intra_field_operator controls multi-value semantics for one field.
    """
    parsed = parse_ui_selections(filters, group_operator=group_operator)
    if not parsed.groups:
        return ""

    groups: list[str] = []
    for group in parsed.groups:
        parts: list[str] = []
        for clause in group:
            if len(clause.values) == 1:
                parts.append(f"{clause.key}={clause.values[0]}")
            else:
                sep = f" {intra_field_operator.upper()} "
                parts.append("(" + sep.join(f"{clause.key}={v}" for v in clause.values) + ")")
        groups.append(" AND ".join(parts))
    return " OR ".join(groups)

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

        expanded_actual = set(actual_values)
        expanded_expected = {v.lower() for v in clause.values}

        if clause.key in TAG_INHERITANCE:
            expanded_actual |= _expand_inheritance(clause.key, actual_values)
            expanded_expected |= _expand_inheritance(clause.key, expanded_expected)

        if expanded_actual.isdisjoint(expanded_expected):
            return False
    return True


def _expand_inheritance(key: str, values: set[str]) -> set[str]:
    inherited: set[str] = set()
    relationships = TAG_INHERITANCE.get(key, {})
    for value in values:
        inherited.update(relationships.get(value, []))
    return inherited


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
