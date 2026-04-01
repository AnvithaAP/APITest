from __future__ import annotations

import json
from pathlib import Path

import pytest

from tagging.tag_guard import TagGuard
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


collector = ResultCollector()


def _extract_item_tags(item: pytest.Item) -> dict[str, str]:
    tag_marks = [m for m in item.iter_markers(name="tag")]
    if not tag_marks:
        return {}
    tags, _ = parse_tag_entries(tuple(tag_marks[0].args))
    return tags


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption("--tag-query", action="store", default="", help="Tag query format: key=v1,v2 AND key2=v")


def pytest_configure(config: pytest.Config) -> None:
    config.pluginmanager.register(collector, "result-collector")


def pytest_collection_modifyitems(session: pytest.Session, config: pytest.Config, items: list[pytest.Item]) -> None:
    guard = TagGuard()
    errors = guard.validate_pytest_items(items)
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
