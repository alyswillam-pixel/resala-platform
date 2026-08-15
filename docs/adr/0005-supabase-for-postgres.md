# 0005 - Use Supabase for PostgreSQL Hosting

 **Date:** 2026-08-15
 **Status:** Accepted

## Context

The platform needs a managed Postgres database without the team taking on the
database ops overhead, within a no-added-budget constraint from leadership.

## Decision

Use Supabase purely as managed Postgres hosting. Django connects to it as a plain
Postgres instance via `DATABASE_URL` , using Django's own migrations as the source
of truth of schema. Supabase's client SDKs, Auth, and RLS are not used; Django
owns both the schema and authentication (ADR 0002)

## Consequences

* Gets managed Postgres with no ops burden, fitting the budget constraint.
* Supabase's auth, storage, and realtime features remain available to adopt later
(e.g., live status updates) without re-platforming the database.
* Requires discipline across the team not to query tables directly via Supbase's
client SDK, which would bypass Django and create a second source of truth for
data access and auth.
* Local dev Postgres (via Docker, per ADR 0004) must be kept on the same major
version as the Supabase project (17) to avoid version-specific behavior mismatches
between local and production.
