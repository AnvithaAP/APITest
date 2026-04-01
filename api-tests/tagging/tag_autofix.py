from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tagging.tag_guard import autofix_file


def main() -> int:
    parser = argparse.ArgumentParser(description="Auto-fix pytest tag markers")
    parser.add_argument("paths", nargs="*", default=["functional", "governance"])
    args = parser.parse_args()

    py_files: list[Path] = []
    for path in args.paths:
        p = Path(path)
        if p.is_file() and p.suffix == ".py":
            py_files.append(p)
        elif p.exists():
            py_files.extend(sorted(p.rglob("test_*.py")))

    for file_path in py_files:
        result = autofix_file(str(file_path))
        print(f"{result.file_path}: {'changed' if result.changed else 'ok'} ({result.reason})")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
