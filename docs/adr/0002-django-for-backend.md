# 0002 - Use Django for the Backend

 **Date:** 2026-08-15
 **Status:** Accepted

## Context

The platform is built around role-based approval gates across different roles
in potentially different committees, budget assignment, and event/request work-
flows. The backend needs to serve a JSON API to a separate frontend and own
authentication/authorization logic.

## Decision

Use Django (with Django REST Framework) as the backend, generated via the tech-
nology of `cookiecutter-django` . Django owns authentication directly (via Knox), 
rather than delegating to Supabase Auth.

## Consequences

* Django's auth system (custom User model, groups/permissions) map well onto the
roles/committee-based approval logic, keeping authorization in one place along
the rest of the business logic (Approval Engine, Budget Assignment).
* Avoids duplicating role/permission state between Supabase and Django, and
avoids fragmenting authorization logic into the frontend or Supabase RLS policies.
* Django's admin panel gives a fast internal tool for staff to inspect data with-
out building custom admin UI early on.
* Requires the team to avoid using Supabase's client SDK to query tables directly, 
since that would bypass Django and reintroduce a second source of truth for data
access and auth.
