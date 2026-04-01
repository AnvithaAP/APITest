from __future__ import annotations

import argparse

from reporting.aggregator_client import merge_canonical_reports


def main() -> int:
    parser = argparse.ArgumentParser(description="Merge canonical or standardized BDD reports across repositories")
    parser.add_argument("inputs", nargs="+", help="Input report paths (canonical, aggregated, or standardized)")
    parser.add_argument("--out", default="artifacts/aggregated_canonical.json", help="Output aggregated JSON path")
    parser.add_argument("--allure-out", default="", help="Optional output directory for merged allure results")
    parser.add_argument("--sqlite-db", default="artifacts/history.db", help="SQLite history DB path")
    args = parser.parse_args()

    merge_canonical_reports(
        paths=args.inputs,
        output_path=args.out,
        copy_allure_to=args.allure_out or None,
        sqlite_db_path=args.sqlite_db,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
