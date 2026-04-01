# Azure DevOps PAT + Project Wiring

## PAT scopes

Create PAT with:

- Test Management (read/write)
- Work Items (read/write)

## Environment

```bash
export ADO_ORG_URL="https://dev.azure.com/<org>"
export ADO_PROJECT="<project-name>"
export ADO_PAT="<pat>"
```

## Validate push

```bash
python integrations/ado_client.py \
  --aggregated artifacts/aggregated_canonical.json \
  --push \
  --org-url "$ADO_ORG_URL" \
  --project "$ADO_PROJECT" \
  --token "$ADO_PAT"
```

This supports:

- pushing results
- linking PBIs
- updating test runs
