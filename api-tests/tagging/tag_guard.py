from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

import pytest

from tagging.tag_parser import parse_tag_entries
from tagging.tag_validator import suggest_autofix, validate_tags


@dataclass
class AutoFixResult:
    file_path: str
    changed: bool
    reason: str


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
                hints = f" suggestions={validation.suggestions}" if validation.suggestions else ""
                errors.append(f"{item.nodeid}: {validation.errors}{hints} | suggested fix: {fix}")
        return errors


def autofix_file(path: str) -> AutoFixResult:
    file_path = Path(path)
    text = file_path.read_text(encoding="utf-8")

    tag_match = re.search(r"@pytest\.mark\.tag\((?P<body>.*?)\)\s*\n\s*def\s+test_", text, flags=re.S)
    if not tag_match:
        insertion = suggest_autofix({}) + "\n"
        patched = re.sub(r"(\n\s*def\s+test_)", f"\n{insertion}\\1", text, count=1)
        if patched == text:
            return AutoFixResult(path, False, "no test function found")
        file_path.write_text(patched, encoding="utf-8")
        return AutoFixResult(path, True, "inserted default tags")

    raw_entries = [item.strip().strip('"\'') for item in tag_match.group("body").split(",") if item.strip()]
    tags, parse_errors = parse_tag_entries(tuple(raw_entries))
    if parse_errors:
        tags = {}
    valid = validate_tags(tags)
    if valid.ok:
        return AutoFixResult(path, False, "already valid")

    replacement = suggest_autofix(tags)
    start, end = tag_match.span()
    marker_block = text[start:end]
    new_block = re.sub(r"@pytest\.mark\.tag\((.*?)\)", replacement, marker_block, flags=re.S)
    file_path.write_text(text[:start] + new_block + text[end:], encoding="utf-8")
    return AutoFixResult(path, True, "updated invalid tag marker")
