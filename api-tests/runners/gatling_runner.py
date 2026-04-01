from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import argparse
import subprocess

from tagging.tag_parser import parse_query


SIMULATION_BY_CONCERN = {
    "latency": "simulations.LatencySimulation",
    "capacity": "simulations.CapacitySimulation",
    "scalability": "simulations.ScalabilitySimulation",
    "stability": "simulations.StabilitySimulation",
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--simulation", default="")
    parser.add_argument("--query", default="")
    args = parser.parse_args()

    simulation = args.simulation
    if not simulation and args.query:
        concern = parse_query(args.query).get("concern", "")
        simulation = SIMULATION_BY_CONCERN.get(concern, "")
    simulation = simulation or "simulations.BasicSimulation"

    cmd = ["gatling", "-s", simulation]
    return subprocess.call(cmd)


if __name__ == "__main__":
    raise SystemExit(main())
