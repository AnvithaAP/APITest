from __future__ import annotations

import subprocess
import sys


GOVERNANCE_PATHS = [
    "governance/headers",
    "governance/conventions",
    "governance/standards",
]


def run_governance_suite() -> int:
    cmd = [sys.executable, "-m", "pytest", *GOVERNANCE_PATHS]
    return subprocess.call(cmd)


if __name__ == "__main__":
    raise SystemExit(run_governance_suite())
