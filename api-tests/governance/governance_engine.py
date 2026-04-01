from __future__ import annotations

import argparse
import subprocess
import sys


def main() -> int:
    parser = argparse.ArgumentParser(description="Governance test engine")
    parser.add_argument("--query", default="scope=api AND intent=functional")
    args = parser.parse_args()

    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "governance",
        f"--tag-query={args.query}",
    ]
    return subprocess.call(cmd)


if __name__ == "__main__":
    raise SystemExit(main())
