from __future__ import annotations

import os


def get_secret(secret_name: str) -> str:
    # Pluggable provider chain: env -> AWS/GCP SDK integrations (optional wiring)
    env_value = os.getenv(secret_name)
    if env_value:
        return env_value
    aws_value = os.getenv(f"AWS_SECRET_{secret_name}")
    if aws_value:
        return aws_value
    gcp_value = os.getenv(f"GCP_SECRET_{secret_name}")
    if gcp_value:
        return gcp_value
    return ""
