from __future__ import annotations

from dataclasses import dataclass
import difflib
import re

from tagging.tag_config import INTENT_TYPE_MAP, REQUIRED_TAGS
from tagging.tag_model import TAG_MODEL

REQUIRED_KEYS = REQUIRED_TAGS | {"release"}
ALLOWED_SCOPE = set(TAG_MODEL)
ALLOWED_INTENT = {"functional", "performance"}
CONCERN_BY_INTENT = {
    intent: {concern for scope in TAG_MODEL.values() for concern in scope[intent]["concerns"]}
    for intent in ALLOWED_INTENT
}
TYPE_BY_INTENT = INTENT_TYPE_MAP

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
    suggestions: list[str]


def normalize_tag_value(value: str) -> str:
    return re.sub(r"[_\s]+", "-", (value or "").strip().lower())


def validate_intent_type(tags: dict[str, str]) -> None:
    intent = normalize_tag_value(tags.get("intent", ""))
    type_ = normalize_tag_value(tags.get("type", ""))

    if not intent or not type_:
        raise ValueError("Missing intent or type tag")

    allowed_types = INTENT_TYPE_MAP.get(intent)
    if not allowed_types:
        raise ValueError(f"Invalid intent: {intent}")

    if type_ not in allowed_types:
        raise ValueError(
            f"Invalid type '{type_}' for intent '{intent}'. "
            f"Allowed types: {sorted(allowed_types)}"
        )


def validate_full_tag_model(tags: dict[str, str]) -> None:
    scope = normalize_tag_value(tags.get("scope", ""))
    intent = normalize_tag_value(tags.get("intent", ""))
    concern = normalize_tag_value(tags.get("concern", ""))
    type_ = normalize_tag_value(tags.get("type", ""))

    if not scope or not intent or not concern or not type_:
        raise ValueError("Missing required tags")

    if scope not in TAG_MODEL:
        raise ValueError(f"Invalid scope: {scope}")

    if intent not in TAG_MODEL[scope]:
        raise ValueError(f"Invalid intent '{intent}' for scope '{scope}'")

    allowed = TAG_MODEL[scope][intent]

    if concern not in allowed["concerns"]:
        raise ValueError(
            f"Invalid concern '{concern}' for {scope}+{intent}. "
            f"Allowed: {sorted(allowed['concerns'])}"
        )

    if type_ not in allowed["types"]:
        raise ValueError(
            f"Invalid type '{type_}' for {scope}+{intent}. "
            f"Allowed: {sorted(allowed['types'])}"
        )


def validate_tags(tags: dict[str, str]) -> ValidationResult:
    errors: list[str] = []
    suggestions: list[str] = []

    normalized_keys = {k.strip().lower() for k in tags}
    missing = sorted(REQUIRED_KEYS - normalized_keys)
    if missing:
        errors.append(f"missing required tags: {missing}")

    unknown = sorted(normalized_keys - REQUIRED_KEYS)
    if unknown:
        errors.append(f"unknown tag keys are not allowed: {unknown}")

    normalized = {k.strip().lower(): normalize_tag_value(v) for k, v in tags.items()}

    for key, raw_value in tags.items():
        if isinstance(raw_value, str) and any(sep in raw_value for sep in [",", "|", ";"]):
            errors.append(f"tag {key} must have a single atomic value; multi-value tags are only allowed in query input")

    scope = normalized.get("scope")
    if scope and scope not in ALLOWED_SCOPE:
        errors.append(f"scope must be one of {sorted(ALLOWED_SCOPE)}")
        suggestions.append(f"did you mean scope={_closest_match(scope, ALLOWED_SCOPE, 'api')}?")

    intent = normalized.get("intent")
    if intent and intent not in ALLOWED_INTENT:
        errors.append(f"intent must be one of {sorted(ALLOWED_INTENT)}")
        fixed = _closest_match(intent, ALLOWED_INTENT, "functional")
        suggestions.append(f"did you mean intent={fixed}?")
        intent = fixed

    concern = normalized.get("concern")
    test_type = normalized.get("type")

    if intent in CONCERN_BY_INTENT:
        allowed_concern = CONCERN_BY_INTENT[intent]
        if concern and concern not in allowed_concern:
            errors.append(f"{intent} concern must be one of {sorted(allowed_concern)}")
            suggestions.append(f"concern suggestion: {_closest_match(concern, allowed_concern, sorted(allowed_concern)[0])}")

    if intent in TYPE_BY_INTENT:
        allowed_types = TYPE_BY_INTENT[intent]
        if test_type and test_type not in allowed_types:
            errors.append(f"{intent} type must be one of {sorted(allowed_types)}")
            suggestions.append(f"type suggestion: {_closest_match(test_type, allowed_types, sorted(allowed_types)[0])}")

    strict_intent = normalized.get("intent")
    if strict_intent in INTENT_TYPE_MAP:
        try:
            validate_intent_type(normalized)
        except ValueError as exc:
            errors.append(str(exc))
            suggestions.append(f"allowed types for intent={strict_intent}: {sorted(INTENT_TYPE_MAP[strict_intent])}")
    try:
        validate_full_tag_model(normalized)
    except ValueError as exc:
        errors.append(str(exc))

    module = normalized.get("module")
    if module and module not in ALLOWED_MODULES:
        errors.append(f"module must be one of {sorted(ALLOWED_MODULES)}")
        suggestions.append(f"module suggestion: {_closest_match(module, ALLOWED_MODULES, 'platform')}")

    release = normalized.get("release", tags.get("release", ""))
    if release and not RELEASE_PATTERN.match(release.upper()):
        errors.append("release must match RYYYY.MM-SN (example: R2026.04-S7)")
        suggestions.append("release suggestion: R2026.04-S1")

    return ValidationResult(ok=not errors, errors=errors, suggestions=suggestions)


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
        if key == "concern" and merged.get("intent") in CONCERN_BY_INTENT:
            allowed = CONCERN_BY_INTENT[merged["intent"]]
            incoming = incoming if incoming in allowed else sorted(allowed)[0]
        if key == "type" and merged.get("intent") in TYPE_BY_INTENT:
            allowed = TYPE_BY_INTENT[merged["intent"]]
            incoming = incoming if incoming in allowed else sorted(allowed)[0]
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
