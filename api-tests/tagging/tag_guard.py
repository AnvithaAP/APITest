from __future__ import annotations

import pytest

from tagging.tag_parser import parse_tag_entries
from tagging.tag_validator import suggest_autofix, validate_tags


class TagGuard:
    def validate_pytest_items(self, items: list[pytest.Item]) -> list[str]:
        errors: list[str] = []
        for item in items:
            tag_marks = [m for m in item.iter_markers(name="tag")]
            if not tag_marks:
                errors.append(f"{item.nodeid}: missing @pytest.mark.tag(...)")
                continue

            if len(tag_marks) > 1:
                errors.append(f"{item.nodeid}: multiple tag markers found; use exactly one")
                continue

            tags, parse_errors = parse_tag_entries(tuple(tag_marks[0].args))
            if parse_errors:
                errors.append(f"{item.nodeid}: {', '.join(parse_errors)}")
                continue

            validation = validate_tags(tags)
            if not validation.ok:
                fix = suggest_autofix(tags)
                errors.append(f"{item.nodeid}: {validation.errors} | suggested fix: {fix}")
        return errors
