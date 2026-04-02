from __future__ import annotations

from dataclasses import dataclass
import re

from tagging.tag_config import INTENT_TYPE_MAP
from tagging.tag_model import TAG_MODEL
from tagging.tag_validator import validate_full_tag_model, validate_intent_type


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
    parsed = ParsedQuery(groups=groups)
    validate_query_intent_type(parsed)
    return parsed


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
        parsed = ParsedQuery(groups=groups)
        validate_query_intent_type(parsed)
        return parsed

    clauses = [QueryClause(key=key, values=values) for key, values in normalized.items()]
    parsed = ParsedQuery(groups=[clauses])
    validate_query_intent_type(parsed)
    return parsed


def parse_nested_ui_tree(tree: dict) -> ParsedQuery:
    """Parse nested UI query tree to fully expressive query groups.

    Example tree:
      {"operator": "AND", "children": [
          {"key": "scope", "values": ["api", "ui"]},
          {"operator": "OR", "children": [
              {"key": "intent", "values": ["functional"]},
              {"key": "intent", "values": ["performance"]},
          ]}
      ]}
    """
    expression = _tree_to_expression(tree)
    return parse_query(expression)



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


def build_query_from_tags(filters: dict[str, list[str]], default_all: bool = True) -> str:
    """Build normalized query that supports multi-value input for every tag.

    Empty filters are interpreted as ALL and omitted from query when default_all=True.
    """
    clauses: list[str] = []
    for key, values in filters.items():
        clean_values = sorted({v.strip() for v in values if v and v.strip() and v.upper() != "ALL"})
        if not clean_values:
            if default_all:
                continue
            raise ValueError(f"tag '{key}' is empty and default_all is disabled")

        if len(clean_values) == 1:
            clauses.append(f"{key}={clean_values[0]}")
        else:
            nested = " OR ".join(f"{key}={value}" for value in clean_values)
            clauses.append(f"({nested})")

    return " AND ".join(clauses)


def validate_query_intent_type(parsed: ParsedQuery) -> None:
    for group in parsed.groups:
        intents = next((clause.values for clause in group if clause.key == "intent"), [])
        types = next((clause.values for clause in group if clause.key == "type"), [])
        scopes = next((clause.values for clause in group if clause.key == "scope"), [])
        concerns = next((clause.values for clause in group if clause.key == "concern"), [])
        if not intents or not types:
            # Allow partial queries but still validate complete tuple presence below.
            pass
        else:
            for intent in intents:
                if intent.lower() not in INTENT_TYPE_MAP:
                    continue
                for test_type in types:
                    validate_intent_type({"intent": intent, "type": test_type})

        if not scopes or not intents:
            continue
        for scope in scopes:
            for intent in intents:
                scope_norm = scope.lower()
                intent_norm = intent.lower()
                if scope_norm not in TAG_MODEL:
                    raise ValueError(f"Invalid scope: {scope_norm}")
                if intent_norm not in TAG_MODEL[scope_norm]:
                    raise ValueError(f"Invalid intent '{intent_norm}' for scope '{scope_norm}'")
                allowed = TAG_MODEL[scope_norm][intent_norm]
                for concern in concerns:
                    if concern.lower() not in allowed["concerns"]:
                        raise ValueError(
                            f"Invalid concern '{concern}' for {scope_norm}+{intent_norm}. "
                            f"Allowed: {sorted(allowed['concerns'])}"
                        )
                for type_ in types:
                    if type_.lower() not in allowed["types"]:
                        raise ValueError(
                            f"Invalid type '{type_}' for {scope_norm}+{intent_norm}. "
                            f"Allowed: {sorted(allowed['types'])}"
                        )
                if concerns and types:
                    for concern in concerns:
                        for type_ in types:
                            validate_full_tag_model(
                                {"scope": scope, "intent": intent, "concern": concern, "type": type_}
                            )


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


def _tree_to_expression(node: dict) -> str:
    if not node:
        return ""

    if "key" in node:
        key = str(node.get("key", "")).strip()
        values = [str(v).strip() for v in node.get("values", []) if str(v).strip()]
        if not key or not values:
            return ""
        if len(values) == 1:
            return f"{key}={values[0]}"
        joined = " OR ".join(f"{key}={value}" for value in values)
        return f"({joined})"

    operator = str(node.get("operator", "AND")).upper()
    children = node.get("children", [])
    rendered: list[str] = []
    for child in children:
        expr = _tree_to_expression(child)
        if expr:
            rendered.append(f"({expr})" if "children" in child and "key" not in child else expr)
    return f" {operator} ".join(rendered)
