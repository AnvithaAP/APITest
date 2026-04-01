from __future__ import annotations

from dataclasses import dataclass
import difflib
import re

REQUIRED_KEYS = {"scope", "intent", "concern", "type", "module", "release"}
ALLOWED_SCOPE = {"api", "ui", "e2e", "device"}
ALLOWED_INTENT = {"functional", "performance", "security", "reliability", "governance"}

CONCERN_BY_INTENT = {
    "functional": {"contract", "data", "behavior", "error", "auth"},
    "performance": {"latency", "capacity", "scalability", "stability"},
    "security": {"authn", "authz", "injection", "secrets", "transport"},
    "reliability": {"resilience", "timeouts", "retry", "chaos", "recovery"},
    "governance": {"headers", "conventions", "standards", "traceability"},
}

TYPE_BY_INTENT = {
    "functional": {"smoke", "sanity", "regression", "system"},
    "performance": {"load", "stress", "spike", "soak", "benchmark"},
    "security": {"smoke", "regression", "compliance"},
    "reliability": {"resilience", "recovery", "failover"},
    "governance": {"compliance", "policy", "standard"},
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


def normalize_tag_value(value: str) -> str:
    return re.sub(r"[_\s]+", "-", (value or "").strip().lower())


def validate_tags(tags: dict[str, str]) -> ValidationResult:
    errors: list[str] = []

    normalized_keys = {k.strip().lower() for k in tags}
    missing = sorted(REQUIRED_KEYS - normalized_keys)
    if missing:
        errors.append(f"missing required tags: {missing}")

    normalized = {k.strip().lower(): normalize_tag_value(v) for k, v in tags.items()}

    if normalized.get("scope") and normalized["scope"] not in ALLOWED_SCOPE:
        errors.append(f"scope must be one of {sorted(ALLOWED_SCOPE)}")

    intent = normalized.get("intent")
    if intent and intent not in ALLOWED_INTENT:
        errors.append(f"intent must be one of {sorted(ALLOWED_INTENT)}")

    concern = normalized.get("concern")
    test_type = normalized.get("type")

    if intent in CONCERN_BY_INTENT:
        allowed_concern = CONCERN_BY_INTENT[intent]
        if concern and concern not in allowed_concern:
            errors.append(f"{intent} concern must be one of {sorted(allowed_concern)}")

    if intent in TYPE_BY_INTENT:
        allowed_types = TYPE_BY_INTENT[intent]
        if test_type and test_type not in allowed_types:
            errors.append(f"{intent} type must be one of {sorted(allowed_types)}")

    module = normalized.get("module")
    if module and module not in ALLOWED_MODULES:
        errors.append(f"module must be one of {sorted(ALLOWED_MODULES)}")

    release = normalized.get("release", tags.get("release", ""))
    if release and not RELEASE_PATTERN.match(release.upper()):
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
    normalized = {k.strip().lower(): normalize_tag_value(v) for k, v in tags.items() if k}
    merged: dict[str, str] = {}
    for key, default in defaults.items():
        incoming = normalized.get(key, default)
        if key == "module" and incoming not in ALLOWED_MODULES:
            incoming = _closest_match(incoming, ALLOWED_MODULES, default)
        if key == "intent" and incoming not in ALLOWED_INTENT:
            incoming = _closest_match(incoming, ALLOWED_INTENT, default)
        if key == "scope" and incoming not in ALLOWED_SCOPE:
            incoming = default
        if key == "release":
            release_raw = tags.get("release", default).upper()
            incoming = release_raw if RELEASE_PATTERN.match(release_raw) else default
        merged[key] = incoming

    ordered_keys = ["scope", "intent", "concern", "type", "module", "release"]
    ordered = [f"{k}={merged[k]}" for k in ordered_keys]
    return "@pytest.mark.tag(" + ", ".join([f'\"{part}\"' for part in ordered]) + ")"


def _closest_match(value: str, candidates: set[str], fallback: str) -> str:
    if value in candidates:
        return value
    matches = difflib.get_close_matches(value, list(candidates), n=1, cutoff=0.5)
    return matches[0] if matches else fallback
