from __future__ import annotations

import argparse
import subprocess
import sys

REQUIRED_HEADERS = {"content-type", "authorization", "x-correlation-id"}


def validate_headers(headers: dict[str, str]) -> list[str]:
    normalized = {k.lower(): v for k, v in headers.items()}
    errors: list[str] = []
    missing = sorted(REQUIRED_HEADERS - set(normalized.keys()))
    if missing:
        errors.append(f"Missing required headers: {missing}")
    if normalized.get("content-type") not in {"application/json", "application/problem+json"}:
        errors.append("content-type must be application/json or application/problem+json")
    if "authorization" in normalized and not normalized["authorization"].startswith("Bearer "):
        errors.append("authorization must use Bearer scheme")
    return errors


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
