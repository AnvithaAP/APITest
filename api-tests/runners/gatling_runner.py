from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import argparse
import subprocess


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--simulation", default="simulations.BasicSimulation")
    parser.add_argument("--query", default="")
    args = parser.parse_args()
    cmd = ["gatling", "-s", args.simulation]
    return subprocess.call(cmd)


if __name__ == "__main__":
    raise SystemExit(main())
