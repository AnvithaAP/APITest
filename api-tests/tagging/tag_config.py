from __future__ import annotations

REQUIRED_TAGS = {"scope", "intent", "concern", "type", "module"}

INTENT_TYPE_MAP = {
    "functional": {"smoke", "sanity", "regression", "system"},
    "performance": {"load", "stress", "spike", "soak", "benchmark"},
}
