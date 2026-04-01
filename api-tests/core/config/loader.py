from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
import yaml


BASE_DIR = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class RuntimeConfig:
    environment: str
    base_url: str
    timeout_seconds: int
    default_release: str
    endpoints: dict


def load_yaml(relative_path: str) -> dict:
    path = BASE_DIR / relative_path
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def load_env_file(relative_path: str) -> dict[str, str]:
    """Minimal .env parser to avoid external dependencies."""
    path = BASE_DIR / relative_path
    if not path.exists():
        return {}

    data: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        data[key.strip()] = value.strip().strip('"').strip("'")
    return data


def _resolve_value(key: str, env_file_values: dict[str, str], default: str = "") -> str:
    """Precedence: OS env vars > runtime.env > default (ignores blank overrides)."""
    os_value = os.getenv(key)
    if os_value is not None and os_value.strip() != "":
        return os_value

    env_file_value = env_file_values.get(key)
    if env_file_value is not None and env_file_value.strip() != "":
        return env_file_value

    return default


def load_runtime_config() -> RuntimeConfig:
    env_config = load_yaml("config/env.yaml")
    endpoint_config = load_yaml("config/endpoints.yaml")
    runtime_env = load_env_file("config/runtime.env")

    environment = _resolve_value("API_ENV", runtime_env, env_config.get("environment", "local"))
    fallback_url = env_config.get("base_urls", {}).get(environment, "")
    base_url = _resolve_value("API_BASE_URL", runtime_env, fallback_url)
    timeout_seconds = int(
        _resolve_value(
            "REQUEST_TIMEOUT_SECONDS",
            runtime_env,
            str(env_config.get("timeouts", {}).get("request_seconds", 20)),
        )
    )
    default_release = _resolve_value("DEFAULT_RELEASE", runtime_env, "R2026.04-S1")

    return RuntimeConfig(
        environment=environment,
        base_url=base_url,
        timeout_seconds=timeout_seconds,
        default_release=default_release,
        endpoints=endpoint_config,
    )
