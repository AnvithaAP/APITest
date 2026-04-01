from __future__ import annotations


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


def parse_query(query: str) -> dict[str, str]:
    filters: dict[str, str] = {}
    if not query:
        return filters
    for token in [part.strip() for part in query.split("AND")]:
        if not token:
            continue
        if "=" not in token:
            raise ValueError(f"Invalid query token '{token}', expected key=value")
        k, v = [s.strip() for s in token.split("=", 1)]
        filters[k] = v
    return filters
