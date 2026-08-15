# 0003 - Use Vite (React + TS) for the Frontend

 **Date:** 2026-08-15
 **Status:** Accepted

## Context

Next.js was a possible frontend direction discussed. Before real development
began, a Vite + React starter (with its default demo counter, persisted via a
localStorage) was deployed to production without prior alignment on framework
choice. This is an internal, auth-gated tool with no public SEO/content needs
(for now), which removes Next.js's main structural advantage (SSR/SSG for public-
facing content).

## Decision

Use Vite + React + TypeScript for the frontend, with shadcn/ui (Base UI primiti-
ves, Nova/Lucide-Geist preset) for components, styled with Tailwind CSS. The
frontend in `frontend/` per the monorepo structure (ADR 0001) and deploys to
Vercel.

## Consequences

* Simpler mental model than Next.js (no Server/Client component split, no built-in
SSR caching layer to reason about) for a small team learning as they build.
* Faster local dev server/HMR than Next.js.
* No built-in SSR/SSG, which is acceptable since the app is internal and authenticaed, 
not indexed by search engines.
* API routes / middleware patterns Next.js offered aren't available; any
backend-for-frontend logic belongs in Django instead.
* The previously deployed default Vite starter (demo counter, localStorage) is
discarded and rebuilt properly in `frontend/` .
