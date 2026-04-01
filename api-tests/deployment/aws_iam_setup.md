# AWS IAM Role Assignment + Secrets

Use IAM roles instead of static keys.

## Principle

- runtime identity obtains credentials
- framework resolves secrets through IAM-authorized calls

## Minimal policy scope

- `secretsmanager:GetSecretValue` for specific secret ARNs

## Runtime wiring

- EKS: IRSA service account role
- EC2: instance profile
- ECS: task role

`config/secrets/aws_iam.py` handles retrieval using ambient IAM credentials.
