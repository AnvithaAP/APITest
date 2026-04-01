from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import argparse
import json
import subprocess
from datetime import datetime, timezone


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--simulation", default="simulations.BasicSimulation")
    parser.add_argument("--query", default="")
    args = parser.parse_args()
    cmd = ["gatling", "-s", args.simulation]
    rc = subprocess.call(cmd)

    out = Path("artifacts/performance_gatling.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(
            {
                "runner": "gatling",
                "simulation": args.simulation,
                "query": args.query,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "exit_code": rc,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
