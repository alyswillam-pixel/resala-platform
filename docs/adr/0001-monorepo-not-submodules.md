# 0001 - Use a Monorepo Instead of Git Submodules

 **Date:** 2026-08-15
 **Status:** Accepted

## Context

The tech director requested that frontend and backend code live in a single rep-
ositry. Git submodules were considered as a way to keep frontend and backend
as separate git histories while still appearing under one parent repo, partly
perceived deployment flexibility and partly anticipating furture desktop/mobile
clinets or standalone tools.

## Decision

Use a single monorepo with `frontend/` and `backend/` as plain subfolders (no
modules). Both Vercel and Render/Railway already support deploying from a sub-
directory of a monorepo directly, so no deployment benefit is lost.

## Consequences

* One git history, and so one Pull Request Flow; matches the director's actual 
request
* Avoices submodule footguns: manual `git submodule update`, stale pointer
commits, detached-HEAD confusion for less git-experienced contributors.
* CI needs path filters so backend and frontend test suites don't both run on
every push; however, this is a configuration task not a structural problem.
* If a genuinely independent client (desktop/mobile with its own release cycle)
becomes required, it can be split into its own standalone repo at that point
rather than forced into submodules now.

## Alternatives Considered (optional)

* **Git submodules** — rejected: still, technically speaking, three repos with
a thin wrapper, doesn't satisfy "one repo", and adds sync/tooling friction with
no real deployment upside for the project's current needs.
