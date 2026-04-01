from __future__ import annotations

import os


def get_secret(secret_id: str, region: str | None = None) -> str:
    """Fetch secret from AWS Secrets Manager using IAM role credentials."""
    resolved_region = region or os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION")
    if not resolved_region:
        return ""

    try:
        import boto3

        session = boto3.session.Session(region_name=resolved_region)
        client = session.client("secretsmanager")
        response = client.get_secret_value(SecretId=secret_id)
        return response.get("SecretString", "") or ""
    except Exception:
        return ""
