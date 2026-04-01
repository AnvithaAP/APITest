from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.validators.schema_diff import assert_backward_compatible, diff_schema


def main() -> int:
    parser = argparse.ArgumentParser(description="Schema validation + diff engine")
    parser.add_argument("--old", required=True)
    parser.add_argument("--new", required=True)
    parser.add_argument("--strict", action="store_true", help="Fail on backward incompatibility")
    args = parser.parse_args()

    old_schema = json.loads(Path(args.old).read_text(encoding="utf-8"))
    new_schema = json.loads(Path(args.new).read_text(encoding="utf-8"))

    report = diff_schema(old_schema, new_schema)
    print(json.dumps(report, indent=2))

    if args.strict:
        assert_backward_compatible(old_schema, new_schema)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
