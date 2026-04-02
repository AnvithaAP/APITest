from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import argparse

from orchestrator.run import run_query


parser = argparse.ArgumentParser()
parser.add_argument("--scope")
parser.add_argument("--intent")
parser.add_argument("--concern")
parser.add_argument("--type")
parser.add_argument("--module", default="all")
parser.add_argument("--dry-run", action="store_true")

args = parser.parse_args()

query = {
    "scope": args.scope,
    "intent": args.intent,
    "concern": args.concern,
    "type": args.type,
    "module": args.module,
}

run_query(query, dry_run=args.dry_run)
