from __future__ import annotations

import argparse
import ast
from dataclasses import dataclass
from pathlib import Path
import re
import sys
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tagging.tag_parser import parse_tag_entries
from tagging.tag_validator import REQUIRED_KEYS, validate_tags

FEATURE_TAG_RE = re.compile(r"^\s*@(?P<tag>[A-Za-z0-9_.:-]+)\s*$")


@dataclass
class GovernanceIssue:
    path: str
    line: int
    message: str


@dataclass
class GovernanceReport:
    ok: bool
    issues: list[GovernanceIssue]


class TagGovernance:
    """Guardrails for scalable, queryable tagging across pytest + BDD features."""

    def scan(self, roots: Iterable[Path]) -> GovernanceReport:
        issues: list[GovernanceIssue] = []
        for root in roots:
            if root.is_file():
                issues.extend(self._scan_file(root))
                continue
            for path in root.rglob("*.py"):
                if path.name.startswith("test_"):
                    issues.extend(self._scan_pytest_file(path))
            for feature in root.rglob("*.feature"):
                issues.extend(self._scan_feature_file(feature))
        return GovernanceReport(ok=not issues, issues=issues)

    def _scan_file(self, path: Path) -> list[GovernanceIssue]:
        if path.suffix == ".py" and path.name.startswith("test_"):
            return self._scan_pytest_file(path)
        if path.suffix == ".feature":
            return self._scan_feature_file(path)
        return []

    def _scan_pytest_file(self, path: Path) -> list[GovernanceIssue]:
        text = path.read_text(encoding="utf-8")
        file_issues: list[GovernanceIssue] = []

        marker_calls = self._extract_pytest_tag_calls(text)
        if "def test_" in text and not marker_calls:
            file_issues.append(GovernanceIssue(str(path), 1, "missing @pytest.mark.tag(...) marker"))
            return file_issues

        for line, raw_entries, extraction_errors in marker_calls:
            if extraction_errors:
                file_issues.append(GovernanceIssue(str(path), line, f"tag parse errors: {extraction_errors}"))
                continue
            tags, parse_errors = parse_tag_entries(tuple(raw_entries))
            if parse_errors:
                file_issues.append(GovernanceIssue(str(path), line, f"tag parse errors: {parse_errors}"))
                continue

            result = validate_tags(tags)
            if not result.ok:
                file_issues.append(GovernanceIssue(str(path), line, f"invalid tags: {result.errors}"))

            normalized_keys = {k.lower().strip() for k in tags.keys()}
            missing = sorted(REQUIRED_KEYS - normalized_keys)
            if missing:
                file_issues.append(GovernanceIssue(str(path), line, f"missing required keys: {missing}"))

        return file_issues

    def _extract_pytest_tag_calls(self, text: str) -> list[tuple[int, list[str], list[str]]]:
        try:
            tree = ast.parse(text)
        except SyntaxError:
            return []

        calls: list[tuple[int, list[str], list[str]]] = []
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for dec in node.decorator_list:
                if not isinstance(dec, ast.Call):
                    continue
                if not self._is_pytest_tag_call(dec.func):
                    continue
                line = getattr(dec, "lineno", 1)
                entries: list[str] = []
                errors: list[str] = []
                for arg in dec.args:
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                        entries.append(arg.value)
                    else:
                        errors.append("tag entries must be string literals in decorators")
                calls.append((line, entries, errors))
        return calls

    @staticmethod
    def _is_pytest_tag_call(func: ast.AST) -> bool:
        if not isinstance(func, ast.Attribute) or func.attr != "tag":
            return False
        inner = func.value
        if not isinstance(inner, ast.Attribute) or inner.attr != "mark":
            return False
        base = inner.value
        return isinstance(base, ast.Name) and base.id == "pytest"

    def _scan_feature_file(self, path: Path) -> list[GovernanceIssue]:
        issues: list[GovernanceIssue] = []
        content = path.read_text(encoding="utf-8").splitlines()
        found_feature_tags = False
        feature_tags: dict[str, str] = {}

        for idx, line in enumerate(content, start=1):
            if line.strip().startswith("Feature:"):
                break
            match = FEATURE_TAG_RE.match(line)
            if not match:
                continue
            found_feature_tags = True
            parts = match.group("tag").split(":", 1)
            if len(parts) != 2:
                issues.append(GovernanceIssue(str(path), idx, "feature tag must be key:value"))
                continue
            key, value = parts[0].lower(), parts[1].strip()
            if key not in REQUIRED_KEYS:
                issues.append(GovernanceIssue(str(path), idx, f"unsupported feature tag key '{key}'"))
            if not value:
                issues.append(GovernanceIssue(str(path), idx, f"empty feature tag value for '{key}'"))
                continue
            if key in feature_tags:
                issues.append(GovernanceIssue(str(path), idx, f"duplicate feature tag key '{key}'"))
                continue
            feature_tags[key] = value

        if not found_feature_tags:
            issues.append(
                GovernanceIssue(
                    str(path),
                    1,
                    "feature-level tags are required (scope:intent:concern:type:module:release as key:value lines)",
                )
            )
            return issues

        normalized_keys = {k.lower().strip() for k in feature_tags.keys()}
        missing = sorted(REQUIRED_KEYS - normalized_keys)
        if missing:
            issues.append(GovernanceIssue(str(path), 1, f"missing required feature keys: {missing}"))

        result = validate_tags(feature_tags)
        if not result.ok:
            issues.append(GovernanceIssue(str(path), 1, f"invalid feature tags: {result.errors}"))

        return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="Tag governance guardrails for pytest and BDD feature files")
    parser.add_argument("paths", nargs="*", default=["functional", "performance", "governance", "tagging"])
    args = parser.parse_args()

    roots = [Path(p) for p in args.paths if Path(p).exists()]
    report = TagGovernance().scan(roots)

    if report.ok:
        print("Tag governance check: PASS")
        return 0

    print("Tag governance check: FAIL")
    for issue in report.issues:
        print(f"- {issue.path}:{issue.line} -> {issue.message}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
