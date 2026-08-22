# [Number] - [Short Decision Title]

 **Date:** 2026-08-20
 **Status:** Superseded by [ADR-0017](0017-database-driven-generic-workflow-engine.md)

## Context

ADR-0012 adopted `django-fsm` for Event workflow state management. Running the
test suite surfaced a runtime deprecation warning: the `djang-fsm` project has
been folded into `viewflow` , with the new functionality living in `viewflow.fsm` 
module. The standalone `django-dsm` 2.x API ( `FSMFIELD` , `@transition` defined
directly on model methods) is frozen and will not receive further updates or
bug fixes.

Two PyPI pacages were considered as the source of `viewflow.dsm` , which caused
real confusion during setup:

* `django-fsm` itself, starting at its own version 3.0, but this only shipped
  the deprecated legacy `django_fsm` module and does **not** contain an
  importable `viewflow` namespace at all.
* `django-viewflow`, the actual package that owns the `viewflow` Python namespace.
  This is where `viewflow.fsm` is implemented, verified by directly importing
  it after installation via `import viewflow.fsm` succeeds only when the
`django-viewflow` module is installed.

`django-viewflow` is also the entry point to a much larger workflow framework
(a BPMN process engine, admin scaffolding, form generation), of which the FSM
module is one small, independently useable part.

## Decision

Depend on `django-workflow` (not `django-fsm` ) to obtain `viewflow.fsm` . Move
the Event workflow's transition graph off the `Event` model itself and into a
separate `Eventflow` class ( `events/flows.py` ) that wraps an `Event` instance
with `TextChoices` on the model; the transition graph and per-transition
authorization live entirely in the wrapping class instead.

Only the FSM piece of `django-viewflow` is used. No BPMN engine, admin
scaffolding, or other framework features from the larger `viewflow` package are
adopted at this time.

## Consequences

### Positive

* Stays on the actively maintained implementation rather than the frozen, rather
  deprecated one. This avoids inheriting bugs or gaps that will never be fixed
  upstream in the old `django-fsm` 2.x code.
* `current_state` becomes a plain,  `CharField` with real `choices` which improves
  on `FSMField` , which DRF and Django admin handle less transparently (e.g., 
  serializer field auto-generation now correctly produces a `ChoiceField` ).
* The transition/permission-checking pattern used in the API layer (`can_proceed()`
  then `has_perm(user)` , checked explicitly before invoking a transition) is
  unchanged in scope from the prior `django-fsm` -based implementation, keeping
  the `ViewSet` code close to what it already was.

### Negative

* Loses `FSMField`'s `protected=True` guard: under `django-fsm`, direct
  assignment to `event.current_state` outside a transition method raised an error
  at the framework level. Under `viewflow.fsm` , `current_state` is a plain field
  where nothing stops direct mutation elsewhere in the codebase. This is
`viewflow.fsm` deliberate design (state as plain data, transitions as separate
  pure logic). However, it moves enforcement from the framework to code-review.
* Pulls in `django-viewflow`, a package with a much larger surface than what's
  actually used here. Only the `fsm` submodule is imported; the rest of the
  dependency is unused weight for now.
* The PYPI package name (`django-viewflow`) adn the deprecation warning's own
  wording (referencing `fjango-fsm` version 3.0) point in different, easily
  conflated directions. This caused real setup fritction and is worth flagging
  for any future contributor hitting the same confusion.  

## Alternatives Considered (optional)

* **Stay on `django-fsm` 2.x indefinitely:** rejected — explicitly
  unmaintained per upstream, and the deprecation warning would persist in
  every test run indefinitely with no path to resolution.
* **`django-fsm-2`** (a community-maintained fork continuing the old 2.x
  API rather than migrating to `viewflow.fsm` ): considered as a
  lower-effort path that would have required no code changes at all, but
  rejected in favor of moving to the actively-developed successor rather
  than a fork of an archived project, given the FSM logic here is core
  to the platform's approval workflows and worth keeping on a
  well-supported base.
