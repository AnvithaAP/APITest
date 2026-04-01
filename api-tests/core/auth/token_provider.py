from __future__ import annotations

from config.secrets_manager import get_secret


def get_bearer_token(secret_name: str = "API_BEARER_TOKEN") -> str:
    token = get_secret(secret_name)
    if not token:
        raise ValueError(f"Missing bearer token for secret '{secret_name}'")
    return token
