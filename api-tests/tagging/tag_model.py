from __future__ import annotations

TAG_MODEL = {
    "ui": {
        "functional": {
            "concerns": {"visual", "interaction", "data", "state", "flow"},
            "types": {"smoke", "sanity", "regression", "system"},
        },
        "performance": {
            "concerns": {
                "responsiveness",
                "rendering",
                "interactivity",
                "capacity",
                "scalability",
                "data_freshness",
                "stability",
            },
            "types": {"load", "stress", "spike", "soak", "benchmark"},
        },
    },
    "api": {
        "functional": {
            "concerns": {"contract", "data", "behavior", "error", "auth"},
            "types": {"smoke", "sanity", "regression", "system"},
        },
        "performance": {
            "concerns": {"latency", "capacity", "scalability", "stability"},
            "types": {"load", "stress", "spike", "soak", "benchmark"},
        },
    },
    "e2e": {
        "functional": {
            "concerns": {"journey", "data", "state", "integration", "resilience"},
            "types": {"smoke", "sanity", "regression", "system"},
        },
        "performance": {
            "concerns": {"journey", "throughput", "degradation", "scalability", "stability"},
            "types": {"load", "stress", "spike", "soak", "benchmark"},
        },
    },
    "device": {
        "functional": {
            "concerns": {"onboarding", "connectivity", "data", "command", "state"},
            "types": {"smoke", "sanity", "regression", "system"},
        },
        "performance": {
            "concerns": {"ingestion", "integrity", "capacity", "reliability", "latency"},
            "types": {"load", "stress", "spike", "soak", "benchmark"},
        },
    },
    "integration": {
        "functional": {
            "concerns": {"flow", "data", "contract", "state", "resilience"},
            "types": {"smoke", "sanity", "regression", "system"},
        },
        "performance": {
            "concerns": {"flow", "throughput", "bottleneck", "scalability", "stability"},
            "types": {"load", "stress", "spike", "soak", "benchmark"},
        },
    },
}

