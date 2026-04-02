from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tagging.tag_governance import TagGovernance


def main() -> int:
    parser = argparse.ArgumentParser(description="Strict intent/type and tag governance validator")
    parser.add_argument("paths", nargs="*", default=["functional", "performance", "governance", "tagging", "orchestrator"])
    args = parser.parse_args()

    roots = [Path(p) for p in args.paths if Path(p).exists()]
    report = TagGovernance().scan(roots)

    if report.ok:
        print("Tag validator check: PASS")
        return 0

    print("Tag validator check: FAIL")
    for issue in report.issues:
        print(f"- {issue.path}:{issue.line} -> {issue.message}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
