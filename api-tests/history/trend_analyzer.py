from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import argparse

from history.html_trend_report import render_trend_html
from history.sqlite_manager import SQLiteManager


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default="artifacts/history.db")
    parser.add_argument("--out", default="artifacts/history_trends.html")
    parser.add_argument("--window", type=int, default=20)
    args = parser.parse_args()

    manager = SQLiteManager(args.db)
    rows = manager.fetch_all()
    sampled = rows[-args.window :] if args.window > 0 else rows
    render_trend_html(sampled, args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
