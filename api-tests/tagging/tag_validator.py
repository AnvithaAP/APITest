from __future__ import annotations

from dataclasses import dataclass

REQUIRED_KEYS = {"scope", "intent", "concern", "type", "module"}
ALLOWED_SCOPE = {"api"}
ALLOWED_INTENT = {"functional", "performance"}
FUNCTIONAL_CONCERNS = {"contract", "data", "behavior", "error", "auth"}
PERFORMANCE_CONCERNS = {"latency", "capacity", "scalability", "stability"}
FUNCTIONAL_TYPES = {"smoke", "sanity", "regression", "system"}
PERFORMANCE_TYPES = {"load", "stress", "spike", "soak", "benchmark"}
ALLOWED_MODULES = {"users", "orders", "payments", "catalog", "platform"}


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

    if intent == "functional":
        if concern and concern not in FUNCTIONAL_CONCERNS:
            errors.append(f"functional concern must be one of {sorted(FUNCTIONAL_CONCERNS)}")
        if test_type and test_type not in FUNCTIONAL_TYPES:
            errors.append(f"functional type must be one of {sorted(FUNCTIONAL_TYPES)}")

    if intent == "performance":
        if concern and concern not in PERFORMANCE_CONCERNS:
            errors.append(f"performance concern must be one of {sorted(PERFORMANCE_CONCERNS)}")
        if test_type and test_type not in PERFORMANCE_TYPES:
            errors.append(f"performance type must be one of {sorted(PERFORMANCE_TYPES)}")

    module = tags.get("module")
    if module and module not in ALLOWED_MODULES:
        errors.append(f"module must be one of {sorted(ALLOWED_MODULES)}")

    return ValidationResult(ok=not errors, errors=errors)


def suggest_autofix(tags: dict[str, str]) -> str:
    defaults = {
        "scope": "api",
        "intent": "functional",
        "concern": "data",
        "type": "regression",
        "module": "platform",
    }
    merged = {**defaults, **tags}
    ordered = [f"{k}={merged[k]}" for k in ["scope", "intent", "concern", "type", "module"]]
    return "@pytest.mark.tag(" + ", ".join([f'\"{part}\"' for part in ordered]) + ")"
