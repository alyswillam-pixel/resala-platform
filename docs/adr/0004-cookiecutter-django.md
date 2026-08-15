# 0004 - Scaffold the Backend with cookiecutter-django

 **Date:** 2026-08-15
 **Status:** Accepted

## Context

Having decided on Django (ADR 0002), the backend needed a starting project
structure. Hand-rolling settings splots, Docker configuration, and a custom
User model from scratch is time-consuming and error-prone for a team new to
production Django setups.

## Decision

Generate the backend using the `cookiecutter-django` template, with: Docker +
docker-compose for local dev, DRF enabled, Celery enabled (for furture approval-
gate notifications), Mailpit as the local mail catcher, Postgres 17 (matching
the Supabase project's version), no cloud provider integration (AWS/GCP/Azure), 
no frontend pipeline (Vite fully separate), GitHub as the CI tool, and .env
files excluded from version control.

## Consequences

* Comes with a custom User model already wired up, sensible settings splits
(base/local/production), and environment-variable-driven config; this fits
deploying to Render/Railway with `DATABASE_URL` pointed to Supabase.
* Default auth is allauth-oriented (session/cookie-based); since Django owns
auth via Know for the API (ADR 0002), `django-rest-knox` will be added on top 
rather than relying on cookiecutter's default auth flow.
* Requires Docker with a working Buildkit/buildx setup locally, and the Docker
daemon running; both were missing initially on the dev machine and needed separate
fixes. Installing `docker-buildx` , starting/enabling the `docker` systemd service, 
adding the user to the `docker` group.
* Generated project structure needed manual flattening (cookiecutter nests the
project under a folder names after `resala_platform` ) to sit directly inside 
`backend/` per the monorepo layout (ADR 0001).
