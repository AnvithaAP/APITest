from __future__ import annotations

from pathlib import Path
import re

import pytest

from tagging.tag_parser import parse_tag_entries
from tagging.tag_validator import REQUIRED_KEYS, suggest_autofix, validate_tags


class TagGuard:
    def __init__(self, strict: bool = True, autofix: bool = False) -> None:
        self.strict = strict
        self.autofix = autofix

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
                continue

            missing_values = [k for k in REQUIRED_KEYS if not tags.get(k)]
            if missing_values:
                errors.append(f"{item.nodeid}: empty values not allowed for keys {sorted(missing_values)}")

        if errors and self.autofix:
            self.autofix_files(items)
        return errors if self.strict else []

    def autofix_files(self, items: list[pytest.Item]) -> None:
        by_file: dict[Path, str] = {}
        for item in items:
            tag_marks = [m for m in item.iter_markers(name="tag")]
            if len(tag_marks) != 1:
                continue
            tags, parse_errors = parse_tag_entries(tuple(tag_marks[0].args))
            if parse_errors:
                continue
            validation = validate_tags(tags)
            if validation.ok:
                continue
            by_file[Path(str(item.fspath))] = suggest_autofix(tags)

        for file_path, replacement in by_file.items():
            source = file_path.read_text(encoding="utf-8")
            updated = re.sub(r"@pytest\.mark\.tag\([^\)]*\)", replacement, source, count=1, flags=re.MULTILINE)
            if updated != source:
                file_path.write_text(updated, encoding="utf-8")
