# Dashboard Hosting (Domain + History + Trends)

## Frontend

Host `dashboard/frontend/index.html` on static hosting (S3+CloudFront, GitLab Pages, nginx).

## Backend

Expose FastAPI backend (`dashboard.backend:app`) behind ingress/API gateway.

## Domain setup

1. Create DNS record for dashboard domain
2. Attach TLS certificate
3. Restrict CORS to trusted dashboard origin(s)

## Value

Users can:

- run tests and inspect tagged outcomes
- track historical runs
- review trends and quality insights
