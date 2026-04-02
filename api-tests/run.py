from __future__ import annotations

import argparse
import subprocess
import sys

from orchestrator.query_engine import build_query_from_tags, parse_query
from tagging.tag_validator import TYPE_BY_INTENT, normalize_tag_value

TAG_KEYS = ["scope", "intent", "concern", "type", "module", "release"]


def _split_multi(values: list[str] | None) -> list[str]:
    if not values:
        return []
    flattened: list[str] = []
    for value in values:
        flattened.extend([item.strip() for item in value.split(",") if item.strip()])
    return flattened


def _build_tag_filters(args: argparse.Namespace) -> dict[str, list[str]]:
    filters: dict[str, list[str]] = {}
    for key in TAG_KEYS:
        values = _split_multi(getattr(args, key, None))
        filters[key] = values if values else ["ALL"]
    return filters


def _enforce_intent_type_alignment(filters: dict[str, list[str]]) -> None:
    intents = [normalize_tag_value(v) for v in filters.get("intent", []) if v and v.upper() != "ALL"]
    types = [normalize_tag_value(v) for v in filters.get("type", []) if v and v.upper() != "ALL"]
    if not intents or not types:
        return

    disallowed: list[str] = []
    for intent in intents:
        allowed = TYPE_BY_INTENT.get(intent)
        if not allowed:
            continue
        for test_type in types:
            if test_type not in allowed:
                disallowed.append(f"intent={intent} is incompatible with type={test_type}; allowed={sorted(allowed)}")

    if disallowed:
        joined = "\n - ".join(disallowed)
        raise SystemExit(f"Strict tag enforcement failed:\n - {joined}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Single entry command for tagged test execution")
    for key in TAG_KEYS:
        parser.add_argument(f"--{key}", action="append", default=[], help=f"Multi-value {key}; use comma-separated or repeat flag")

    parser.add_argument("--query", default="", help="Full query expression; supports AND/OR and nested parentheses")
    parser.add_argument("--parallel", type=int, default=1)
    parser.add_argument("--runner", choices=["local", "docker", "k8s", "gitlab"], default="local")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--out", default="artifacts/entry_run.json")
    parser.add_argument("--atomic", action="store_true", default=True)
    args = parser.parse_args()

    filters = _build_tag_filters(args)
    _enforce_intent_type_alignment(filters)

    query = args.query.strip() or build_query_from_tags(filters, default_all=True)
    parse_query(query)

    cmd = [
        sys.executable,
        "orchestrator/execution_engine.py",
        "--query",
        query,
        "--parallel",
        str(max(1, args.parallel)),
        "--runner",
        args.runner,
        "--out",
        args.out,
        "--atomic",
    ]
    if args.dry_run:
        cmd.append("--dry-run")

    return subprocess.call(cmd)


if __name__ == "__main__":
    raise SystemExit(main())
