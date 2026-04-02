from __future__ import annotations

import ast
import json
from pathlib import Path
import re

import pytest

from reporting.cucumber_formatter import build_cucumber_report, write_cucumber_report
from reporting.standardized_report import build_standardized_report, write_standardized_report
from tagging.tag_config import INTENT_TYPE_MAP
from tagging.tag_guard import TagGuard
from tagging.tag_validator import validate_intent_type
from tagging.tag_parser import matches_query, parse_query_groups, parse_tag_entries


class ResultCollector:
    def __init__(self) -> None:
        self.tests: list[dict] = []

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_makereport(self, item: pytest.Item, call: pytest.CallInfo):
        outcome = yield
        rep = outcome.get_result()
        if rep.when != "call":
            return
        tags = _extract_item_tags(item)
        self.tests.append(
            {
                "nodeid": item.nodeid,
                "outcome": rep.outcome,
                "call": {"duration": rep.duration},
                "keywords": {k: True for k in item.keywords.keys()},
                "tags": tags,
            }
        )

    def pytest_sessionfinish(self, session: pytest.Session, exitstatus: int) -> None:
        summary = {"total": len(self.tests), "passed": 0, "failed": 0, "skipped": 0}
        for t in self.tests:
            summary[t["outcome"]] = summary.get(t["outcome"], 0) + 1
        report = {"tests": self.tests, "summary": summary}
        out = Path("artifacts/pytest_report.json")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2), encoding="utf-8")

        cucumber = build_cucumber_report(report)
        write_cucumber_report(cucumber)
        if self.tests:
            repo = Path.cwd().name
            minimal_canonical = {
                "source_repo": repo,
                "run_id": f"{repo}-{exitstatus}",
                "scope": "api",
                "intent": "functional",
                "summary": summary,
            }
            write_standardized_report(build_standardized_report(minimal_canonical, cucumber))


collector = ResultCollector()

_TAG_PREFIXES = {"scope", "intent", "concern", "type", "module", "release"}
_BDD_ALIAS_MAP = {
    "api": "scope=api",
    "ui": "scope=ui",
    "e2e": "scope=e2e",
    "device": "scope=device",
    "functional": "intent=functional",
    "performance": "intent=performance",
    "governance": "intent=governance",
    "reliability": "intent=reliability",
    "smoke": "type=smoke",
    "sanity": "type=sanity",
    "regression": "type=regression",
    "system": "type=system",
    "load": "type=load",
    "compliance": "type=compliance",
    "standard": "type=standard",
}


def _normalize_bdd_tag(token: str) -> str | None:
    cleaned = token.strip().lstrip("@").lower()
    if not cleaned:
        return None

    if cleaned in _BDD_ALIAS_MAP:
        return _BDD_ALIAS_MAP[cleaned]

    for sep in (":", "="):
        if sep in cleaned:
            key, value = cleaned.split(sep, 1)
            if key in _TAG_PREFIXES and value:
                return f"{key}={value}"
            return None

    underscore = re.match(r"^(scope|intent|concern|type|module|release)_(.+)$", cleaned)
    if underscore:
        return f"{underscore.group(1)}={underscore.group(2)}"
    return None


def _infer_tags_from_keywords(item: pytest.Item) -> dict[str, str]:
    inferred: dict[str, str] = {}
    for keyword in item.keywords.keys():
        normalized = _normalize_bdd_tag(keyword)
        if not normalized:
            continue
        key, value = normalized.split("=", 1)
        inferred.setdefault(key, value)
    return inferred


def _extract_item_tags(item: pytest.Item) -> dict[str, str]:
    tag_marks = [m for m in item.iter_markers(name="tag")]
    if tag_marks:
        tags, _ = parse_tag_entries(tuple(tag_marks[0].args))
        return tags
    return _infer_tags_from_keywords(item)




def extract_tags(item: pytest.Item) -> dict[str, str]:
    tags: dict[str, str] = {}
    for marker in item.iter_markers():
        if marker.name.startswith("scope_"):
            tags["scope"] = marker.name.split("_", 1)[1]
        elif marker.name.startswith("intent_"):
            tags["intent"] = marker.name.split("_", 1)[1]
        elif marker.name.startswith("type_"):
            tags["type"] = marker.name.split("_", 1)[1]
        elif marker.name.startswith("concern_"):
            tags["concern"] = marker.name.split("_", 1)[1]
        elif marker.name.startswith("module_"):
            tags["module"] = marker.name.split("_", 1)[1]
    return tags

def _validate_atomic_tests(items: list[pytest.Item]) -> list[str]:
    violations: list[str] = []
    for item in items:
        path = Path(str(item.fspath))
        normalized = str(path).replace('\\', '/')
        if '/functional/' not in normalized and '/performance/' not in normalized:
            continue
        try:
            source = path.read_text(encoding="utf-8")
        except OSError:
            continue

        module = ast.parse(source)
        fn_name = item.name.split("[")[0]
        fn = next(
            (
                node
                for node in ast.walk(module)
                if isinstance(node, ast.FunctionDef) and node.name == fn_name
            ),
            None,
        )
        if fn is None:
            continue
        assert_stmt_count = sum(1 for node in ast.walk(fn) if isinstance(node, ast.Assert))
        assert_call_count = sum(
            1
            for node in ast.walk(fn)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and str(node.func.attr).startswith("assert")
        )
        total_assertions = assert_stmt_count + assert_call_count
        if total_assertions > 1:
            violations.append(
                f"{item.nodeid} has {total_assertions} assertion checks; atomic policy allows 1 assertion per test"
            )
    return violations


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption("--tag-query", action="store", default="", help="Tag query format: key=v1,v2 AND key2=v")


def pytest_configure(config: pytest.Config) -> None:
    config.pluginmanager.register(collector, "result-collector")


def pytest_collection_modifyitems(session: pytest.Session, config: pytest.Config, items: list[pytest.Item]) -> None:
    for item in items:
        if list(item.iter_markers(name="tag")):
            continue
        inferred = _infer_tags_from_keywords(item)
        if inferred:
            item.add_marker(pytest.mark.tag(*(f"{k}={v}" for k, v in sorted(inferred.items()))))

    guard = TagGuard()
    errors = guard.validate_pytest_items(items)
    for item in items:
        try:
            extracted = extract_tags(item)
            if extracted and extracted.get("intent") in INTENT_TYPE_MAP:
                validate_intent_type(extracted)
        except ValueError as exc:
            errors.append(f"{item.nodeid}: {exc}")
    errors.extend(_validate_atomic_tests(items))
    if errors:
        formatted = "\n".join(f"- {e}" for e in errors)
        raise pytest.UsageError(f"Tag guard validation failed:\n{formatted}")

    query = config.getoption("--tag-query")
    filters = parse_query_groups(query)
    if not filters:
        return

    selected: list[pytest.Item] = []
    deselected: list[pytest.Item] = []
    for item in items:
        tags = _extract_item_tags(item)
        if matches_query(tags, filters):
            selected.append(item)
        else:
            deselected.append(item)

    if deselected:
        config.hook.pytest_deselected(items=deselected)
    items[:] = selected
