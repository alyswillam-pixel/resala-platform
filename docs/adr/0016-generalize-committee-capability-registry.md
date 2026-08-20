# 0015 - Generalize Committee Capability Registry

 **Date:** 2026-08-20
 **Status:** Accepted

## Context

ADR-0014 introduced the `TreasuryCommittee` model as a structural registry to 
authorize specific committees for budget review, successfully decoupling 
permissions from fragile free-text role names. Following this implementation, a 
new requirement emerged to restrict event creation to specific, authorized 
committees.

Continuing the ADR-0014 pattern would require creating a new, structurally 
identical database model (e.g., `EventCreatorCommittee` ), alongside its own 
Django admin class and custom permission-checking function. Because the platform
will require additional capability-based routing in the future (such as 
escalating requests), continuing to duplicate this table structure would result
in fragmented permission management, duplicated code, and increased maintenance
overhead. 

## Decision

Deprecate the standalone `TreasuryCommittee` model and replace it with a 
generalized `CommitteeCapability` model in the shared `committees` app. This 
unified registry pairs a `Committee` foreign key with a `Capability` type using
a `TextChoices` field (e.g., `TREASURY` , `EVENT_CREATION` ), enforced across
the platform via a single, reusable permission-checking helper function.

## Consequences

### Positive

* **Zero-Migration Scalability:** Adding a new platform capability in the future
  requires only appending a new string to the `TextChoices` class. It no longer
  requires a database schema migration or a new model definition.
* **Centralized Administration:** Presidential Office leadership can now manage
  all structural committee powers from a single, unified interface in the Django
  admin panel, rather than hunting through different model registries.
* **DRY Codebase:** Eliminates the need for multiple, identical capability-
  checking functions, routing all permission logic through a single, highly
  tested `committee_has_capability()` helper.

### Negative

* **Immediate Rework:** Imposes an immediate refactoring cost. The recently
  built and tested `TreasuryCommittee` model must be deleted, requiring
  destructive database migrations and updates to existing tests and fixtures
  before they ever reach production. 

## Alternatives Considered

* **Creating separate capability models (e.g.,    `EventCreatorCommittee`):** 
  Considered as the faster immediate path to deliver the event creation feature 
  without touching the existing treasury logic. Rejected because deferring the 
  generalization would only compound technical debt, multiplying the eventual
  migration cost once a third capability inevitably emerged.
