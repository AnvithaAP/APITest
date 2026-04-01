import pytest

from tagging.tag_parser import compile_query_expression, evaluate_query_expression, parse_query


@pytest.mark.tag("scope=api", "intent=functional", "concern=contract", "type=regression", "module=platform")
def test_parse_query_supports_and_only():
    assert parse_query("scope=api AND intent=functional") == {"scope": "api", "intent": "functional"}


@pytest.mark.tag("scope=api", "intent=functional", "concern=contract", "type=regression", "module=platform")
def test_compile_and_evaluate_or_expression():
    rpn = compile_query_expression("scope=api AND (intent=functional OR concern=latency)")
    assert evaluate_query_expression(rpn, {"scope": "api", "intent": "functional"}) is True
    assert evaluate_query_expression(rpn, {"scope": "api", "concern": "latency"}) is True
    assert evaluate_query_expression(rpn, {"scope": "web", "concern": "latency"}) is False
