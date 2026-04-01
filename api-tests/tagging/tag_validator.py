from __future__ import annotations

from dataclasses import dataclass
import re

REQUIRED_KEYS = {"scope", "intent", "concern", "type", "module", "release"}
ALLOWED_SCOPE = {"api"}
ALLOWED_INTENT = {"functional", "performance", "security", "reliability"}

CONCERN_BY_INTENT = {
    "functional": {"contract", "data", "behavior", "error", "auth"},
    "performance": {"latency", "capacity", "scalability", "stability"},
    "security": {"authn", "authz", "injection", "secrets", "transport"},
    "reliability": {"resilience", "timeouts", "retry", "chaos", "recovery"},
}

TYPE_BY_INTENT = {
    "functional": {"smoke", "sanity", "regression", "system"},
    "performance": {"load", "stress", "spike", "soak", "benchmark"},
    "security": {"smoke", "regression", "compliance"},
    "reliability": {"resilience", "recovery", "failover"},
}

ALLOWED_MODULES = {
    "users",
    "orders",
    "payments",
    "catalog",
    "platform",
    "device-detail-page",
    "data-ingestion",
}

RELEASE_PATTERN = re.compile(r"^R\d{4}\.\d{2}-S\d{1,2}$")


@dataclass
class ValidationResult:
    ok: bool
    errors: list[str]


def validate_tags(tags: dict[str, str]) -> ValidationResult:
    errors: list[str] = []

    missing = sorted(REQUIRED_KEYS - set(tags.keys()))
    if missing:
        errors.append(f"missing required tags: {missing}")

    if tags.get("scope") and tags["scope"] not in ALLOWED_SCOPE:
        errors.append("scope must be 'api'")

    intent = tags.get("intent")
    if intent and intent not in ALLOWED_INTENT:
        errors.append(f"intent must be one of {sorted(ALLOWED_INTENT)}")

    concern = tags.get("concern")
    test_type = tags.get("type")

    if intent in CONCERN_BY_INTENT:
        allowed_concern = CONCERN_BY_INTENT[intent]
        if concern and concern not in allowed_concern:
            errors.append(f"{intent} concern must be one of {sorted(allowed_concern)}")

    if intent in TYPE_BY_INTENT:
        allowed_types = TYPE_BY_INTENT[intent]
        if test_type and test_type not in allowed_types:
            errors.append(f"{intent} type must be one of {sorted(allowed_types)}")

    module = tags.get("module")
    if module and module not in ALLOWED_MODULES:
        errors.append(f"module must be one of {sorted(ALLOWED_MODULES)}")

    release = tags.get("release")
    if release and not RELEASE_PATTERN.match(release):
        errors.append("release must match RYYYY.MM-SN (example: R2026.04-S7)")

    return ValidationResult(ok=not errors, errors=errors)


def suggest_autofix(tags: dict[str, str]) -> str:
    defaults = {
        "scope": "api",
        "intent": "functional",
        "concern": "data",
        "type": "regression",
        "module": "platform",
        "release": "R2026.04-S1",
    }
    merged = {**defaults, **tags}
    ordered_keys = ["scope", "intent", "concern", "type", "module", "release"]
    ordered = [f"{k}={merged[k]}" for k in ordered_keys]
    return "@pytest.mark.tag(" + ", ".join([f'\"{part}\"' for part in ordered]) + ")"
