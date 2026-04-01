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



