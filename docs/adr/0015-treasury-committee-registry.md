# 0015 - Treasury Committee Registry for Budget-Approval Authority

 **Date:** 2026-08-18
 **Status:** Superseded by [ADR-0016](0016-generalize-committee-capability-registry.md)

## Context

The Event/Budget approval workflow (ADR-0012, ADR-0013) requires a way to
determine which users are authorized to review and approve event budgets
at the "Pending Treasurer Review" stage. An initial implementation
determined this by substring-matching the user's `CommitteeRole.name` and
`Committee.name` fields against the words "treasurer"/"treasury".

That approach was fragile and inconsistent with how authorization is
derived everywhere else in the platform (the committee admin hierarchy, 
`is_presidential_office_leader` ) — all of which check structural
relationships (foreign keys, boolean flags) rather than free-text names a
Director could edit at any time. Renaming a role would silently revoke
approval power with no error, and an unrelated committee whose name
happened to contain "treasury" could unintentionally gain it.

## Decision

Introduce a `TreasuryCommittee` model in the `events` app: a registry of
`Committee` rows explicitly designated as holding budget-review authority.
A user is treated as a treasurer for budget-approval purposes if and only
if their `committee_role.committee` has a corresponding `TreasuryCommittee` 
row — checked live, at authorization time, not cached or derived from
role/committee naming.

The registry is managed exclusively through the Django admin, restricted
to Presidential Office leadership (or a true superuser) — the same
scoping pattern already used for `Committee` management. Granting a
committee budget-approval authority is a platform-wide power grant, on
the same level as creating a new committee, and is scoped accordingly
rather than left open to individual committee Directors.

## Consequences

 **Positive:** 
* Authorization no longer depends on how a role or committee happens to
  be named — renaming "Treasurer" to "Finance Lead" has no effect on
  approval authority, since the check is structural.
* Supports more than one committee holding treasury authority
  simultaneously, without any schema change, simply by adding more
`TreasuryCommittee` rows — useful if the approval structure changes
  later (e.g. splitting treasury duties across two committees).
* Changes take effect immediately and reversibly: registering or
  removing a committee from the list immediately grants or revokes
  approval authority for every member of that committee's role, with no
  need to touch individual `User` records.

 **Negative:** 
* Adds one more model and admin registration to maintain, versus a
  single boolean field directly on `Committee` (e.g. `is_treasury` ).
  A `OneToOneField` -based registry model was chosen over a boolean flag
  on `Committee` to keep this concern decoupled from the core committee
  schema, at the cost of an extra join for every `is_treasurer` check.
 * No history is kept of *when* or *why* a committee was added to or
  removed from the registry beyond the `added_at` timestamp on creation —
  a removal leaves no trace at all. If an audit trail of authority
  changes becomes necessary, this would need a transition-log model
  similar to `EventStateTransition` .

## Alternatives Considered

* **Boolean flag on `Committee`** (e.g. `Committee.is_treasury`):
  rejected as the simpler option, in favor of keeping the `events` app's
  authorization concerns out of the shared `Committee` model's schema —
  discussed and consciously traded for the registry model's extra
  indirection.
* **Django `Group`/`Permission` objects:** rejected for the same reasons
  as in ADR-0011 — doesn't naturally express "any current member of
  committee X, " and would still need custom code to resolve group
  membership from `committee_role` , without offering less complexity than
  the registry model.
