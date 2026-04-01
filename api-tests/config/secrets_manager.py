from __future__ import annotations

import os


def _aws_secret(secret_name: str) -> str:
    secret_id = os.getenv(f"AWS_SECRET_ID_{secret_name}", secret_name)
    region = os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION")
    try:
        import boto3

        kwargs = {"service_name": "secretsmanager"}
        if region:
            kwargs["region_name"] = region
        client = boto3.client(**kwargs)
        payload = client.get_secret_value(SecretId=secret_id)
        return payload.get("SecretString", "") or ""
    except Exception:
        return ""


def _gcp_secret(secret_name: str) -> str:
    project = os.getenv("GCP_PROJECT_ID", "")
    secret_id = os.getenv(f"GCP_SECRET_ID_{secret_name}", secret_name)
    version = os.getenv("GCP_SECRET_VERSION", "latest")
    if not project:
        return ""
    try:
        from google.cloud import secretmanager

        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{project}/secrets/{secret_id}/versions/{version}"
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode("utf-8")
    except Exception:
        return ""



def _vault_secret(secret_name: str) -> str:
    vault_addr = os.getenv("VAULT_ADDR", "")
    vault_token = os.getenv("VAULT_TOKEN", "")
    path = os.getenv(f"VAULT_SECRET_PATH_{secret_name}", f"secret/data/{secret_name.lower()}")
    key = os.getenv(f"VAULT_SECRET_KEY_{secret_name}", "value")
    if not vault_addr or not vault_token:
        return ""

    try:
        import requests

        url = f"{vault_addr.rstrip('/')}/v1/{path.lstrip('/')}"
        response = requests.get(url, headers={"X-Vault-Token": vault_token}, timeout=10)
        if response.status_code >= 400:
            return ""
        data = response.json()
        nested = data.get("data", {})
        if isinstance(nested.get("data"), dict):
            nested = nested.get("data", {})
        return nested.get(key, "") or ""
    except Exception:
        return ""

def get_secret(secret_name: str) -> str:
    env_value = os.getenv(secret_name)
    if env_value:
        return env_value

    aws_env_value = os.getenv(f"AWS_SECRET_{secret_name}")
    if aws_env_value:
        return aws_env_value

    gcp_env_value = os.getenv(f"GCP_SECRET_{secret_name}")
    if gcp_env_value:
        return gcp_env_value

    aws_value = _aws_secret(secret_name)
    if aws_value:
        return aws_value

    gcp_value = _gcp_secret(secret_name)
    if gcp_value:
        return gcp_value

    vault_value = _vault_secret(secret_name)
    if vault_value:
        return vault_value

    return ""
