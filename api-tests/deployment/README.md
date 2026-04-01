# Deployment Layer (Kubernetes + GitLab + ADO + AWS + Dashboard)

This folder contains practical setup guides to make the framework portable across:

- local execution
- GitLab shell runners
- GitLab docker runners
- GitLab Kubernetes runners
- direct Kubernetes distributed jobs

## Setup Order

1. `k8s_setup.md`
2. `gitlab_runner_setup.md`
3. `ado_pat_setup.md`
4. `aws_iam_setup.md`
5. `dashboard_hosting.md`

## Outcome

After completing these guides, any team member can:

- select tags and trigger targeted runs
- run dry-runs / parallel / atomic execution
- publish artifacts and trends
- push results to Azure DevOps
- run the same test plan from any supported GitLab runner flavor
