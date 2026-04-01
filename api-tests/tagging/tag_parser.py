from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Condition:
    key: str
    value: str


class QuerySyntaxError(ValueError):
    pass


def parse_tag_entries(entries: tuple[str, ...]) -> tuple[dict[str, str], list[str]]:
    tags: dict[str, str] = {}
    errors: list[str] = []
    for entry in entries:
        if "=" not in entry:
            errors.append(f"invalid tag format '{entry}', expected key=value")
            continue
        key, value = [s.strip() for s in entry.split("=", 1)]
        if key in tags:
            errors.append(f"duplicate tag key '{key}'")
            continue
        tags[key] = value
    return tags, errors


def _tokenize(query: str) -> list[str]:
    if not query:
        return []
    normalized = query.replace("(", " ( ").replace(")", " ) ")
    return [token.strip() for token in normalized.split() if token.strip()]


def parse_query(query: str) -> dict[str, str]:
    """
    Legacy helper that only supports pure AND expressions.
    """
    filters: dict[str, str] = {}
    if not query:
        return filters

    tokens = _tokenize(query)
    idx = 0
    while idx < len(tokens):
        token = tokens[idx]
        upper = token.upper()
        if upper in {"AND", "OR", "(", ")"}:
            if upper != "AND":
                raise QuerySyntaxError("parse_query only supports AND key=value expressions")
            idx += 1
            continue
        if "=" not in token:
            raise QuerySyntaxError(f"Invalid query token '{token}', expected key=value")
        key, value = [s.strip() for s in token.split("=", 1)]
        filters[key] = value
        idx += 1
    return filters


def _to_rpn(tokens: list[str]) -> list[str]:
    precedence = {"OR": 1, "AND": 2}
    output: list[str] = []
    operators: list[str] = []

    for token in tokens:
        upper = token.upper()
        if upper in precedence:
            while operators and operators[-1] in precedence and precedence[operators[-1]] >= precedence[upper]:
                output.append(operators.pop())
            operators.append(upper)
            continue
        if token == "(":
            operators.append(token)
            continue
        if token == ")":
            while operators and operators[-1] != "(":
                output.append(operators.pop())
            if not operators:
                raise QuerySyntaxError("Mismatched ')' in query")
            operators.pop()
            continue
        if "=" not in token:
            raise QuerySyntaxError(f"Invalid query token '{token}', expected key=value")
        output.append(token)

    while operators:
        op = operators.pop()
        if op == "(":
            raise QuerySyntaxError("Mismatched '(' in query")
        output.append(op)
    return output


def compile_query_expression(query: str) -> list[str]:
    tokens = _tokenize(query)
    if not tokens:
        return []
    return _to_rpn(tokens)


def evaluate_query_expression(rpn_tokens: list[str], tags: dict[str, str]) -> bool:
    if not rpn_tokens:
        return True

    stack: list[bool] = []
    for token in rpn_tokens:
        if token in {"AND", "OR"}:
            if len(stack) < 2:
                raise QuerySyntaxError("Malformed query expression")
            right = stack.pop()
            left = stack.pop()
            stack.append(left and right if token == "AND" else left or right)
            continue

        key, value = [s.strip() for s in token.split("=", 1)]
        stack.append(tags.get(key) == value)

    if len(stack) != 1:
        raise QuerySyntaxError("Malformed query expression")
    return stack[0]
